# LiteLLM deployment and migration

Do not start alongside the existing LiteLLM on port 4000. Back up and migrate its database first; reuse its master key, salt and database password. Do not attach a PostgreSQL 15 data directory to PostgreSQL 16. Verify all model IDs and endpoints against live provider catalogs; this config is a candidate based on the prior design. Verify the guard rejects missing session headers and that actual upstream headers survive streaming/tool requests. Go models are only for personal coding-related traffic; general chat and research use chat-* models. Create separate virtual keys for clients.

Infisical Production /litellm: LITELLM_MASTER_KEY, LITELLM_SALT_KEY, POSTGRES_PASSWORD, OPENCODE_GO_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY. Never commit actual values.

The deployment is now registered in .doco-cd.main-devnode.yaml. Before merging the activation PR, ensure all required Infisical entries exist and the previous installation has been backed up and migrated or stopped. Doco-CD tracks main and will attempt deployment automatically after merge.

## Pocket ID SSO
Native generic OIDC, free for up to five SSO users according to LiteLLM documentation. No OAuth proxy or enterprise license required within that limit.

Create a confidential OIDC client in https://id.s3tupw1zard.ovh with exact redirect URI https://api.s3tupw1zard.dev/sso/callback, PKCE S256, and access restricted to your intended administrator group. Do not enable public client or unrestricted group access.

In Infisical prod /litellm add GENERIC_CLIENT_ID and GENERIC_CLIENT_SECRET from Pocket ID. Run `bash scripts/generate-secrets.sh --infisical litellm --apply --prompt` (without --fresh for migration). Existing values are kept. Endpoint URLs and proxy base URL are configured in Infisical; scopes remain in Compose. The provisioning script creates missing non-secret defaults, but never overwrites existing entries.

Verify discovery from devnode:
```sh
curl -fsS https://id.s3tupw1zard.ovh/.well-known/openid-configuration | jq '{issuer,authorization_endpoint,token_endpoint,userinfo_endpoint,code_challenge_methods_supported}'
```
The expected endpoints are /authorize, /api/oidc/token, /api/oidc/userinfo. Live discovery could not be retrieved during authoring; adjust if INTERNAL_APP_URL or a different configuration changes them.

Before enabling, keep a verified local break-glass admin and test /fallback/login. OIDC sub is the stable user ID; assign admin role explicitly through existing admin access, do not grant all SSO users administrator permissions. Restrict Pocket ID client access. Test browser sign-in, logout, administrator role, and existing virtual-key API requests; no change to API-key auth or model routing is intended. The old standalone instance is not automatically migrated or stopped. Do not merge the activation PR until DB migration and routing are verified.

References: https://docs.litellm.ai/docs/proxy/admin_ui_sso and https://pocket-id.org/docs/setup/connect-an-app

## Local service connectivity and configuration
Required /litellm keys are exactly the entries in .doco-cd.main-devnode.yaml. In addition to existing credentials, UI_PASSWORD is the separate bootstrap UI password (use an existing value when migrating, or generate with --fresh only for new installs). UI_USERNAME defaults to admin via provisioning. Create and verify a named break-glass admin, then disable environment credential login when safe. STORE_MODEL_IN_DB enables Admin UI persistence; do not duplicate static YAML model names in the database. The native OpenCode Go provider selects its upstream endpoint per model; do not set OPENCODE_GO_API_BASE. SearXNG search tool searxng-search uses SEARXNG_API_BASE=https://search.s3tupw1zard.dev via the existing HTTPS reverse proxy. No separate host port or API token is required for this private SearXNG connection. Search is explicit, not an automatic fallback. Verify /v1/search/searxng-search with a restricted virtual key. Crawl4AI is not a native LiteLLM search provider; it retains host loopback and a separate Morphic network; do not add an unused URL or pretend a Firecrawl API key can connect to it.

Existing Infisical values are preserved by provisioning. Set /litellm/SEARXNG_API_BASE to https://search.s3tupw1zard.dev manually if it still points to Docker DNS. Verify DNS, TLS and routing from the LiteLLM container.

