"""Forward only authentic, caller-supplied affinity and identification headers."""
import re

from fastapi import HTTPException
from litellm.integrations.custom_logger import CustomLogger


def _session_header(headers):
    # OpenCode's affinity can intentionally be shared by related sessions.
    # An explicitly supplied LiteLLM conversation header is a fallback,
    # not a generated request/trace ID or the child session's own ID.
    for name in ("x-opencode-session", "x-session-affinity", "x-litellm-session-id"):
        if name in headers:
            return headers[name]
    return ""


class OpenCodeGuard(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        model = str(data.get("model", ""))
        if not model.startswith(("go-", "opencode_go/")):
            return data
        request = data.get("proxy_server_request") or {}
        headers = {str(k).lower(): str(v) for k, v in (request.get("headers") or {}).items()}
        agent = headers.get("user-agent", "")
        session = _session_header(headers)
        if not agent.strip() or len(agent) > 512 or not re.fullmatch(r"[ -~]+", agent):
            raise HTTPException(400, "A valid client User-Agent is required")
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,256}", session):
            raise HTTPException(400, "A stable caller session header is required")
        # Do not forward client Authorization, cookies, project metadata, or
        # arbitrary extra_headers. LiteLLM inserts the real upstream API key.
        upstream = {"User-Agent": agent, "x-opencode-session": session}
        client = headers.get("x-opencode-client")
        if client and len(client) <= 128 and re.fullmatch(r"[ -~]+", client):
            upstream["x-opencode-client"] = client
        data["extra_headers"] = upstream
        return data


proxy_handler_instance = OpenCodeGuard()
