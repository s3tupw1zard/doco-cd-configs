# doco-cd-configs

## devnode (Unesty)

Active target: `devnode`. Previous targets and retired apps are preserved in `archive/`. Archiving repository files does not stop containers; review existing deployments before switching targets. Never run down -v to migrate.

### Infisical
Create folders in the new Production environment: /searxng, /crawl4ai, /litellm, /scira and /doco-cd. Replace INFISICAL_PROJECT_ID in .doco-cd.devnode.yaml with the actual UUID and verify that the environment slug is prod. Grant the Doco-CD machine identity read access only to the needed folders. Bootstrap Doco-CD manually using apps/doco-cd/compose.devnode.yaml and SECRET_PROVIDER_SITE_URL, SECRET_PROVIDER_CLIENT_ID, SECRET_PROVIDER_CLIENT_SECRET from the new identity. Do not commit the bootstrap environment. Verify container DNS can resolve the Infisical host.

Generate once per new app, in a private terminal, and paste the output into the matching Infisical folder:

    bash scripts/generate-secrets.sh searxng
    bash scripts/generate-secrets.sh crawl4ai

Do not regenerate secrets for existing deployments. The script also offers litellm and scira for future use, but reuse existing LiteLLM keys and database credentials when migrating.

### Network
Host Nginx and NetBird are external. Services bind only to loopback: SearXNG 8002, Crawl4AI 11235. SearXNG JSON is enabled and the limiter is disabled for private use only. Do not expose publicly. Configure NetBird-only Nginx vhosts with TLS if remote access is needed. Crawl4AI requires bearer authentication; never allow crawling private or link-local destinations. Verify outbound restrictions and API authentication before enabling the service. No Docker socket is mounted into crawler.

### Deployment status
Search services are prepared, not runtime-tested. Verify image versions/digests, settings mounts, health and JSON search. The new Infisical UUID is not yet configured. Doco-CD bootstrap requires explicit manual setup. Existing LiteLLM remains external until a data-preserving migration is prepared; its prior configuration stays archived. Scira requires a dedicated source fork for LiteLLM routing, session headers, local search, auth, storage and cloud dependency removal. No unmodified Scira deployment is activated. Garage and pgvector are deferred until Scira integration defines their actual contracts.

### Smoke tests
    curl -fsS 'http://127.0.0.1:8002/search?q=flutter&format=json'
    curl -fsS http://127.0.0.1:11235/health

Verify unauthenticated crawler requests fail and authenticated requests use the intended token. Do not enable public ingress.

Staged replacement manifests for LiteLLM are in apps/litellm/; they are deliberately not in the active target. Scira requirements are in apps/scira/README.md.
