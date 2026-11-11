"""Block 05: a second user cannot read the dataset until its owner gives permission.

Run: uv run python 05_permissions.py
"""

import asyncio
import os

os.environ.setdefault("LOG_LEVEL", "CRITICAL")  # keep Cognee's logs quiet

import cognee
import litellm
from cognee import SearchType
from cognee.modules.users.exceptions import PermissionDeniedError
from cognee.modules.users.methods import create_user, get_default_user, get_user, get_user_id_by_email
from cognee.modules.users.permissions.methods import (
    authorized_give_permission_on_datasets,
    authorized_revoke_permission_on_datasets,
)

from workshop import aha, mark, wait_note

litellm.suppress_debug_info = True  # keep the LLM library quiet too

DATASET = "checkout_v2"  # the same name in every block
SECOND_USER = "agent-b@example.com"
QUESTION = "Who owns PAY-104 and when is it due?"


async def ask(user, dataset_id) -> bool:
    """Ask the question as this user. Returns True if Cognee answered."""
    try:
        results = await cognee.recall(
            QUESTION,
            query_type=SearchType.HYBRID_COMPLETION,
            dataset_ids=[dataset_id],
            user=user,
        )
        print(f"  A: {results[0].text if results else '(nothing found)'}")
        return True
    except PermissionDeniedError:
        print("  No access: this user has no read permission on the dataset.")
        return False


async def main() -> None:
    wait_note("permissions", "up to a minute")
    owner = await get_default_user()  # the user who ran blocks 01 to 04
    dataset = next((d for d in await cognee.datasets.list_datasets() if d.name == DATASET), None)
    if dataset is None:
        raise SystemExit("[permissions] There is no data yet. Run step 1 first: uv run python 01_ingest.py")

    # A second user, for a second agent.
    user_id = await get_user_id_by_email(SECOND_USER)  # it exists if you ran this block before
    agent_b = await get_user(user_id) if user_id else await create_user(SECOND_USER, "workshop-pass")
    print(f"[permissions] Owner: {owner.email}   Second user: {agent_b.email}")

    # Start clean, so this block works the same every time you run it.
    await authorized_revoke_permission_on_datasets(agent_b.id, [dataset.id], "read", owner.id)

    print(f"\n[permissions] {agent_b.email} asks before any permission: {QUESTION}")
    answered_before = await ask(agent_b, dataset.id)

    await authorized_give_permission_on_datasets(agent_b.id, [dataset.id], "read", owner.id)
    print(f"\n[permissions] The owner gave {agent_b.email} read permission on {DATASET}")

    print(f"\n[permissions] {agent_b.email} asks again: {QUESTION}")
    answered_after = await ask(agent_b, dataset.id)

    if answered_after and not answered_before:  # say it only when that is what happened
        aha(
            [
                "The same user asked the same question twice. The data did not change.",
                "The first time Cognee refused. The second time it answered.",
                "The only difference is one line: the owner gave that user read permission.",
                "",
                "So a memory is shared only with the users and agents you allow, dataset by dataset.",
            ]
        )
    else:
        print("\n[permissions] This did not go as expected: the user should have no access first, "
              "then get an answer. Run step 1 again, then this step.")
    mark(5)
    print("[permissions] Done. The last step connects two BAND agents to this memory.")
    print("Next: uv run python 06_band.py")


asyncio.run(main())
