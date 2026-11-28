# Staged LiteLLM migration (not active in devnode target)

Do not start alongside the existing LiteLLM on port 4000. Back up and migrate its database first; reuse its master key, salt and database password. Do not attach a PostgreSQL 15 data directory to PostgreSQL 16. Verify all model IDs and endpoints against live provider catalogs; this config is a candidate based on the prior design. Verify the guard rejects missing session headers and that actual upstream headers survive streaming/tool requests. Go models are only for personal coding-related traffic; general chat and research use chat-* models. Create separate virtual keys for clients.

Infisical Production /litellm: LITELLM_MASTER_KEY, LITELLM_SALT_KEY, POSTGRES_PASSWORD, OPENCODE_GO_API_KEY, OPENROUTER_API_KEY. Never commit actual values.

Append deployment.devnode.yaml.example to .doco-cd.main-devnode.yaml only after validation and migration.

## Pocket ID SSO
Native generic OIDC, free for up to five SSO users according to LiteLLM documentation. No OAuth proxy or enterprise license required within that limit.

Create a confidential OIDC client in https://id.s3tupw1zard.ovh with exact redirect URI https://api.s3tupw1zard.dev/sso/callback, PKCE S256, and access restricted to your intended administrator group. Do not enable public client or unrestricted group access.

In Infisical prod /litellm add GENERIC_CLIENT_ID and GENERIC_CLIENT_SECRET from Pocket ID. Run `bash scripts/generate-secrets.sh --infisical litellm --apply --prompt` (without --fresh for migration). Existing values are kept. Endpoint URLs and scopes are set in compose, not secrets.

Verify discovery from devnode:
```sh
curl -fsS https://id.s3tupw1zard.ovh/.well-known/openid-configuration | jq '{issuer,authorization_endpoint,token_endpoint,userinfo_endpoint,code_challenge_methods_supported}'
```
The expected endpoints are /authorize, /api/oidc/token, /api/oidc/userinfo. Live discovery could not be retrieved during authoring; adjust if INTERNAL_APP_URL or a different configuration changes them.

Before enabling, keep a verified local break-glass admin and test /fallback/login. OIDC sub is the stable user ID; assign admin role explicitly through existing admin access, do not grant all SSO users administrator permissions. Restrict Pocket ID client access. Test browser sign-in, logout, administrator role, and existing virtual-key API requests; no change to API-key auth or model routing is intended. Existing running LiteLLM is not modified by this staged manifest. Do not activate until DB migration and routing are verified.

References: https://docs.litellm.ai/docs/proxy/admin_ui_sso and https://pocket-id.org/docs/setup/connect-an-app
