"""Small helpers the step files share: the messages that tell you what to do next."""

import platform
from pathlib import Path

FOLDER = Path(__file__).parent.resolve()


def wait_note(tag: str, how_long: str = "about a minute") -> None:
    """Say that the step is working, so nobody thinks it is stuck."""
    print(f"[{tag}] Working. This takes {how_long}. Nothing to do until you see a line that starts with 'Next:'.\n")


def box(lines: list[str]) -> None:
    """Print a few lines inside a frame, so they stand out from the logs."""
    width = max(len(line) for line in lines)
    print()
    print("+" + "-" * (width + 2) + "+")
    for line in lines:
        print("| " + line.ljust(width) + " |")
    print("+" + "-" * (width + 2) + "+")
    print()


def new_terminal(command: str) -> list[str]:
    """The lines for 'open another terminal and run this there'."""
    opener = (
        "Open a NEW PowerShell window (Windows key, type powershell, Enter)."
        if platform.system() == "Windows"
        else "Open a NEW terminal window."
    )
    return [opener, "Paste these two lines there:", f'    cd "{FOLDER}"', f"    {command}"]
