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

from workshop import aha, mark, wait_note

DATASET = "checkout_v2"  # the same name in every block
SESSION = "workshop_session"  # the same name in block 04

QUESTIONS = [
    "List the next steps agreed in the call 'Checkout v2 launch readiness'. "
    "For each one give the owner, the owner's team, the due date and the Linear issue. "
    "If the issue has no due date, use a deadline from an email about that step.",
    "When is PAY-104 due, and who set that date?",
]


async def main() -> None:
    wait_note("agent", "up to a minute")
    for question in QUESTIONS:
        results = await cognee.recall(
            question,
            query_type=SearchType.HYBRID_COMPLETION,
            datasets=[DATASET],
            session_id=SESSION,  # Cognee keeps this question and answer in the session
        )
        print(f"\n[agent] Q: {question}")
        print(f"[agent] A: {results[0].text if results else '(nothing found)'}")

    # How many questions and answers does the session hold now?
    try:
        count = len(await cognee.session.get_session(session_id=SESSION))
    except Exception:
        count = len(QUESTIONS)

    aha(
        [
            "1. The call never names a team, an issue id or a date. The answer has all three.",
            "Cognee joined the call, the Linear issues and the bank's email through the graph.",
            "",
            f"2. These {count} questions and answers are now a SESSION called '{SESSION}'.",
            "A session is the agent's short-term memory. It lives next to the graph, not in it: "
            "the graph has not changed yet.",
            "",
            "Step 4 takes what the session learned and puts it into the graph.",
        ]
    )
    mark(3)
    print("Next: uv run python 04_feedback_improve.py")


asyncio.run(main())
