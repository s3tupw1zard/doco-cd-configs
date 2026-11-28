# Scira — local-only deployment, application blocked upstream

The existing Compose manifest is the only deployment definition, registered in .doco-cd.main-devnode.yaml. No fork, source patches, additional Doco-CD target, object storage, billing, specialized API services, or social-login credentials are added.

## Current state
PostgreSQL and Valkey can be deployed with local credentials. Scira itself is deliberately disabled via the upstream-blocked Compose profile and scale: 0, has no Traefik route or shared ingress network, and is not usable yet. Do not enable the profile or increase the scale until a compatible upstream version or explicitly approved source adaptation exists. The existing Dockerfile pins and packages unmodified upstream source; it is not a working local-only build.

The intended integration is LiteLLM (general chat/research only through allowed chat-* models), SearXNG, authenticated Crawl4AI, PostgreSQL, and Valkey. The pinned upstream revision does not expose configuration for arbitrary LiteLLM routing, SearXNG or Crawl4AI adapters, or generic Pocket ID OIDC. It hardcodes providers and requires external credentials at build and runtime, including cloud Redis REST and billing; its migration journal also references absent SQL files. Removing environment entries does not remove these dependencies from the application code. No placeholder API keys, fake endpoint mappings, auth bypass, or unsupported environment switches are supplied. No external API calls are introduced.

## Infisical
Production /scira retains only BETTER_AUTH_SECRET, CRON_SECRET, MCP_CREDENTIALS_ENCRYPTION_KEY, POSTGRES_PASSWORD and REDIS_PASSWORD. These are local values, not social-login or external provider credentials. For a genuinely new installation use `bash scripts/generate-secrets.sh --infisical scira --apply --fresh`; preserve existing credentials for migrations. The first three values are reserved for the disabled Scira service. No existing Infisical values are deleted by this change.

## Operations
After merging, check existing containers with `docker compose -p scira -f apps/scira/compose.scira.yaml --profile upstream-blocked ps -a` using the required local environment. If a previous Scira container exists, stop it explicitly using the actual project name and service; do not delete volumes. Doco-CD profile reconciliation is not runtime-tested. Confirm database/cache health; do not expose Scira until authentication, migrations, local integrations and egress behavior are verified.

Upstream reference: https://github.com/zaidmukaddam/scira/tree/e1692f5bdec7ec3f6482a24e0c6cf9b483d810f9
