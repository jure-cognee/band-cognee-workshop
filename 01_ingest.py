"""Block 01: give Cognee the team's data and let it build a knowledge graph.

Run: uv run python 01_ingest.py
"""

import asyncio
import os
from pathlib import Path

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet

import cognee
from cognee.modules.engine.operations.setup import setup

DATASET = "checkout_v2"  # the same name in every block
DATA = Path(__file__).parent / "data"

# This prompt tells the LLM what to pull out of the text when it builds the graph.
# Change it and run this block again to get a different graph.
EXTRACTION_PROMPT = """You build a knowledge graph of a software team's work.
From the text, extract:
- people, and the team each person belongs to
- calls, and who attended them
- issues, with their id exactly as written (for example PAY-104), their assignee and team
- every action a person agreed to take, and who owns it
- deadlines, with the date exactly as written, and who set them
Connect them with short, clear relationship names such as owns, member_of, tracked_by,
agreed_in, due_on. Use only what the text says."""


async def main() -> None:
    print("[ingest] The extraction prompt Cognee will use:\n")
    print(EXTRACTION_PROMPT)
    print()

    # Start from an empty dataset, so running this block twice gives the same result.
    await setup()
    existing = {dataset.name for dataset in await cognee.datasets.list_datasets()}
    if DATASET in existing:
        await cognee.forget(dataset=DATASET)
        print(f"[ingest] Forgot the old dataset {DATASET}")

    # One remember() call per source. remember() stores the text and builds the graph.
    for source in ["calls", "linear", "email"]:
        texts = [path.read_text() for path in sorted((DATA / source).glob("*.txt"))]
        await cognee.remember(
            texts,
            dataset_name=DATASET,
            node_set=[source],  # a label, so we can tell the sources apart later
            custom_prompt=EXTRACTION_PROMPT,
            self_improvement=False,  # we do this step by hand in block 04
        )
        print(f"[ingest] Remembered {len(texts)} file(s) from data/{source}/")

    print("[ingest] Done. Next: uv run python 02_graph.py")


asyncio.run(main())
