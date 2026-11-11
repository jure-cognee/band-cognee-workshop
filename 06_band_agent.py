# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "band-sdk[pydantic_ai]>=6.0.1",
#   "cognee-integration-band @ https://github.com/topoteretes/cognee-integrations/archive/refs/heads/main.zip#subdirectory=integrations/band",
# ]
# ///
"""Block 06, step 2: a BAND agent that uses the Cognee memory from blocks 01-05.

06_server.py must be running in another terminal.
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

configure_logging()

WHICH = sys.argv[1].upper() if len(sys.argv) > 1 else "A"  # "A" or "B"

# The agent uses the same OpenAI key as Cognee (LLM_API_KEY in .env).
os.environ.setdefault("OPENAI_API_KEY", os.environ["LLM_API_KEY"])
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
    await agent.run()


asyncio.run(main())
