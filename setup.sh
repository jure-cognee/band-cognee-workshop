#!/usr/bin/env bash
# Step 0 on macOS or Linux, in one command. Run this in the workshop folder:
#
#   bash setup.sh
#
# It installs uv if you don't have it, creates .env, asks for your OpenAI key,
# installs everything, and checks the result. You can run it again at any time.

set -euo pipefail
cd "$(dirname "$0")"

say()  { echo "[setup] $*"; }
fail() { echo "[setup] $*" >&2; exit 1; }

[ -f pyproject.toml ] || fail "Run this from the band-cognee-workshop folder."

# 1. uv
if ! command -v uv >/dev/null 2>&1; then
  say "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv was installed, but this terminal can't see it yet. Open a new terminal and run this script again."
fi
say "uv: $(uv --version)"

# 2. macOS only: Cognee's graph database needs OpenSSL 3
if [ "$(uname)" = "Darwin" ]; then
  if command -v brew >/dev/null 2>&1; then
    brew list openssl@3 >/dev/null 2>&1 || { say "Installing OpenSSL 3..."; brew install openssl@3; }
  else
    echo "[setup] Homebrew not found. If step 1 fails with 'lbug C API', install OpenSSL 3: https://brew.sh then: brew install openssl@3" >&2
  fi
fi

# 3. .env
if [ ! -f .env ]; then
  cp .env.example .env
  say "Created .env"
fi

# 4. OpenAI key. In Codespaces, a secret called LLM_API_KEY is used if you set one.
if grep -q '^LLM_API_KEY=$' .env; then
  key="${LLM_API_KEY:-}"
  if [ -z "$key" ]; then
    [ -t 0 ] || fail "Put your OpenAI key in .env after LLM_API_KEY=, then run this script again."
    read -r -p "[setup] Paste your OpenAI API key (starts with sk-): " key
  fi
  key="$(echo "$key" | tr -d '[:space:]')"
  case "$key" in sk-*) ;; *) fail "That doesn't look like an OpenAI key. Run the script again." ;; esac
  tmp="$(mktemp)"
  sed "s|^LLM_API_KEY=\$|LLM_API_KEY=$key|" .env > "$tmp" && mv "$tmp" .env
  say "Saved your key in .env"
else
  say "LLM_API_KEY is already in .env"
fi

# 5. Node.js 22 (only step 2, the graph UI, needs it)
node_version="$(node --version 2>/dev/null || echo none)"
case "$node_version" in
  v22.*) say "Node.js: $node_version" ;;
  *) echo "[setup] Node.js 22 not found (found: $node_version). Steps 0, 1 and 3 to 6 work without it." >&2
     echo "[setup] For step 2 (the graph UI): nvm install 22 && nvm use 22, or https://nodejs.org/en/download" >&2 ;;
esac

# 6. Install and check
say "Installing Python and Cognee. The first time takes a few minutes..."
uv sync || fail "uv sync failed. Send the error above to the presenter."
uv run python 00_check.py
