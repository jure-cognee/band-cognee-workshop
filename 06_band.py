"""Block 06: two BAND agents share the Cognee memory. One terminal, and it guides you.

Run: uv run python 06_band.py

It asks for your two BAND agents (you paste, no file to edit), starts the Cognee server
and both agents in the background, and tells you what to do in BAND, one step at a time.
The background programs write their output to the folder runs/.

To run the three programs by hand instead, see "Step 6 by hand" in the README.
"""

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from workshop import box, mark

HERE = Path(__file__).parent.resolve()
ENV = HERE / ".env"
RUNS = HERE / "runs"
BAND_NAMES = ["BAND_AGENT_A_ID", "BAND_AGENT_A_API_KEY", "BAND_AGENT_B_ID", "BAND_AGENT_B_API_KEY"]
SERVER = "http://localhost:8000"

# What you paste into BAND. Each one is a single line, so it is easy to copy.
QUESTION_A = "what are the next steps from the Checkout v2 launch readiness call? Give owner, team, due date and Linear issue for each."
NEW_FACT = "new fact for the team: Lena Fischer finished the first draft of the Checkout v2 launch announcement today. It is waiting for review by Omar Haddad."
QUESTION_B = "is the Checkout v2 launch announcement written yet, and who has to review it?"

children: dict[str, subprocess.Popen] = {}


# ---------- .env ----------

def read_env() -> dict[str, str]:
    values = {}
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            name, value = line.split("=", 1)
            values[name.strip()] = value.strip()
    return values


def save(name: str, value: str) -> None:
    lines = ENV.read_text(encoding="utf-8").splitlines()
    if any(line.startswith(f"{name}=") for line in lines):
        lines = [f"{name}={value}" if line.startswith(f"{name}=") else line for line in lines]
    else:
        lines.append(f"{name}={value}")
    ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ask(label: str) -> str:
    while True:
        value = input(f"  Paste the {label} and press Enter: ").strip().strip('"').strip("'")
        if value:
            return value
        print("  Nothing was pasted. Try again.")


def band_agents() -> None:
    """Part 1: make sure the IDs and keys of two BAND agents are in .env."""
    values = read_env()
    if all(values.get(name) for name in BAND_NAMES):
        answer = input("[band] Your two BAND agents are already saved. Use them? (Y/n): ").strip().lower()
        if answer != "n":
            return

    box(
        [
            "PART 1 of 3: make two agents in BAND. You make them yourself, in your browser.",
            "",
            "First: open https://app.band.ai and sign in (or click Create account).",
            "",
            "Then do this twice, once for agent A and once for agent B:",
            "1. Click Agents in the left menu.",
            "2. Click Connect remote agent (top right).",
            "3. Fill in the name and the description (copy them from below).",
            "   Leave everything else as it is.",
            "4. Click Connect Agent. BAND now shows an ID and an API Key.",
            "5. Copy the ID, come back to this window, paste it, press Enter.",
            "6. Copy the API Key, come back, paste it, press Enter.",
            "   The API key is shown only once. If you lose it: open the agent's",
            "   menu in BAND and choose Regenerate API key.",
            "",
            "Start with agent A now. This window is waiting for its ID.",
        ]
    )
    print("    AGENT A   name:         Cognee Agent A")
    print("              description:  Workshop agent A. Answers questions about the Checkout v2 project from shared Cognee memory.")
    print()
    print("    AGENT B   name:         Cognee Agent B")
    print("              description:  Workshop agent B. Answers questions about the Checkout v2 project from shared Cognee memory.")
    print()
    for letter in ["A", "B"]:
        print(f"[band] Cognee Agent {letter}")
        save(f"BAND_AGENT_{letter}_ID", ask(f"ID of Cognee Agent {letter}"))
        save(f"BAND_AGENT_{letter}_API_KEY", ask(f"API Key of Cognee Agent {letter}"))
        print(f"[band] Saved Cognee Agent {letter}.\n")


# ---------- background programs ----------

def start(name: str, command: list[str], extra_env: dict[str, str] | None = None) -> Path:
    RUNS.mkdir(exist_ok=True)
    log = RUNS / f"06_{name}.log"
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", **(extra_env or {})}
    children[name] = subprocess.Popen(
        command, cwd=HERE, env=env, stdout=open(log, "w", encoding="utf-8"), stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
    )
    return log


def tail(log: Path, lines: int = 15) -> str:
    try:
        return "\n".join(log.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])
    except OSError:
        return "(no output)"