## Low-cost direct OpenAI models

Create OPENAI_API_KEY in Infisical prod /litellm before merging this branch; use a restricted OpenAI project API key, not a LiteLLM master key or a ChatGPT subscription token. The existing provisioning script prompts for it; never commit the value. Both chat-gpt-6-luna and chat-gpt-5.6-luna use the native openai provider directly, not OpenRouter or OpenCode Go. GPT-6 Luna defaults to reasoning_effort none for tool calling via Chat Completions (Morphic); GPT-5.6 Luna uses the same low-cost default. Do not interpret this as a hard per-request budget or a restriction on client-supplied parameters. Standard short-context input/cached input/output prices per million tokens as of 2026-11-28: GPT-6 Luna $0.10/$0.01/$0.50; GPT-5.6 Luna $0.20/$0.02/$1.20. Long contexts and higher service tiers may cost more. No expensive fallback models are added. Add these aliases to existing restricted Morphic virtual keys explicitly if desired; do not grant go-* access. Test streaming and tool calling using a restricted key after deployment; account-level model access and the pinned LiteLLM runtime were not tested.

The branch uses LiteLLM's native opencode_go provider with os.environ/OPENCODE_API_KEY. Compose now exposes that environment variable from the existing OPENCODE_GO_API_KEY secret; no new OpenCode secret is needed.

References: https://developers.openai.com/api/docs/models/gpt-6-luna and https://developers.openai.com/api/docs/models/gpt-5.6-luna

## OpenCode Go: session affinity and cache verification

The pinned LiteLLM 1.111.0 native provider resolves the upstream protocol from its model catalog. OPENCODE_GO_API_BASE was removed from Compose, Doco-CD and provisioning; the old Infisical entry can be deleted after deployment (not required). Keep the existing OPENCODE_GO_API_KEY. The guard sends the original User-Agent and x-opencode-session (preferred), x-session-affinity or explicitly provided x-litellm-session-id, mapped to x-opencode-session. It never generates session IDs, forwards client credentials, or uses a request/trace ID. The optional x-opencode-client is copied unchanged if valid. OpenCode 2.3.2 already sends affinity headers, including parent/fork affinity. Other clients must provide a truthful client User-Agent and stable caller session header. Go is for coding-agent traffic only; use separate restricted virtual keys for go-* and chat-* models. Keep forward_client_headers_to_llm_api=false.

All eight configured Go IDs are listed in the OpenCode model catalog on 2026-11-28; context/output limits in tokens: DeepSeek V4.1 Flash 1,000,000/384,000; MiMo V2.6 Flash 1,048,576/131,072; GLM 5.3 Flash and GLM 5.3 1,000,000/131,072; Qwen 3.8 Flash 1,000,000/131,072; Qwen 3.7 Plus 1,000,000/65,536; MiniMax M3 and LongCat 2.0 1,000,000/131,072. All list reasoning and tool calling. These are provider maximums, not recommended client context budgets. Do not hard-code reasoning variants, cache rates or protocol overrides; verify them against the provider catalog and the pinned LiteLLM model info. Account privacy/region settings may restrict available models. Keep model selection unchanged. Disable Go Extra Usage in the OpenCode Console if you want a hard subscription-only limit.

After deployment, run a real OpenChamber coding session using a restricted LiteLLM key and the same go-* model for multiple turns. Keep a stable prompt prefix and affinity; inspect the LiteLLM spend log and OpenCode session usage for cached input/read/write tokens, including streaming/tool calls. Compare with a direct Go session using a comparable prefix. Cache hits depend on model, prefix, upstream routing, TTL and compaction; there is no guarantee on every turn. The OpenCode Console remains authoritative for actual subscription quotas. Test missing and invalid session headers with a local mock or a controlled request (must reject before inference). For model metadata from the deployed image:
```sh
docker exec litellm python -c 'import litellm; from litellm.llms.opencode.common_utils import go_api_base; ids="deepseek-v4.1-flash mimo-v2.6-flash glm-5.3-flash glm-5.3 qwen3.8-flash qwen3.7-plus minimax-m3 longcat-2.0".split(); [(print(m,go_api_base(None,m), {k:v for k,v in litellm.model_cost.get("opencode_go/"+m,{}).items() if k in ("max_input_tokens","max_output_tokens","supports_reasoning","supports_function_calling","supports_prompt_caching","supported_endpoints")})) for m in ids]'
```

