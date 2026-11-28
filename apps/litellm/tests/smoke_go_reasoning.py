"""Run inside the pinned LiteLLM container; local mock upstream, no real inference."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import litellm
import yaml
from litellm.llms.opencode.common_utils import go_endpoint


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.requests.append((self.path, body))
        response = {
            "id": "mock", "object": "chat.completion", "created": 1,
            "model": body["model"],
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "OK"},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
        }
        raw = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *args):
        pass


def main():
    config = yaml.safe_load(Path("/app/config.yaml").read_text())
    entries = [e["litellm_params"] for e in config["model_list"]
               if e["litellm_params"].get("allowed_openai_params") == ["reasoning_effort"]
               and e["litellm_params"]["model"].startswith("opencode_go/")]
    assert len(entries) == 5, "Expected five temporary Go chat allowlists"
    assert config["litellm_settings"]["drop_params"] is False
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.requests = []
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for params in entries:
                model = params["model"]
                assert go_endpoint(model) == "/v1/chat/completions", (model, go_endpoint(model))
                for effort in ("none", "low", "high"):
                    count = len(server.requests)
                    litellm.completion(
                        model=model, api_base=f"http://127.0.0.1:{server.server_port}/v1",
                        api_key="synthetic-test-key", messages=[{"role": "user", "content": "OK"}],
                        reasoning_effort=effort, allowed_openai_params=params["allowed_openai_params"],
                        drop_params=False, max_tokens=32, num_retries=0, timeout=10,
                    )
                    assert len(server.requests) == count + 1
                    path, body = server.requests[-1]
                    assert path.endswith("/chat/completions"), path
                    assert body.get("reasoning_effort") == effort, (model, effort, body.get("reasoning_effort"))
                    print(f"PASS {model}: {effort} forwarded")
        finally:
            server.shutdown()
            thread.join()


if __name__ == "__main__":
    main()
