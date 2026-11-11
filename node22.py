"""Make sure Node.js 22 is available for step 2 (the graph UI). Nothing to install by hand.

If "node" on your PATH is already version 22, that one is used. If not, this downloads
Node.js 22 into the folder .node/ inside the workshop folder (about 30 MB, one time) and
uses it for this workshop only. It does not change the Node.js on your computer.

The setup script runs it for you. To run it yourself: uv run python node22.py
"""

import os
import platform
import shutil
import ssl
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = "v22.12.0"
BASE_URL = os.environ.get("NODE22_BASE_URL", f"https://nodejs.org/dist/{VERSION}")
HOME = Path(__file__).parent / ".node"


def _version(node: str | None) -> str:
    if not node:
        return "none"
    try:
        return subprocess.run([node, "--version"], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "none"


def _archive_name() -> str:
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    system = platform.system()
    if system == "Windows":
        return f"node-{VERSION}-win-{arch}.zip"
    if system == "Darwin":
        return f"node-{VERSION}-darwin-{arch}.tar.gz"
    return f"node-{VERSION}-linux-{arch}.tar.gz"


def _bin_dir() -> Path:
    """The folder that holds node and npm inside .node/."""
    folder = HOME / _archive_name().removesuffix(".zip").removesuffix(".tar.gz")
    return folder if platform.system() == "Windows" else folder / "bin"


def _local_node() -> str | None:
    name = "node.exe" if platform.system() == "Windows" else "node"
    path = _bin_dir() / name
    return str(path) if path.exists() else None


def _download() -> None:
    name = _archive_name()
    url = f"{BASE_URL}/{name}"
    HOME.mkdir(exist_ok=True)
    archive = HOME / name
    print("[node] Downloading Node.js 22 for this workshop (one time, about 30 MB)...")
    try:
        import certifi

        context = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        context = ssl.create_default_context()
    with urllib.request.urlopen(url, context=context, timeout=120) as response, open(archive, "wb") as out:
        shutil.copyfileobj(response, out)
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            z.extractall(HOME)
    else:
        with tarfile.open(archive) as t:
            t.extractall(HOME)
    archive.unlink()


def ensure_node_22() -> str:
    """Put a Node.js 22 first on PATH for this process. Returns its version, or exits."""
    version = _version(shutil.which("node"))
    if version.startswith("v22."):
        return version

    if not _local_node():
        try:
            _download()
        except Exception as error:  # no network, proxy, disk full...
            raise SystemExit(
                f"[node] Could not download Node.js 22: {error}\n"
                "[node] Install it by hand from https://nodejs.org/en/download (pick v22), "
                "open a new terminal, and run this again."
            )

    os.environ["PATH"] = str(_bin_dir()) + os.pathsep + os.environ.get("PATH", "")
    version = _version(_local_node())
    if not version.startswith("v22."):
        raise SystemExit(
            "[node] Node.js 22 was downloaded but does not start. Delete the folder .node "
            "and run this again, or install Node.js 22 from https://nodejs.org/en/download"
        )
    return version


if __name__ == "__main__":
    print(f"[node] Node.js {ensure_node_22()} is ready for step 2.")
    sys.exit(0)