def fail(message: str, log: Path | None = None) -> None:
    print(f"\n[band] {message}")
    if log:
        print(f"[band] The last lines of {log.relative_to(HERE)}:\n")
        print(tail(log))
    raise SystemExit(1)


def wait_until(name: str, log: Path, ready, seconds: int, what: str) -> None:
    """Wait until ready() is true. Show dots, so nobody thinks it is stuck."""
    print(f"[band] {what}", end="", flush=True)
    end = time.time() + seconds
    while time.time() < end:
        if children[name].poll() is not None:
            print()
            fail(f"{name} stopped by itself.", log)
        if ready():
            print(" ready.")
            return
        print(".", end="", flush=True)
        time.sleep(2)
    print()
    fail(f"{name} was not ready after {seconds} seconds.", log)


def wait_for_optional(name: str, ready, seconds: int, what: str) -> bool:
    """Like wait_until, but if it fails the step goes on without this program."""
    print(f"[band] {what}", end="", flush=True)
    end = time.time() + seconds
    while time.time() < end and children[name].poll() is None:
        if ready():
            print(" ready.")
            return True
        print(".", end="", flush=True)
        time.sleep(2)
    print(" not available. Going on without it.")
    return False


def server_answers() -> bool:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never through a proxy
    try:
        opener.open(SERVER, timeout=3)
        return True
    except urllib.error.HTTPError:
        return True  # it answered, even if with an error page
    except OSError:
        return False


def stop_agent(name: str, stop_file: Path) -> None:
    """Ask an agent to stop the clean way, so it moves its rooms into the graph first."""
    process = children.get(name)
    if not process or process.poll() is not None:
        return
    stop_file.write_text("stop", encoding="utf-8")
    try:
        process.wait(timeout=90)
    except subprocess.TimeoutExpired:
        process.terminate()


def stop_everything() -> None:
    # The graph UI first, the clean way, so it does not leave a program on port 3000.
    ui = children.get("graph_ui")
    if ui and ui.poll() is None:
        (RUNS / "stop_ui").write_text("stop", encoding="utf-8")
        try:
            ui.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass
    for name, process in children.items():
        if process.poll() is None:
            process.terminate()
    for process in children.values():
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
    for letter in "ab":
        (RUNS / f"stop_agent_{letter}").unlink(missing_ok=True)
    (RUNS / "stop_ui").unlink(missing_ok=True)


def countdown(seconds: int, what: str) -> None:
    """A progress bar, so the wait looks alive."""
    width, spinner, start = 30, "|/-\\", time.time()
    tick = 0
    while True:
        passed = time.time() - start
        if passed >= seconds:
            break
        filled = int(width * passed / seconds)
        bar = "#" * filled + "." * (width - filled)
        left = int(seconds - passed) + 1
        print(f"\r[band] {what} [{bar}] {spinner[tick % 4]} {left:>2}s ", end="", flush=True)
        tick += 1
        time.sleep(0.2)
    print(f"\r[band] {what} [{'#' * width}] done.   ")


def copy_this(text: str) -> None:
    """A line to copy into BAND, on its own, so it is easy to select."""
    print("    COPY THIS INTO BAND (after you typed @ and picked the agent):")
    print()
    print(f"    {text}")
    print()


# ---------- the step ----------

