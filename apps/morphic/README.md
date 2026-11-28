# Morphic on devnode

Official upstream image, release v1.11.0 (commit e6c36d8bd0da12b9acb7faa95c99d673974ba383). Upstream publishes latest and commit-SHA image tags, not semver tags. The SHA tag matches the reviewed source; verify pull before merging. For updates review upstream releases and update SHA and digest explicitly (Renovate can pin digests; SHA tag update discovery is not guaranteed). No source modifications.

## Prerequisites before merge

- Keep Nginx/NetBird ingress private. Wildcard DNS or explicit records for morphic, api and search must resolve to the correct private host from browsers and containers. Keep TLS verification enabled. Check container-to-host routing and firewall; use split DNS if necessary.
- Create the dedicated shared network on devnode: `docker network inspect morphic-crawler >/dev/null 2>&1 || docker network create --internal morphic-crawler`. Ensure the existing traefik network exists. The crawler has its own default network for Internet egress, is not attached to traefik and has no new published port.
- Verify the Crawl4AI 0.9.6 image, existing read-only filesystem/tmpfs constraints, bearer authentication and outbound destination policy. Block private, link-local and metadata destinations at the host egress firewall; verify redirects and subresources on devnode before allowing user traffic. Do not enable unsafe crawler settings. Morphic hands URLs to the crawler, so the crawler must enforce its own destination policy.
- Create a LiteLLM virtual key explicitly allowed only the intended chat-* aliases for general chat/research (no go-*, wildcard or master key). Check that the key's /v1/models response contains only approved models and those models support tool calling.
- Set existing /litellm/SEARXNG_API_BASE=https://search.s3tupw1zard.dev manually; bootstrap never overwrites existing values.
- Create a confidential Pocket ID client at https://id.s3tupw1zard.ovh, restrict allowed groups, enable authorization-code PKCE (S256). Exact redirect URI: https://morphic.s3tupw1zard.dev/api/auth/callback/pocket-id. Scopes openid profile email. Do not use a public client.
- Provision Infisical /morphic via `bash scripts/generate-secrets.sh --infisical morphic --apply --fresh --prompt` for a new installation. Enter the restricted LiteLLM virtual key, Pocket ID client ID and secret, and intended local bootstrap admin email. The Doco-CD identity needs read access to /morphic and /crawl4ai. CRAWL4AI_API_KEY is mapped directly to existing /crawl4ai/CRAWL4AI_API_TOKEN, not a second secret. Use generated hex DB/cache passwords to avoid URI encoding problems.

## Login

Better Auth uses migrations at image startup and stores accounts in local PostgreSQL. Upstream v1.11.0 requires the first user to register through the credential bootstrap flow, not OIDC. Restrict ingress to your own device while creating this local admin at /auth/sign-up (no SMTP, so the email gate alone does not prove mailbox ownership). Then test Pocket ID with an allowed identity; it may create a separate account, do not assume automatic account linking or admin privileges. Retain a local recovery admin and assign roles explicitly. AUTH_SIGNUP_MODE=open is required for new OIDC users; local password signup is also possible after bootstrap, so enforce NetBird ACLs and Pocket ID group restrictions. Invite mode prevents implicit OIDC account creation. No guest chat, public sharing, SMTP or additional social providers are configured.

## Local services

Morphic uses https://api.s3tupw1zard.dev/v1 and https://search.s3tupw1zard.dev (existing HTTPS routing), and http://crawl4ai:11235 over the dedicated network. The app discovers permitted models through /v1/models. PostgreSQL and Valkey are private to its Compose project. No object storage (uploads disabled), external search/extraction providers, analytics, or payment services are configured. Favicons and update checks disabled. Research/model traffic still reaches the chosen upstream provider through LiteLLM and SearXNG queries configured search engines.

## Verify

Before merge, pull images, create network, provision secrets and verify container DNS/TLS. After deployment check migration logs, health, admin bootstrap, Pocket ID sign-in, permitted models and a tool-calling research query with citations and extraction. Verify missing/invalid crawler tokens are rejected and private destination requests blocked. Confirm the old Scira project is stopped separately (do not delete data volumes or existing /scira secrets). No runtime tests have been run during configuration authoring.

References:
- https://github.com/miurla/morphic/blob/v1.11.0/docs/CONFIGURATION.md
- https://github.com/miurla/morphic/blob/v1.11.0/docs/DOCKER.md
- https://github.com/miurla/morphic/blob/v1.11.0/.github/workflows/docker-build.yml
- https://docs.crawl4ai.com/core/self-hosting/

## Login-first landing page

Traefik redirects GET/HEAD requests to / and /search to /auth/login when the production Better Auth session cookie (__Secure-better-auth.session_token) is absent. Login, signup, OIDC callback, assets and API routes are not redirected. The redirect is temporary and intentionally drops the initial search query. This is a UX rule, not an authorization boundary: cookie presence does not verify authenticity or expiry. Morphic's server-side AUTH_PROVIDER=better-auth and ENABLE_GUEST_CHAT=false remain the actual chat protection; the upstream chat API rejects unauthenticated requests with HTTP 401. An expired or forged cookie may still show the landing page, but cannot authorize a chat. This is not a blanket auth gate for every API (upstream advanced-search does not check sessions), so retain private NetBird ingress. No new auth service, source modifications or secrets.

After deployment verify in a private browser: / and /search redirect to /auth/login, Pocket ID and local login succeed and return to the chat page, logout then reload redirects, and unauthenticated chat requests are rejected. Confirm the actual cookie name and the authenticated home page does not redirect. Upstream may change cookie naming on updates; review this rule when upgrading. If the ingress redirects valid sessions unexpectedly, remove the morphic-login router and middleware labels (the original chat authentication stays enforced).