## OpenRouter price catalog and spend

LiteLLM 1.111.0 reads the provider-reported usage.cost for OpenRouter (including streaming usage when provided), rather than requiring a static map for actual spend. The public OpenRouter /api/v1/models JSON is additionally read at proxy callback initialization by openrouter_prices.py, with a bounded response and timeout. Only configured OpenRouter models are registered in the normal provider model catalog, preserving other provider rows and native cost reporting; no deployment custom pricing is configured. The rates describe default list pricing and may differ from routed/discounted actual cost. On catalog failure the proxy continues with native LiteLLM data. Refresh occurs on proxy restart, not for each request. No third-party full-map override is used (CloudPrice offers one but could change unrelated provider routing/capability metadata). No new credentials are required. Verify /model/info and a non-streaming and streaming OpenRouter call in the live proxy; compare spend with OpenRouter Activity. A streaming request should request usage; cost may be logged on completion instead of being available in initial response headers. Do not treat an absent cost or zero estimate as proof of a free request.

References:
- https://opencode.ai/docs/console/go
- https://models.opencode.ai/providers/opencode-go/
- https://github.com/anomalyco/opencode/blob/v2.3.2/packages/core/src/session/model-request.ts
- https://github.com/BerriAI/litellm/blob/v1.111.0/litellm/llms/opencode/common_utils.py
- https://docs.litellm.ai/docs/providers/openrouter
- https://openrouter.ai/api/v1/models
- https://cloudprice.net/content/about

## Temporary OpenCode Go reasoning workaround (LiteLLM 1.111.0)

Native OpenCode Go Chat Completions rejects or drops reasoning_effort in 1.111.0 (upstream issue #51871, fixed by PR #52156, listed in 1.112.0rc1). Allow only reasoning_effort in the five configured OpenAI-compatible Go chat deployments: DeepSeek V4.1 Flash, MiMo V2.6 Flash, GLM 5.3 Flash, GLM 5.3 and LongCat 2.0. Keep drop_params=false, no default effort, and no protocol overrides. The caller chooses the effort; upstream support and valid levels remain model-specific. Qwen3.8 Flash, Qwen3.7 Plus and MiniMax M3 use the native Messages transformation and are deliberately unchanged; the upstream fix does not modify that path. The allowance is temporary: remove it after deploying a stable LiteLLM release containing #52156 and validating native reasoning. The Compose config-revision label forces proxy recreation so its bind-mounted configuration is reloaded.

Run the existing offline tests and the new wire smoke test against the installed LiteLLM SDK (dummy API key, loopback mock upstream, no real model calls):

```sh
python3 -m unittest discover -s apps/litellm/tests
docker exec -i -e LITELLM_LOCAL_MODEL_COST_MAP=True -e DO_NOT_TRACK=True -e LITELLM_TELEMETRY=False litellm python - < apps/litellm/tests/smoke_go_reasoning.py
```

Then test OpenChamber with DeepSeek low/high and verify no UnsupportedParamsError. A mock wire test proves forwarding, not that every effort level has distinct effects for each upstream model. For any native Messages model, inspect its actual supported variants rather than forcing an OpenAI wire parameter onto the Messages endpoint. Existing OpenRouter/OpenAI deployments, pricing, session guard, secrets and model aliases stay unchanged.

References: https://github.com/BerriAI/litellm/pull/52156 and https://docs.litellm.ai/release_notes/v1.112.0rc1/v1-112-0-rc-1
