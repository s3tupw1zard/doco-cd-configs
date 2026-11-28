#!/usr/bin/env python3
"""Create missing production folders and secrets; never update existing values."""
import argparse
import getpass
import json
import os
import secrets
import sys
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

PROJECT = "249698ea-20b9-43f5-9066-95a0af265dac"
SCOPE = {"projectId": PROJECT, "environment": "prod"}
GENERATED = {
    "searxng": {"SEARXNG_SECRET": ""},
    "crawl4ai": {"CRAWL4AI_API_TOKEN": ""},
    "litellm": {"LITELLM_MASTER_KEY": "sk-", "LITELLM_SALT_KEY": "sk-", "POSTGRES_PASSWORD": "", "UI_PASSWORD": ""},
    "scira": {"BETTER_AUTH_SECRET": "", "CRON_SECRET": "", "MCP_CREDENTIALS_ENCRYPTION_KEY": "", "POSTGRES_PASSWORD": "", "REDIS_PASSWORD": ""},
    "doco-cd": {},
    "traefik": {},
}
MANUAL = {
    "traefik": ["TRAEFIK_TRUSTED_PROXY_IP"],
    "doco-cd": ["SECRET_PROVIDER_SITE_URL", "SECRET_PROVIDER_CLIENT_ID", "SECRET_PROVIDER_CLIENT_SECRET"],
    "litellm": ["OPENCODE_GO_API_KEY", "OPENROUTER_API_KEY", "GENERIC_CLIENT_ID", "GENERIC_CLIENT_SECRET"],
    "scira": ["AMADEUS_API_KEY","AMADEUS_API_SECRET","BLOB_READ_WRITE_TOKEN","COINGECKO_API_KEY","DAYTONA_API_KEY","DODO_PAYMENTS_API_KEY","DODO_PAYMENTS_WEBHOOK_SECRET","ELEVENLABS_API_KEY","EXA_API_KEY","FIRECRAWL_API_KEY","GITHUB_CLIENT_ID","GITHUB_CLIENT_SECRET","GOOGLE_CLIENT_ID","GOOGLE_CLIENT_SECRET","GOOGLE_GENERATIVE_AI_API_KEY","GOOGLE_MAPS_API_KEY","GROQ_API_KEY","MICROSOFT_CLIENT_ID","MICROSOFT_CLIENT_SECRET","NEXT_PUBLIC_GOOGLE_MAPS_API_KEY","NEXT_PUBLIC_MAX_SLUG","NEXT_PUBLIC_MAX_TIER","NEXT_PUBLIC_PREMIUM_SLUG","NEXT_PUBLIC_PREMIUM_TIER","NEXT_PUBLIC_STARTER_SLUG","NEXT_PUBLIC_STARTER_TIER","OPENAI_API_KEY","OPENWEATHER_API_KEY","PARALLEL_API_KEY","POLAR_ACCESS_TOKEN","POLAR_WEBHOOK_SECRET","QSTASH_TOKEN","RESEND_API_KEY","SMITHERY_API_KEY","SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET","SUPADATA_API_KEY","SUPERMEMORY_API_KEY","TAVILY_API_KEY","TMDB_API_KEY","TWITTER_CLIENT_ID","TWITTER_CLIENT_SECRET","UPSTASH_REDIS_REST_TOKEN","UPSTASH_REDIS_REST_URL","VALYU_API_KEY","XAI_API_KEY","YT_ENDPOINT"],
}


DEFAULTS = {"litellm": {"GENERIC_AUTHORIZATION_ENDPOINT":"https://id.s3tupw1zard.ovh/authorize","GENERIC_TOKEN_ENDPOINT":"https://id.s3tupw1zard.ovh/api/oidc/token","GENERIC_USERINFO_ENDPOINT":"https://id.s3tupw1zard.ovh/api/oidc/userinfo","PROXY_BASE_URL":"https://api.s3tupw1zard.dev","SEARXNG_API_BASE":"http://searxng:8080","UI_USERNAME":"admin","OPENCODE_GO_API_BASE":"https://opencode.ai/inference/go/openai/v1"}}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app", choices=["all", *GENERATED])
    parser.add_argument("--apply", action="store_true", help="Actually create missing objects")
    parser.add_argument("--fresh", action="store_true", help="Allow new random credentials for staged LiteLLM/Scira; never use for migrations")
    parser.add_argument("--prompt", action="store_true", help="Prompt for missing externally issued or existing credentials (hidden input)")
    args = parser.parse_args()
    origin = os.environ.get("INFISICAL_DOMAIN", "").rstrip("/")
    parsed = urlsplit(origin)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        parser.error("Set INFISICAL_DOMAIN to your trusted HTTPS origin, without /api")
    token = os.environ.get("INFISICAL_TOKEN") or getpass.getpass("Infisical access token: ")
    if not token:
        parser.error("Access token required")
    opener = build_opener(NoRedirect())

    def api(method, path, params=None, body=None):
        url = origin + path + ("?" + urlencode(params) if params else "")
        request = Request(url, method=method, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"}, data=json.dumps(body).encode() if body is not None else None)
        try:
            with opener.open(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f"{method} {path}: HTTP {exc.code}; stopped without printing response") from None
        except (URLError, ValueError, TimeoutError):
            raise RuntimeError(f"{method} {path}: connection or response failure") from None

    apps = list(GENERATED) if args.app == "all" else [args.app]
    folders = {item["name"] for item in api("GET", "/api/v2/folders", {**SCOPE, "path": "/"})["folders"]}
    for app in apps:
        path = "/" + app
        if app not in folders:
            print(f"{'Create' if args.apply else 'Would create'} folder {path}")
            if args.apply:
                api("POST", "/api/v2/folders", body={**SCOPE, "name": app, "path": "/"})
            existing = set()
        else:
            existing = {item["secretKey"] for item in api("GET", "/api/v4/secrets", {**SCOPE, "secretPath": path, "viewSecretValue": "false", "expandSecretReferences": "false"})["secrets"]}
        for key in [*GENERATED[app], *MANUAL.get(app, []), *DEFAULTS.get(app, {})]:
            if key in existing:
                print(f"Keep {path}/{key}")
                continue
            generate = key in GENERATED[app] and (app not in ("litellm", "scira") or args.fresh)
            default = DEFAULTS.get(app, {}).get(key)
            if not args.apply:
                print(f"Would {'set configured default for' if default is not None else 'generate' if generate else 'require input for'} {path}/{key}")
                continue
            if default is not None:
                value = default
            elif generate:
                value = GENERATED[app][key] + secrets.token_hex(32)
            elif args.prompt:
                value = getpass.getpass(f"{path}/{key} (empty skips): ")
            else:
                value = ""
            if not value:
                print(f"Missing manual value: {path}/{key}")
                continue
            api("POST", "/api/v4/secrets/" + key, body={**SCOPE, "secretPath": path, "secretValue": value, "type": "shared"})
            print(f"Created {path}/{key}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, TypeError) as exc:
        print(f"Stopped: {exc if isinstance(exc, RuntimeError) else 'unexpected API response'}", file=sys.stderr)
        sys.exit(1)
