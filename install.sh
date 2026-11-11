#!/usr/bin/env bash
# The whole of step 0 on macOS or Linux, in one line. Paste this into a terminal:
#
#   curl -LsSf https://raw.githubusercontent.com/jure-cognee/band-cognee-workshop/main/install.sh | bash
#
# It gets the workshop into a folder called band-cognee-workshop (inside the folder you are
# in now) and runs the setup. Running it again is safe: it updates and re-checks.

set -euo pipefail

repo="https://github.com/jure-cognee/band-cognee-workshop"
say() { echo "[install] $*"; }

# Where the workshop goes. If you are already inside it, stay there.
if [ -f 00_check.py ] && [ -f pyproject.toml ]; then
  folder="$PWD"
else
  folder="$PWD/band-cognee-workshop"
fi

had_uv=yes
command -v uv >/dev/null 2>&1 || had_uv=no

# 1. Get or update the code with git, when git is there.
if command -v git >/dev/null 2>&1 && [ -d "$folder/.git" ]; then
  say "Updating $folder"
  git -C "$folder" pull --ff-only || true
elif command -v git >/dev/null 2>&1 && [ ! -e "$folder" ]; then
  say "Downloading the workshop into $folder"
  git clone "$repo.git" "$folder"
fi

# 2. No git, or the update did not bring the new files: take the files as an archive.
#    This never touches your .env.
if [ ! -f "$folder/setup.sh" ] || [ ! -f "$folder/node22.py" ]; then
  say "Downloading the workshop files"
  tmp="$(mktemp -d)"
  curl -LsSf "$repo/archive/refs/heads/main.tar.gz" | tar -xz -C "$tmp"
  mkdir -p "$folder"
  cp -R "$tmp/band-cognee-workshop-main/." "$folder/"
  rm -rf "$tmp"
fi

# 3. Run the setup.
if bash "$folder/setup.sh"; then
  echo
  say "Done. Now run these lines:"
  [ "$folder" = "$PWD" ] || echo "    cd band-cognee-workshop"
  [ "$had_uv" = yes ] || echo "    source \"\$HOME/.local/bin/env\""
  echo "    uv run python 01_ingest.py"
else
  say "The setup did not finish. Read the message above, fix it, and paste the same line again."
  exit 1
fi
