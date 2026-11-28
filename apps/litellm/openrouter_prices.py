"""Best-effort OpenRouter list-price catalog; provider-reported spend remains authoritative."""
import json
import logging
import math
from pathlib import Path
from urllib.request import HTTPRedirectHandler, Request, build_opener

import litellm
import yaml
from litellm.integrations.custom_logger import CustomLogger

CATALOG_URL = "https://openrouter.ai/api/v1/models"
MAX_BYTES = 16 * 1024 * 1024
CONFIG = Path("/app/config.yaml")
log = logging.getLogger(__name__)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_catalog():
    # Public, fixed HTTPS endpoint. No API key, prompts, or user headers.
    request = Request(CATALOG_URL, headers={"Accept": "application/json"})
    with build_opener(NoRedirect()).open(request, timeout=5) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("OpenRouter catalog too large")
    return json.loads(raw)


def configured_models(config):
    return {
        model.removeprefix("openrouter/")
        for entry in config.get("model_list", [])
        if isinstance(model := entry.get("litellm_params", {}).get("model"), str)
        and model.startswith("openrouter/")
    }


def price(value):
    if isinstance(value, bool):
        raise ValueError("invalid price")
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError("invalid price")
    return result


def catalog_rows(document, wanted, existing):
    result = {}
    for item in document["data"]:
        if not isinstance(item, dict) or item.get("id") not in wanted:
            continue
        key = "openrouter/" + item["id"]
        try:
            pricing = item["pricing"]
            row = dict(existing.get(key, {}))
            row.update(
                litellm_provider="openrouter",
                mode="chat",
                input_cost_per_token=price(pricing["prompt"]),
                output_cost_per_token=price(pricing["completion"]),
            )
            for source, target in (
                ("input_cache_read", "cache_read_input_token_cost"),
                ("input_cache_write", "cache_creation_input_token_cost"),
            ):
                if pricing.get(source) is not None:
                    row[target] = price(pricing[source])
            context = item.get("context_length")
            if type(context) is int and context > 0:
                row["max_input_tokens"] = context
            output = (item.get("top_provider") or {}).get("max_completion_tokens")
            if type(output) is int and output > 0:
                row["max_output_tokens"] = output
            params = item.get("supported_parameters")
            if isinstance(params, list):
                row["supports_function_calling"] = "tools" in params
                row["supports_reasoning"] = any(p in params for p in ("reasoning", "include_reasoning"))
            result[key] = row
        except (KeyError, TypeError, ValueError, OverflowError, AttributeError):
            log.warning("Skipping invalid OpenRouter catalog entry for configured model")
    return result


def refresh_prices():
    try:
        with CONFIG.open(encoding="utf-8") as source:
            wanted = configured_models(yaml.safe_load(source))
        if not wanted:
            return
        rows = catalog_rows(fetch_catalog(), wanted, litellm.model_cost)
        if rows:
            # Register canonical provider catalog rows, NOT deployment
            # model_info/custom_pricing overrides. Native usage.cost wins.
            litellm.register_model(rows)
        log.info("OpenRouter list prices loaded: %d/%d configured models", len(rows), len(wanted))
        if len(rows) != len(wanted):
            log.warning("OpenRouter catalog incomplete; missing models use native LiteLLM defaults")
    except Exception:
        # This is display/fallback pricing only; do not stop the proxy or
        # expose credentials or response content on catalog failure.
        log.warning("OpenRouter list price refresh unavailable; using native LiteLLM catalog")


class OpenRouterPriceCatalog(CustomLogger):
    def __init__(self):
        super().__init__()
        refresh_prices()


proxy_handler_instance = OpenRouterPriceCatalog()
