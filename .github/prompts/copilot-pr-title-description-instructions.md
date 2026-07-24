# Pull Request Generation Instructions

## Context

This repository is a collection of Docker Compose stacks deployed via doco-cd.
It is NOT an application or software project. Files present:
- `compose.*.yaml` — Docker Compose stack definitions
- `.doco-cd.*.yaml` — doco-cd deployment configuration files (NOT Compose files)
- `renovate.json` — Renovate bot config for automated container image updates

Do NOT invent a "Why" or business rationale. If the diff does not explain a reason, omit the Why section entirely.

## PR Title

`<type>(<scope>): <short description>`

Types:
- **compose**: Docker Compose stack additions or modifications
- **doco-cd**: doco-cd configuration changes
- **config**: Env/secrets/Renovate config updates
- **image**: Container image version changes
- **fix**: Broken stack or config fixes

Rules:
- Imperative verb (`Add`, `Update`, `Fix`)
- Max 72 characters
- Scope = service name (e.g. `service-x`, `stack`, `host`)

## PR Description

One sentence: what was added/changed. No filler phrases like "to improve functionality" or "to enhance capabilities".

### Changes

Bullet per changed file. Be specific and literal — only what is visible in the diff:
- `compose.service-x.yaml`: add stack definition
- `.doco-cd.main-vm-01.yaml`: add service-x to doco-cd deployment config, including external secrets when needed. If the filename differs from the one in the example, use the actual filename instead of blindly using the one from the example.
- `renovate.json`: add image update rules for new service

### Breaking Changes

Only if an existing running service is affected.
If none: `None`

## Example

**Title:** `compose(service-x): add new stack`

**Description:** Adds Docker Compose stack and doco-cd deployment config for a new service.

### Changes
- `compose.service-x.yaml`: add stack definition
- `.doco-cd.main-vm-01.yaml`: add service-x to doco-cd deployment config, including external secrets when needed
- `renovate.json`: add image update rules for new service

### Breaking Changes
None