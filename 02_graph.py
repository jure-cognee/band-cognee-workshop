"""Block 02: look at the graph in the Cognee UI.

Run: uv run python 02_graph.py
Then open http://localhost:3000, click "Sign in", click "Graph", pick the dataset
"checkout_v2" and click "Records".
Press Ctrl+C to stop before you run the next block.

Needs Node.js 22. If you don't have it, this block downloads it into the folder .node/
(for this workshop only). The first run also downloads the UI, so it takes a little longer.
"""

import asyncio
import os
import warnings
from pathlib import Path

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet
warnings.simplefilter("ignore")  # and Python's warnings

import cognee

from workshop import box


def wait_for_ui(url: str = "http://localhost:3000", seconds: int = 240) -> None:
    """Return when the UI answers, or after a few minutes if it never does."""
    import time
    import urllib.error
    import urllib.request

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never through a proxy
    end = time.time() + seconds
    while time.time() < end:
        try:
            opener.open(url, timeout=5)
            return
        except urllib.error.HTTPError:
            return  # the server answered, even if with an error page
        except OSError:
            time.sleep(2)


def use_node_22() -> None:
    # Cognee 1.6.6 starts the UI with the newest Node.js it finds in nvm, and installs
    # the newest Node.js if "node" is not on your PATH. The UI fails on Node 27
    # ("Internal Server Error"). So: put a Node 22 on the PATH (node22.py downloads one
    # into .node/ if you don't have it), and keep Cognee out of nvm.
    from cognee.api.v1.ui import ui

    from node22 import ensure_node_22

    print(f"[graph] Using Node.js {ensure_node_22()}")
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

    # 3. Wait until the UI really answers, so the link works when you click it.
    print("[graph] Starting the UI. The first time takes a minute or two. Wait for the box below...")
    await asyncio.to_thread(wait_for_ui)

    box(
        [
            "The graph is ready.",
            "",
            "1. Open http://localhost:3000 in your browser.",
            "2. Click Sign in (the login is already filled in).",
            "3. Click Graph on the left, pick the dataset checkout_v2, click Records.",
            "4. Look for: Omar Haddad -> Payments -> PAY-104 -> the Kestrel Bank deadline.",
            "",
            "Lines that start with [frontend] below are normal. Ignore them.",
            "",
            "WHEN YOU ARE DONE: click this terminal window and press Ctrl+C.",
            "This step does not end by itself. You must stop it before step 3.",
        ]
    )
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


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
print("\n[graph] Stopped.")
print("Next: uv run python 03_agent_session.py")