def main() -> None:
    if not ENV.exists():
        raise SystemExit("[band] There is no .env file yet. Do step 0 first (see the README).")
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("[band] uv was not found. Open a new terminal and do step 0 again (see the README).")

    band_agents()

    box(["PART 2 of 3: starting the Cognee server and your two agents.", "Nothing to do. Wait for PART 3."])

    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 8000)) == 0:
            fail(
                "Something is already running on port 8000. If step 2 (the graph) is still open in "
                "another window, stop it there with Ctrl+C. Then run this again."
            )

    log = start("server", [sys.executable, "06_server.py"])
    wait_until("server", log, server_answers, 180, "Starting the Cognee server")

    key = subprocess.run([sys.executable, "06_api_key.py"], cwd=HERE, capture_output=True, text=True)
    if key.returncode != 0:
        fail("Could not get a key for the Cognee server:\n" + (key.stdout + key.stderr)[-800:])

    for letter in "ab":
        stop_file = RUNS / f"stop_agent_{letter}"
        stop_file.unlink(missing_ok=True)
        log = start(
            f"agent_{letter}",
            [uv, "run", "--env-file", ".env", "06_band_agent.py", letter],
            {"BAND_STOP_FILE": str(stop_file)},
        )
        wait_until(
            f"agent_{letter}",
            log,
            lambda log=log: "Agent started" in log.read_text(encoding="utf-8", errors="replace"),
            420,
            f"Starting agent {letter.upper()} (the first time it installs a few things)",
        )

    # The graph UI, so you can look at the memory between the BAND steps. If it does not
    # start, the step goes on without it.
    ui_stop = RUNS / "stop_ui"
    ui_stop.unlink(missing_ok=True)
    ui_log = start("graph_ui", [sys.executable, "02_graph.py"], {"GRAPH_UI_STOP_FILE": str(ui_stop)})
    has_ui = wait_for_optional(
        "graph_ui", lambda: "[graph] UI ready" in ui_log.read_text(encoding="utf-8", errors="replace"), 240,
        "Starting the graph view",
    )

    box(
        [
            "PART 3 of 3: both agents are online. Now go to BAND (https://app.band.ai).",
            "",
            "A. Open a room with agent A:",
            "   1. Click Agents in the left menu.",
            "   2. Click Cognee Agent A.",
            "   3. Click Create room.",
            "",
            "B. Ask agent A a question:",
            "   1. Click the message box. Type @ and pick Cognee Agent A.",
            "      (An agent only answers messages that mention it with @.)",
            "   2. Paste the question below and press Enter.",
        ]
    )
    copy_this(QUESTION_A)
    print("    Agent A answers from the memory you built in steps 1 to 5.\n")
    input("[band] Press Enter here when agent A has answered... ")

    box(
        [
            "C. Tell agent A something new, in the same room:",
            "   1. Type @ and pick Cognee Agent A again.",
            "   2. Paste the new fact below and press Enter.",
            "   3. Wait until agent A confirms it (it says something like Noted).",
        ]
    )
    copy_this(NEW_FACT)
    input("[band] Press Enter here when agent A has confirmed the new fact... ")

    print("\n[band] Switching agent A off. When an agent stops, its room moves into the shared memory.")
    stop_agent("agent_a", RUNS / "stop_agent_a")
    countdown(60, "Cognee is building the graph")

    if has_ui:
        box(
            [
                "LOOK AT THE GRAPH. The BAND room is now inside Cognee.",
                "",
                "You typed one sentence into a chat room in BAND. Agent A stopped,",
                "and Cognee turned that room into graph memory. See it yourself:",
                "",
                "1. Open http://localhost:3000 in your browser.",
                "2. Click Sign in (the login is already filled in).",
                "3. Click Graph on the left and pick the dataset checkout_v2.",
                "   (The page title says Mindmap. That is Cognee's name for the graph.)",
                "4. Type Lena in the search box and pick lena fischer.",
                "   Follow her lines to the launch announcement and to Omar Haddad.",
                "",
                "   On the left, under SOURCES, user sessions now also holds the BAND room.",
                "",
                "Nobody added that to the graph by hand. It came from the BAND room.",
            ]
        )
        input("[band] Press Enter here when you have seen it... ")

    box(
        [
            "Agent A is now OFF. Go back to BAND.",
            "",
            "D. Open a NEW room, this time with agent B:",
            "   1. Click Agents in the left menu.",
            "   2. Click Cognee Agent B.",
            "   3. Click Create room.",
            "",
            "E. Ask agent B about the fact you gave to agent A:",
            "   1. Type @ and pick Cognee Agent B.",
            "   2. Paste the question below and press Enter.",
        ]
    )
    copy_this(QUESTION_B)
    box(
        [
            "WHAT TO NOTICE",
            "",
            "Agent B was never in the first room, and agent A is switched off.",
            "Agent B still knows, because both agents use the same Cognee memory.",
            "Without Cognee, a BAND agent forgets everything when its room ends.",
            "",
            "If agent B does not know yet, wait a minute and ask again.",
        ]
    )
    input("[band] Press Enter here when you are done, to switch everything off... ")


try:
    main()
    print("[band] Stopping agent B and the Cognee server...")
    stop_agent("agent_b", RUNS / "stop_agent_b")
    mark(6)
    box(
        [
            "All done. Two agents shared one memory, and everything is switched off now.",
            "",
            "To look at the graph again at any time:",
            "    uv run python 02_graph.py",
        ]
    )
except KeyboardInterrupt:
    print("\n[band] Stopped.")
finally:
    stop_everything()
