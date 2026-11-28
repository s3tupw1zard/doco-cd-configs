# Scira — unmodified upstream deployment candidate

Source: https://github.com/zaidmukaddam/scira/tree/e1692f5bdec7ec3f6482a24e0c6cf9b483d810f9. No fork or application patches. The local Dockerfile packages the exact upstream commit, uses its bun.lock, and builds Next.js at container startup with runtime secrets (not image build arguments). This avoids upstream Dockerfile's COPY .env and missing standalone output configuration. Runtime builds can still write sensitive server-side artifacts; keep container access restricted. Build and runtime are not tested.

## Deployment
Compose includes dedicated PostgreSQL 17 and Valkey 9, internal database networking and Traefik routing at https://scira.s3tupw1zard.dev. No published app/database ports. Use hex-generated DB/cache passwords to avoid URI escaping issues. Keep ingress private over NetBird. Scira is registered in .doco-cd.main-devnode.yaml by request. Merging this PR will enable automatic deployment attempts; resolve all blockers and populate required values first.

## Blockers
- Upstream env/server.ts and env/client.ts require real provider credentials, including Upstash REST, and lib/auth.ts initializes Polar/Dodo billing. Local Valkey is not a drop-in Upstash REST API. No fake API keys or validation bypass.
- Upstream migration journal lists 0010–0015, but corresponding SQL files were absent from the inspected tree. Resolve with upstream or validate a supported schema bootstrap on a disposable DB; do not blindly use schema push on production. No automatic migration is run.
- Native Pocket ID, arbitrary LiteLLM model routing, SearXNG and Crawl4AI adapters are not supported by this upstream revision. Pocket ID can protect ingress with a separately configured OAuth2 Proxy but cannot create a Scira account session. Use a supported native login with real OAuth credentials; no OAuth2 Proxy configured here.
- Do not route general Scira requests to OpenCode Go subscription. No Go key is configured. Other optional provider integrations are not enabled.
- Verify all remaining build/runtime environment variables, billing behavior, API calls, DB setup, and privacy before activation.

## Secrets
Production /scira: run `bash scripts/generate-secrets.sh --infisical scira --apply --fresh --prompt` only for a new installation. Skip unavailable externally issued credentials; required values must be present before deployment. Public NEXT_PUBLIC variables are not confidential and may be embedded in the browser bundle; never use secret keys there. See .doco-cd.main-devnode.yaml for exact mappings. Existing values are not overwritten.

Before merging, resolve blockers and verify build, migration, login and Traefik routing. A new upstream commit must be reviewed explicitly; Renovate can track image tags in Compose but does not automatically update the pinned source commit.
