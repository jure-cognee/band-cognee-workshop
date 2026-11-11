"""Block 02: look at the graph in the Cognee UI.

Run: uv run python 02_graph.py
Then open http://localhost:3000, click "Sign in", click "Graph", pick the dataset
"checkout_v2" and click "Records".
Press Ctrl+C to stop before you run the next block.

Needs Node.js 22 on your PATH. The first run downloads the UI, so it takes a little longer.
"""

import asyncio
import os
import shutil
import subprocess
import warnings
from pathlib import Path

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet
warnings.simplefilter("ignore")  # and Python's warnings

import cognee


def use_node_22() -> None:
    # Cognee 1.6.6 starts the UI with the newest Node.js it finds in nvm, and installs
    # the newest Node.js if "node" is not on your PATH. The UI fails on Node 27
    # ("Internal Server Error"). So: need Node 22 on the PATH, and keep Cognee out of nvm.
    from cognee.api.v1.ui import ui

    node = shutil.which("node")
    version = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip() if node else "none"
    if not version.startswith("v22."):
        raise SystemExit(
            f"[graph] This block needs Node.js 22 on your PATH (found: {version}).\n"
            "[graph] Install it from https://nodejs.org/en/download (pick v22), or with nvm: nvm install 22, then nvm use 22.\n"
            "[graph] Open a new terminal, then run this block again."
        )
    ui.get_nvm_sh_path = lambda: Path("no-nvm")  # Cognee now runs the "npm" from your PATH


async def main() -> None:
    import uvicorn

    use_node_22()

    from cognee.api.client import app
    from cognee.api.v1.ui.ui import remove_ui_container, stop_ui_pid
    from cognee.base_config import get_base_config

    # The UI signs in as Cognee's local default user. Give that user the usual local
    # password. The server only listens on this machine.
    config = get_base_config()
    config.default_user_password = config.default_user_password or "default_password"

    # 1. Cognee's API server, on port 8000.
    server = uvicorn.Server(uvicorn.Config(app, port=8000, log_level="warning"))
    api = asyncio.create_task(server.serve())
    while not server.started:
        if api.done():
            return await api  # shows the startup error, for example a port in use
        await asyncio.sleep(0.2)

    # 2. The UI, on port 3000.
    started: list = []
    ui = await asyncio.to_thread(cognee.start_ui, started.append, auto_download=True)
    if ui is None:
        server.should_exit = True
        await api
        raise SystemExit("[graph] The UI did not start. See the message above.")

    print("[graph] Open http://localhost:3000 and click Sign in (the login is already filled in).")
    print("[graph] Click Graph on the left, pick the dataset checkout_v2, then click Records.")
    print("[graph] Look for: Omar Haddad -> Payments -> PAY-104 -> the Kestrel Bank deadline.")
    print("[graph] Press Ctrl+C to stop, then run: uv run python 03_agent_session.py")
    try:
        await api  # runs until Ctrl+C
    except asyncio.CancelledError:
        pass
    finally:
        for item in started:
            pid, container = item if isinstance(item, tuple) else (item, None)
            if container:
                remove_ui_container(container)
            stop_ui_pid(pid)


asyncio.run(main())
