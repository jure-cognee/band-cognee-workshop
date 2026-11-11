"""Block 06: start the Cognee server that the BAND agents talk to.

Run: uv run python 06_server.py
Leave it running. Press Ctrl+C to stop.
"""

import os
import warnings

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet
warnings.simplefilter("ignore")  # and Python's warnings

import uvicorn

from cognee.api.client import app
from cognee.base_config import get_base_config

from workshop import box, new_terminal

# Give Cognee's local default user the usual local password, so block 06_api_key.py can
# sign in. The server only listens on this machine.
config = get_base_config()
config.default_user_password = config.default_user_password or "default_password"

box(
    [
        "This window is now the Cognee server (http://localhost:8000).",
        "LEAVE IT OPEN. Do not type here. Press Ctrl+C only at the very end.",
        "",
        "Window 2 will be agent A.",
    ]
    + new_terminal("uv run python 06_api_key.py")
)
uvicorn.run(app, port=8000, log_level="warning")
