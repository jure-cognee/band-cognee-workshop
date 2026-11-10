#!/bin/bash
# Run one block and keep its output in runs/. Example: ./run.sh 01
set -o pipefail
cd "$(dirname "$0")"
mkdir -p runs
file=$(ls ${1}_*.py 2>/dev/null | head -1)
[ -z "$file" ] && { echo "No block starts with '$1'"; exit 1; }
uv run python "$file" 2>&1 | tee "runs/$1.log"
code=$?
echo "exit code: $code" >> "runs/$1.log"
exit $code
