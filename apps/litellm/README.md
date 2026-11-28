# Staged LiteLLM migration (not active in devnode target)

Do not start alongside the existing LiteLLM on port 4000. Back up and migrate its database first; reuse its master key, salt and database password. Do not attach a PostgreSQL 15 data directory to PostgreSQL 16. Verify all model IDs and endpoints against live provider catalogs; this config is a candidate based on the prior design. Verify the guard rejects missing session headers and that actual upstream headers survive streaming/tool requests. Go models are only for personal coding-related traffic; general chat and research use chat-* models. Create separate virtual keys for clients.

Infisical Production /litellm: LITELLM_MASTER_KEY, LITELLM_SALT_KEY, POSTGRES_PASSWORD, OPENCODE_GO_API_KEY, OPENROUTER_API_KEY. Never commit actual values.

Add the deployment to .doco-cd.devnode.yaml only after validation and migration.
