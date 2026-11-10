"""Block 04: give feedback on the session, then let Cognee improve the graph from it.

Run: uv run python 04_feedback_improve.py
"""

import asyncio
import os

os.environ.setdefault("LOG_LEVEL", "ERROR")  # keep Cognee's logs quiet

import cognee
from cognee import SearchType

DATASET = "checkout_v2"  # the same name in every block
SESSION = "workshop_session"  # the session from block 03

NEW_FACT = (
    "Update from Lena Fischer on 2026-11-11: Kestrel Bank moved the 3DS2 deadline. "
    "PAY-104 is now due on 2027-01-15, not 2026-12-10."
)
QUESTION = "When is PAY-104 due?"


async def main() -> None:
    # 1. What is in the session so far?
    entries = await cognee.session.get_session(session_id=SESSION)
    print(f"[feedback] The session holds {len(entries)} question(s):")
    for entry in entries:
        print(f"  - {entry.question[:80]}")
    if not entries:
        raise SystemExit("[feedback] The session is empty. Run block 03 first.")

    # 2. Rate the last answer (1 = bad, 5 = good) and say why.
    last = entries[-1]
    await cognee.session.add_feedback(
        session_id=SESSION,
        qa_id=last.qa_id,
        feedback_text="The date is out of date. The bank moved the deadline.",
        feedback_score=1,
    )
    print("[feedback] Rated the last answer 1 out of 5")

    # 3. Add the new fact to the session. It is not in the graph yet.
    await cognee.remember(NEW_FACT, dataset_name=DATASET, session_id=SESSION, self_improvement=False)
    print(f"[feedback] Added to the session: {NEW_FACT}")

    # 4. improve() moves what the session learned into the graph.
    result = await cognee.improve(DATASET, session_ids=[SESSION])
    print("[improve] Stages:")
    for stage in result.stages:
        print(f"  - {stage.stage}: {stage.status} {stage.reason or ''}")

    # 5. The same question again, in a fresh session.
    results = await cognee.recall(
        QUESTION, query_type=SearchType.HYBRID_COMPLETION, datasets=[DATASET]
    )
    print(f"\n[improve] Q: {QUESTION}")
    print(f"[improve] A: {results[0].text if results else '(nothing found)'}")
    print("\n[improve] To see what changed in the graph, run block 02 again.")
    print("[improve] Next: uv run python 05_permissions.py")


asyncio.run(main())
