"""Block 00: check the setup. Run: uv run python 00_check.py"""

import os
import sys

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet

import cognee  # importing cognee also loads the .env file in this folder

print(f"[check] Python {sys.version.split()[0]}")
print(f"[check] Cognee {cognee.__version__}")

if os.environ.get("LLM_API_KEY"):
    print("[check] LLM_API_KEY is set")
    print("[check] OK: ready. Next: uv run python 01_ingest.py")
else:
    print("[check] MISSING: LLM_API_KEY. Copy .env.example to .env and add your OpenAI key.")
    sys.exit(1)
