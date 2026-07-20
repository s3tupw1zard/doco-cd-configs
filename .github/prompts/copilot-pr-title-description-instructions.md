# Pull Request Generation Instructions

## General

- Be concise and technical.
- Focus on the actual infrastructure impact.
- Base entirely on commit history/diff - no inventions.
- If the filename begins with `.doco-cd.` then it is not a docker compose configuration file but a doco-cd configuration file.

## PR Title

`<type>(<scope>): <infra-impact>`

Types:

- **deploy**: Rollout/replica changes
- **compose**: Docker Compose modifications
- **doco-cd**: Doco-CD configuration modifications
- **config**: Env/secrets/params updates
- **infra**: Cloud resource modifications
- **image**: Container image adjustments
- **fix**: Service-level bug resolutions

Scope Examples: `compose`, `service/web`, `network`, `stack`, `ci`

Rules:

- Imperative verb first (`Add`, `Upgrade`, `Fix`)
- Max 72 characters
- Scope in parentheses for service-specific changes

## PR Description

### First Line: Summary

"Adjusts \[WHAT\] to achieve \[OPERATIONAL GOAL\]"

### Why Section (1-2 sentences)

- Problem context: "Resolves intermittent DNS lookup failures during..."
- Business rationale: "Avoids 5xx errors during peak traffic"

### Changes (Bullet Point Heavy!)

### **Do:**

- compose/prod.yml: increase web replicas from 2 → 4
- volume/web-data: change mount type to tmpfs
- secrets/db-password: rotate to v2
- service/redis: add healthcheck endpoint

### **Avoid:**

- "Updated config files"
- "Fixed bugs"
- Generic "Improved performance"

### Breaking Changes (If Any)

BREAKING CHANGE:

- \[service-name\]: Migrate volumes before redeploy  
→ `docker volume migrate --old=legacy --new=nvme`

### Formatting

Use three hashtag characters followed by a space in front of Title, Description, Why, Changes and Breaking Changes so that it is displayed as header 3.

## Example

**Title**

deploy(service/api): scale gunicorn workers

**Description**

Increases Gunicorn worker count for API service to handle peak traffic loads.

**Why**

Performance metrics showed worker saturation leading to 503 errors during daily traffic spikes.

**Changes**

- compose/prod.yml: `gunicorn_workers: 8` → `12`
- service/api: memory limit 512MB → 768MB
- image/api: upgrade base image to python:3.11-slim

**Breaking Changes**

None

