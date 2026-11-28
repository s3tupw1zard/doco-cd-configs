# Traefik behind host Nginx
Nginx terminates TLS and restricts ingress to the NetBird address. Traefik only publishes HTTP on 127.0.0.1:8080 and routes opted-in Docker services by Host. No ACME, public dashboard or public ports. Docker API access is filtered through a dedicated socket proxy network; read access still exposes container metadata, so do not attach other services to that network.

Before merging, create or inspect the shared bridge:
```sh
docker network inspect traefik >/dev/null 2>&1 || docker network create traefik
docker network inspect traefik --format '{{(index .IPAM.Config 0).Gateway}}'
```
Store the IPv4 gateway (without /32) in prod /traefik/TRAEFIK_TRUSTED_PROXY_IP. This assumes Linux Docker DNAT from host loopback uses that gateway as the source; verify actual peer IP in logs after startup and adjust if needed. Trust only the actual Nginx peer, not the entire Docker subnet. Do not enable insecure forwarded headers. Nginx must replace client-supplied forwarded headers.

Port 8080 must be free. Install nginx.conf.example on the host after replacing NETBIRD_IP. Validate nginx -t before reload. Keep existing LiteLLM proxy unchanged until migration. Crawl4AI stays isolated on localhost:11235 until authentication and outbound SSRF protections are validated.

Test locally: curl -fsS -H 'Host: search.s3tupw1zard.dev' 'http://127.0.0.1:8080/search?q=flutter&format=json'
Test TLS over NetBird, then verify access fails from outside NetBird. Do not expose the Docker socket proxy. No runtime tests have been performed.
