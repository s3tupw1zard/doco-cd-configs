# Commit Message Instructions

## General
- Generate commit messages only, do not make git commits.
- Write the message in English.
- Keep it concise and technical.
- Base the message only on the actual diff.

## Format
- Use Conventional Commits.
- Follow this structure: <type>(<scope>): <summary>.
- Keep the subject line short and imperative.
- Prefer one-line commit messages unless extra context is necessary.

## Types
- feat: New Docker service or feature added.
- fix: Bug fix in compose file, image, or service.
- config: Configuration parameter changes (env, volumes, networks, secrets).
- deploy: Deployment strategy changes (scaling, rollouts, replicas, profiles).
- ci: CI/CD pipeline or automation changes.
- docs: Documentation only changes.
- style: Formatting, whitespace, YAML, or linting fixes.
- refactor: Restructured services or config reorganizations.
- perf: Performance tuning of services, images, or containers.
- test: Added or updated test containers, compose overrides, or healthchecks.
- build: Image build changes, build args, multi-stage builds.
- chore: Maintenance, cleanup, or non-functional changes.
- revert: Revert a previous commit.

## Scope
Pick a scope that reflects the Docker area affected:
- compose: General compose file changes.
- service/<name>: A specific service (e.g., service/web, service/db).
- image/<name>: A specific image configuration.
- network, volume, secret, env: Infrastructure components.
- dockerfile: Changes to Dockerfiles.
- stack: Docker Swarm stack changes.
- yaml: General YAML structure changes.
- ci: CI/CD configuration.

## Body
- Add a body only if the change needs explanation.
- Explain why the change was made, not just what changed.
- Use bullet points for multiple items.
- Mention breaking changes explicitly using:
  BREAKING CHANGE: <description of the breaking change and migration path>

## Examples
- feat(service/api): add rate limiting middleware
- fix(compose): resolve dependency startup order for db service
- config(env): update database connection string variables
- deploy(stack): increase replica count for worker service
- ci(gitlab): add build stage for production image
- docs(README): add environment setup instructions
