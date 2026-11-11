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

from workshop import wait_note

litellm.suppress_debug_info = True  # keep the LLM library quiet too

DATASET = "checkout_v2"  # the same name in every block
SECOND_USER = "agent-b@example.com"
QUESTION = "Who owns PAY-104 and when is it due?"


async def ask(user, dataset_id) -> None:
    try:
        results = await cognee.recall(
            QUESTION,
            query_type=SearchType.HYBRID_COMPLETION,
            dataset_ids=[dataset_id],
            user=user,
        )
        print(f"  A: {results[0].text if results else '(nothing found)'}")
    except PermissionDeniedError:
        print("  No access: this user has no read permission on the dataset.")


async def main() -> None:
    wait_note("permissions", "up to a minute")
    owner = await get_default_user()  # the user who ran blocks 01 to 04
    dataset = next(d for d in await cognee.datasets.list_datasets() if d.name == DATASET)

    # A second user, for a second agent.
    user_id = await get_user_id_by_email(SECOND_USER)  # it exists if you ran this block before
    agent_b = await get_user(user_id) if user_id else await create_user(SECOND_USER, "workshop-pass")
    print(f"[permissions] Owner: {owner.email}   Second user: {agent_b.email}")

    # Start clean, so this block works the same every time you run it.
    await authorized_revoke_permission_on_datasets(agent_b.id, [dataset.id], "read", owner.id)

    print(f"\n[permissions] {agent_b.email} asks before any permission: {QUESTION}")
    await ask(agent_b, dataset.id)

    await authorized_give_permission_on_datasets(agent_b.id, [dataset.id], "read", owner.id)
    print(f"\n[permissions] The owner gave {agent_b.email} read permission on {DATASET}")

    print(f"\n[permissions] {agent_b.email} asks again: {QUESTION}")
    await ask(agent_b, dataset.id)

    print("\n[permissions] Done. The last step connects two BAND agents to this memory.")
    print("Next: uv run python 06_band.py")


asyncio.run(main())
