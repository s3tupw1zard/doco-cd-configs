# Scira integration — blocked on source fork

Do not deploy the unmodified upstream image with fake credentials. The source has hardcoded model providers and mandatory cloud dependencies. Required fork work:
- LiteLLM compatible provider, dynamic allowed model list, default chat-* model.
- Stable chat ID as x-opencode-session and truthful Scira user-agent for every go-* request; preserve selected provider for all internal tasks, with no automatic fallback to go-* for general use.
- SearXNG JSON and authenticated Crawl4AI adapters. Restrict crawler outbound access to public destinations.
- Local authentication, PostgreSQL, Valkey; remove billing and required unused cloud services.
- Runtime-only secrets, build without secrets, database migrations, smoke tests.
- Optional local object storage (Garage) and pgvector after actual interface design.

Planned Infisical Production /scira: BETTER_AUTH_SECRET, CRON_SECRET, MCP_CREDENTIALS_ENCRYPTION_KEY, POSTGRES_PASSWORD, REDIS_PASSWORD, LITELLM_API_KEY (virtual key), CRAWL4AI_API_TOKEN (import/reference from /crawl4ai). Never use the LiteLLM master key.

Planned origin https://scira.s3tupw1zard.dev, host loopback port 3001. No active deployment until a tested fork exists.
