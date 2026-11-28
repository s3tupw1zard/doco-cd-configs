"""Staged guard; integration-test request metadata and upstream headers before use."""
import re

from fastapi import HTTPException
from litellm.integrations.custom_logger import CustomLogger


class OpenCodeGuard(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if not str(data.get("model", "")).startswith("go-"):
            return data
        request = data.get("proxy_server_request") or {}
        headers = {str(k).lower(): str(v) for k, v in (request.get("headers") or {}).items()}
        agent = headers.get("user-agent", "").strip()
        session = headers.get("x-opencode-session", "").strip()
        if not agent or len(agent) > 512 or not re.fullmatch(r"[ -~]+", agent):
            raise HTTPException(400, "A valid client User-Agent is required")
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,256}", session):
            raise HTTPException(400, "A stable x-opencode-session is required")
        data["extra_headers"] = {"User-Agent": agent, "x-opencode-session": session}
        return data


proxy_handler_instance = OpenCodeGuard()
