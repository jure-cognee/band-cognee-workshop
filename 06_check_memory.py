# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "cognee-integration-band @ git+https://github.com/topoteretes/cognee-integrations#subdirectory=integrations/band",
# ]
# ///
"""Block 06, check: the memory path the BAND agents use, without BAND.

06_server.py must be running in another terminal.
Run: uv run --env-file .env 06_check_memory.py

It does what the integration does for a BAND room: store a message in "room 1", close
the room, then ask from "room 2". Use it to test your setup, or to show the idea if
BAND is not available.
"""

import time

from cognee_band import CogneeClient, CogneeSettings

settings = CogneeSettings.resolve()  # reads COGNEE_BASE_URL, COGNEE_API_KEY, COGNEE_BAND_DATASET
client = CogneeClient(settings)
room_1 = settings.session_id_for_room("room-1")  # one BAND room is one Cognee session
room_2 = settings.session_id_for_room("room-2")

FACT = "Mia Novak joined the Platform team as QA lead on 2026-11-09."
QUESTION = "Who is the QA lead on the Platform team?"

# Room 1: agent A is told a fact. The integration stores the message and the reply.
client.store_qa(FACT, "Noted. Mia Novak is the QA lead on Platform.", session_id=room_1)
print(f"[check] Room 1, told agent A: {FACT}")

# Room 1 closes. The integration calls improve(), which moves the room into the graph.
client.improve(room_1)
print("[check] Room 1 closed. Waiting for the graph...")

# Room 2: agent B asks. Recall reads the graph, not room 1.
start = time.time()
while time.time() - start < 120:
    results = client.recall(QUESTION, session_id=room_2)
    if "Mia Novak" in str(results):
        print(f"[check] Room 2, agent B's memory has it after {time.time() - start:.0f} seconds.")
        break
    time.sleep(5)
else:
    print(f"[check] Not found after 120 seconds. Last result: {str(results)[:300]}")
