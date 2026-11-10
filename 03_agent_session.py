"""Block 03: an agent asks the memory questions. The questions and answers form a session.

Run: uv run python 03_agent_session.py
"""

import asyncio
import os

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet

import cognee
import litellm
from cognee import SearchType

litellm.suppress_debug_info = True  # keep the LLM library quiet too

DATASET = "checkout_v2"  # the same name in every block
SESSION = "workshop_session"  # the same name in block 04

QUESTIONS = [
    "List the next steps agreed in the call 'Checkout v2 launch readiness'. "
    "For each one give the owner, the owner's team, the due date and the Linear issue. "
    "If the issue has no due date, use a deadline from an email about that step.",
    "When is PAY-104 due, and who set that date?",
]


async def main() -> None:
    for question in QUESTIONS:
        results = await cognee.recall(
            question,
            query_type=SearchType.HYBRID_COMPLETION,
            datasets=[DATASET],
            session_id=SESSION,  # Cognee keeps this question and answer in the session
        )
        print(f"\n[agent] Q: {question}")
        print(f"[agent] A: {results[0].text if results else '(nothing found)'}")

    print("\n[agent] The call itself never names a team, a date or an issue id.")
    print("[agent] Next: uv run python 04_feedback_improve.py")


asyncio.run(main())
