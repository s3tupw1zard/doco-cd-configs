#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--infisical" ]]; then
  shift
  exec python3 "$(dirname "$0")/bootstrap-infisical.py" "$@"
fi
case "${1:-}" in
  searxng) printf 'SEARXNG_SECRET=%s\n' "$(openssl rand -hex 32)" ;;
  crawl4ai) printf 'CRAWL4AI_API_TOKEN=%s\n' "$(openssl rand -hex 32)" ;;
  litellm) printf 'LITELLM_MASTER_KEY=sk-%s\nLITELLM_SALT_KEY=sk-%s\nPOSTGRES_PASSWORD=%s\n' "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" ;;
  scira) printf 'BETTER_AUTH_SECRET=%s\nCRON_SECRET=%s\nMCP_CREDENTIALS_ENCRYPTION_KEY=%s\nPOSTGRES_PASSWORD=%s\nREDIS_PASSWORD=%s\n' "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" ;;
  *) echo "Usage: $0 {searxng|crawl4ai|litellm|scira}" >&2; exit 2 ;;
esac
