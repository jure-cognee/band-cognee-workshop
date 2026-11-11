# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "band-sdk[pydantic_ai]>=6.0.1",
#   "cognee-integration-band @ https://github.com/topoteretes/cognee-integrations/archive/refs/heads/main.zip#subdirectory=integrations/band",
# ]
# ///
"""Block 06: a BAND agent that uses the Cognee memory from blocks 01-05.

06_band.py starts this for you. To start it by hand, 06_server.py must be running in
another terminal, and 06_api_key.py must have run once.
Run agent A:  uv run --env-file .env 06_band_agent.py a
Run agent B:  uv run --env-file .env 06_band_agent.py b   (in a third terminal)

Both agents read and write the same dataset, so they share one memory.
"""

import asyncio
import os
import sys

from band import Agent, configure_logging
from band.adapters import PydanticAIAdapter, PydanticAIAdapterConfig
from cognee_band import CogneeClient, CogneeMemoryAdapter, CogneeSettings, cognee_tools

from workshop import box, new_terminal

configure_logging()

WHICH = sys.argv[1].upper() if len(sys.argv) > 1 else "A"  # "A" or "B"

for name in ["LLM_API_KEY", "COGNEE_API_KEY", f"BAND_AGENT_{WHICH}_ID", f"BAND_AGENT_{WHICH}_API_KEY"]:
    if not os.environ.get(name):
        raise SystemExit(
            f"[band] {name} is missing. Start the agent exactly like this:\n"
            f"    uv run --env-file .env 06_band_agent.py {WHICH.lower()}\n"
            "Or use the guided version, which does all of step 6 in one window:\n"
            "    uv run python 06_band.py"
        )

# The agent uses the same OpenAI key as Cognee (LLM_API_KEY in .env).
os.environ.setdefault("OPENAI_API_KEY", os.environ["LLM_API_KEY"])

WHAT_NEXT = {
    "A": [
        "This window is agent A. LEAVE IT OPEN.",
        "It is ready when a line below says: Agent started: Cognee Agent A",
        "",
        "Window 3 will be agent B.",
    ]
    + new_terminal("uv run --env-file .env 06_band_agent.py b"),
    "B": [
        "This window is agent B. LEAVE IT OPEN.",
        "It is ready when a line below says: Agent started: Cognee Agent B",
        "",
        "Now go to BAND in your browser (https://app.band.ai):",
        "1. Rooms -> New room (+) -> select Cognee Agent A -> Create room.",
        "2. Type @ and pick Cognee Agent A, then ask:",
        "   what are the next steps from the Checkout v2 launch readiness call?",
        "3. In the same room, type @, pick Cognee Agent A, and tell it a new fact:",
        "   new fact for the team: Lena Fischer finished the first draft of the",
        "   Checkout v2 launch announcement today. Omar Haddad has to review it.",
        "4. Click the agent A window (window 2) and press Ctrl+C. Wait one minute.",
        "5. New room -> select Cognee Agent B. Type @, pick Cognee Agent B, ask:",
        "   is the Checkout v2 launch announcement written yet, and who reviews it?",
        "",
        "Agent B was never in the first room, but it knows. That is the shared memory.",
        "At the end: press Ctrl+C in this window and in the server window.",
    ],
}
MODEL = "openai:gpt-5.6-luna"


async def main() -> None:
    # Reads COGNEE_BASE_URL, COGNEE_API_KEY and COGNEE_BAND_DATASET from .env
    settings = CogneeSettings.resolve()
    client = CogneeClient(settings)

    # A normal BAND agent that uses an OpenAI model.
    inner = PydanticAIAdapter(
        PydanticAIAdapterConfig(
            model=MODEL,
            custom_section=(
                "You are a helpful assistant with persistent memory. <cognee_memory> "
                "blocks contain context recalled from past sessions. Treat them as your "
                "own memory. Use cognee_search for explicit lookups and cognee_remember "
                "to store facts worth keeping."
            ),
        ),
        additional_tools=cognee_tools(client),
    )

    agent = Agent.create(
        # This one line gives the agent Cognee memory. Without it: adapter=inner
        adapter=CogneeMemoryAdapter(inner, settings=settings, client=client),
        agent_id=os.environ[f"BAND_AGENT_{WHICH}_ID"],
        api_key=os.environ[f"BAND_AGENT_{WHICH}_API_KEY"],
    )
    print(f"[band] Agent {WHICH} is starting. Dataset: {settings.dataset}")
    stop_file = os.environ.get("BAND_STOP_FILE")  # set by 06_band.py, which then guides you itself
    if not stop_file:
        box(WHAT_NEXT.get(WHICH, [f"This window is agent {WHICH}. Leave it open."]))

    # Run until Ctrl+C, or until 06_band.py asks this agent to stop by creating the stop file.
    # Both end the agent the same way, so it moves its rooms into the graph before it exits.
    run = asyncio.create_task(agent.run())
    try:
        while not run.done():
            if stop_file and os.path.exists(stop_file):
                run.cancel()
                break
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        run.cancel()
    await asyncio.gather(run, return_exceptions=True)
    if not run.cancelled() and run.exception():
        raise run.exception()


asyncio.run(main())
