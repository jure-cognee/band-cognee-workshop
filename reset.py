"""Start over: delete Cognee's local databases. Works on Windows, macOS and Linux.

Run: uv run python reset.py
Then run step 1 again: uv run python 01_ingest.py

Use it when a step fails with "no such table", "lbug C API" or another database error.
"""

import importlib.util
import shutil
from pathlib import Path

# Find the installed cognee package without importing it, so this works even when
# importing cognee fails.
spec = importlib.util.find_spec("cognee")
if spec is None or spec.origin is None:
    raise SystemExit("[reset] Cognee is not installed. Run the setup script first.")

cognee_dir = Path(spec.origin).parent
removed = 0
for name in [".cognee_system", ".data_storage", ".cognee_cache"]:
    for folder in [cognee_dir / name, Path(__file__).parent / name]:
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
            print(f"[reset] Deleted {folder}")
            removed += 1

print("[reset] Nothing to delete." if removed == 0 else "[reset] Done.")
print("[reset] Next: uv run python 01_ingest.py")
