"""Offline regression tests: no paid requests and no external catalog calls."""
import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Test the local guard and catalog logic independently from the runtime.
class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

class CustomLogger:
    pass

fastapi = types.ModuleType("fastapi")
fastapi.HTTPException = HTTPException
litellm = types.ModuleType("litellm")
litellm.model_cost = {}
litellm.register_model = lambda rows: litellm.model_cost.update(rows)
integrations = types.ModuleType("litellm.integrations")
logger = types.ModuleType("litellm.integrations.custom_logger")
logger.CustomLogger = CustomLogger
yaml = types.ModuleType("yaml")
yaml.safe_load = lambda stream: {}
with patch.dict(sys.modules, {
    "fastapi": fastapi, "litellm": litellm,
    "litellm.integrations": integrations,
    "litellm.integrations.custom_logger": logger, "yaml": yaml,
}):
    import opencode_guard as guard
    with patch.object(Path, "open", side_effect=FileNotFoundError):
        import openrouter_prices as prices


class GuardTests(unittest.TestCase):
    def request(self, headers, model="go-deepseek-v4.1-flash"):
        data = {"model": model, "proxy_server_request": {"headers": headers},
                "extra_headers": {"Authorization": "client-secret", "Cookie": "secret"}}
        return asyncio.run(guard.proxy_handler_instance.async_pre_call_hook(None, None, data, "completion"))

    def test_preference_and_allowlist(self):
        data = self.request({"User-Agent": "opencode/2.3.2", "X-OpenCode-Session": "parent_123",
                             "x-session-affinity": "other", "x-litellm-session-id": "another",
                             "x-opencode-client": "openchamber", "Authorization": "client-secret"})
        self.assertEqual(data["extra_headers"], {
            "User-Agent": "opencode/2.3.2", "x-opencode-session": "parent_123",
            "x-opencode-client": "openchamber"})

    def test_explicit_fallbacks(self):
        for name in ("x-session-affinity", "x-litellm-session-id"):
            with self.subTest(name=name):
                data = self.request({"user-agent": "coding-agent/1.0", name: "stable-session"})
                self.assertEqual(data["extra_headers"]["x-opencode-session"], "stable-session")

    def test_missing_invalid_and_trace_ids(self):
        for headers in (
            {"user-agent": "opencode/2.3.2"},
            {"user-agent": "opencode/2.3.2", "x-litellm-trace-id": "trace-only"},
            {"user-agent": "opencode/2.3.2", "x-opencode-session": "invalid\nheader",
             "x-litellm-session-id": "valid-fallback"},
            {"x-opencode-session": "valid-session"},
        ):
            with self.subTest(headers=headers), self.assertRaises(HTTPException) as error:
                self.request(headers)
            self.assertEqual(error.exception.status_code, 400)

    def test_native_prefix(self):
        with self.assertRaises(HTTPException):
            self.request({"user-agent": "opencode/2.3.2"}, "opencode_go/glm-5.3")

    def test_non_go_untouched(self):
        data = self.request({}, "chat-gpt-6-luna")
        self.assertEqual(data["extra_headers"], {"Authorization": "client-secret", "Cookie": "secret"})


class PricingTests(unittest.TestCase):
    def test_only_configured_openrouter_models(self):
        config = {"model_list": [
            {"litellm_params": {"model": "openrouter/example/model"}},
            {"litellm_params": {"model": "opencode_go/example"}},
            {"litellm_params": {"model": "openai/gpt-6-luna"}},
        ]}
        self.assertEqual(prices.configured_models(config), {"example/model"})

    def test_public_price_mapping_and_scope(self):
        row = {"id": "example/model",
               "pricing": {"prompt": "0.000001", "completion": "0.000002",
                           "input_cache_read": "0.0000001", "input_cache_write": "0.0000012"},
               "context_length": 100000,
               "top_provider": {"max_completion_tokens": 10000},
               "supported_parameters": ["tools", "reasoning"]}
        existing = {"openrouter/example/model": {"supports_vision": True},
                    "opencode_go/example": {"supported_endpoints": ["/v1/messages"]}}
        result = prices.catalog_rows({"data": [row, {**row, "id": "other/model"}]},
                                    {"example/model"}, existing)
        self.assertEqual(set(result), {"openrouter/example/model"})
        value = result["openrouter/example/model"]
        self.assertEqual(value["input_cost_per_token"], 0.000001)
        self.assertEqual(value["cache_read_input_token_cost"], 0.0000001)
        self.assertEqual(value["cache_creation_input_token_cost"], 0.0000012)
        self.assertEqual(value["max_input_tokens"], 100000)
        self.assertTrue(value["supports_vision"])
        self.assertTrue(value["supports_function_calling"])
        self.assertTrue(value["supports_reasoning"])
        self.assertNotIn("custom_pricing", value)
        self.assertNotIn("input_cost_per_token", existing["openrouter/example/model"])

    def test_invalid_prices_skipped(self):
        for invalid in ("nan", "inf", "-1", True, None):
            row = {"id": "example/model", "pricing": {"prompt": invalid, "completion": "0"}}
            with self.subTest(invalid=invalid):
                self.assertEqual(prices.catalog_rows({"data": [row]}, {"example/model"}, {}), {})

    def test_zero_is_valid(self):
        self.assertEqual(prices.price("0"), 0.0)

    def test_catalog_failure_does_not_stop_startup(self):
        with patch.object(prices, "fetch_catalog", side_effect=TimeoutError), \
             patch.object(prices, "configured_models", return_value={"example/model"}), \
             patch.object(Path, "open", unittest.mock.mock_open(read_data="{}")):
            prices.refresh_prices()


if __name__ == "__main__":
    unittest.main()
