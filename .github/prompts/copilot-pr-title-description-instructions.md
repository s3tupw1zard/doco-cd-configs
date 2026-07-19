# Pull Request Generation Instructions

## General
- Be concise and technical.
- Focus on the actual user-facing or infrastructure impact.
- Do not invent facts that are not present in the diff.

## PR Title
- Generate a short, imperative title.
- Use the Conventional Commits format: <type>(<scope>): <summary>.
- Keep it under 72 characters if possible.
- Mention the most important change only.
- Use Docker Compose / doco-cd specific types and scopes (see below).

### Docker Types
- deploy: Deployment or rollout strategy changes (e.g., replicas, profiles, stacks).
- compose: Docker Compose file changes (e.g., services, networks, volumes).
- config: Environment variables, secrets, or configuration changes.
- infra: Infrastructure or cloud resource changes (e.g., AWS, GCP, Azure).
- image: Container image updates, tags, or build arg changes.
- fix: Bug fix in services, networking, or container behavior.
- ci: CI/CD pipeline or automation changes (e.g., GitHub Actions, GitLab CI).
- docs: Documentation changes in README or inline comments.
- refactor: Restructuring services, volumes, or compose files without behavior change.
- perf: Performance improvements (e.g., resource limits, caching layers).
- test: Changes to healthchecks, test containers, or compose overrides.
- chore: Maintenance tasks, cleanup, or version bumps.
- revert: Revert a previous PR or change.

### Scope Examples
- compose: General compose file changes.
- service/<name>: Specific service changes (e.g., service/web, service/db).
- image/<name>: Specific image or Dockerfile changes.
- stack: Docker Swarm stack or deployment changes.
- network, volume, secret, env: Component-level changes.
- ci: CI/CD workflow files.
- docs: Documentation updates.

## PR Description
- Start with a short summary of what changed.
- Then explain why the change was made.
- Include testing notes and relevant caveats.
- Mention breaking changes explicitly if present.
- If helpful, add bullet points for key changes.

### Body Structure
1. Summary: One or two sentences about the change.
2. Why: Explain the motivation or problem being solved.
3. Changes: Use bullet points for specific modifications.
4. Testing: How was this validated (e.g., docker compose up, healthchecks, CI pipeline)?
5. Breaking Changes: If applicable, describe what breaks and the migration path.

### Example
**Title:**
deploy(stack): add rolling update policy to web service

**Description:**
Adds a rolling update configuration to the web service in the production stack to minimize downtime during deployments.

Why:
Previously, updating the web service caused a brief outage due to immediate container recreation.

Changes:
- Added `deploy.update_config` with `delay: 10s` and `failure_action: rollback` to `compose.prod.yml`.
- Set `parallelism: 1` to update one container at a time.
- Added healthcheck endpoint verification before marking the update as successful.

Testing:
- Verified zero-downtime deployment with `docker stack deploy`.
- Confirmed healthcheck passes before old container is stopped.

Breaking Changes:
- None.
