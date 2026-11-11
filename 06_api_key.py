"""Block 06: get an API key for the local Cognee server.

06_server.py must be running in another terminal.
Run: uv run python 06_api_key.py
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

from workshop import box

SERVER = "http://localhost:8000"

# 1. Sign in as Cognee's local default user.
login = urllib.request.Request(
    f"{SERVER}/api/v1/auth/login",
    data=urllib.parse.urlencode(
        {"username": "default_user@example.com", "password": "default_password"}
    ).encode(),
)
try:
    token = json.load(urllib.request.urlopen(login))["access_token"]
except OSError:
    raise SystemExit(
        "[api-key] The Cognee server is not running. In another terminal window, in this folder, run:\n"
        "    uv run python 06_server.py\n"
        "Leave it open, then run this again."
    )

# 2. Ask the server for an API key.
request = urllib.request.Request(
    f"{SERVER}/api/v1/auth/api-keys",
    data=json.dumps({"name": "band"}).encode(),
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)
key = json.load(urllib.request.urlopen(request))["key"]

# 3. Save it in .env, where the BAND agents read it.
env = Path(__file__).parent / ".env"
lines = [line for line in env.read_text(encoding="utf-8").splitlines() if not line.startswith("COGNEE_API_KEY=")]
env.write_text("\n".join(lines + [f"COGNEE_API_KEY={key}"]) + "\n", encoding="utf-8")
print("[api-key] Saved COGNEE_API_KEY in .env")
box(["Now start agent A in this same window:", "    uv run --env-file .env 06_band_agent.py a"])
print("Next: uv run --env-file .env 06_band_agent.py a")
