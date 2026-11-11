# Presenter script (about 30 minutes)

For the person who runs the session. Participants follow `README.md`.

## The day before

1. Run steps 0 to 6 once on your own laptop, in order. All of it, including BAND.
2. Create your two BAND agents (README step 6.1) and put the four values in `.env`.
3. Run step 2 once before the session. The first run downloads the UI, and Node.js 22 if you don't have it.
4. Ask participants to do **Step 0** before they arrive. The install is the slow part.

## Ten minutes before

1. Run `uv run python 01_ingest.py` so you start from clean data.
2. Open three terminals in the repo folder and one browser window with two tabs:
   http://localhost:3000 and https://app.band.ai (signed in).
3. Make the terminal font large.

## The session

| Min | Step | Do | Say |
|---|---|---|---|
| 0-3 | Intro | Open `data/calls/02_checkout_v2_launch_readiness.txt` and `data/email/01_kestrel_bank_3ds2.txt` | "Five small files: two calls, two Linear issues, one email from a bank. The latest call agrees three next steps. It never says which team, which issue, or what deadline." |
| 3-7 | 1 Ingest | `uv run python 01_ingest.py` (about 50 s) | "One call: `remember()`. It stores the text and builds a graph. This prompt is what we ask the LLM to extract. You can change it." Talk about the prompt while it runs. |
| 7-11 | 2 Graph | `uv run python 02_graph.py`, open localhost:3000, Sign in, Graph, `checkout_v2`, Records, search "Omar" | "His team comes from the old call. PAY-104 comes from Linear. The deadline comes from the email. Nobody linked these by hand." Then Ctrl+C. |
| 11-14 | 3 Agent | `uv run python 03_agent_session.py` (about 20 s) | **Moment 1.** "The call never mentions Payments, PAY-104 or a date. The answer has all three." |
| 14-18 | 4 Improve | `uv run python 04_feedback_improve.py` (about 60 s) | "The bank moved the deadline. We rate the old answer, add the new fact to the session, call `improve()`." **Moment 2:** same question, new answer, 2027-01-15. |
| 18-20 | 5 Permissions | `uv run python 05_permissions.py` (about 15 s) | "A second user asks. No access. The owner gives read permission. Now it works." |
| 20-30 | 6 BAND | README steps 6.2 to 6.8 | "BAND gives agents rooms and routes messages by @mention. This one line gives a BAND agent our memory." Ask agent A, tell it a fact, Ctrl+C agent A, ask agent B in a new room. **Moment 3:** agent B knows. |

The three moments to slow down for: step 3 (one answer from three sources), step 4 (the
memory corrects itself), step 6.8 (agent B knows what agent A was told).

## Step 6, in order (you need three terminals)

| Terminal | Command | Wait for |
|---|---|---|
| 1 | `uv run python 06_server.py` | `Cognee server on http://localhost:8000` |
| 2 | `uv run python 06_api_key.py` | `Saved COGNEE_API_KEY in .env` |
| 2 | `uv run --env-file .env 06_band_agent.py a` | `Agent started: Cognee Agent A` |
| 3 | `uv run --env-file .env 06_band_agent.py b` | `Agent started: Cognee Agent B` |

Then in BAND:

1. **Rooms**, **New room**, select Cognee Agent A, **Create room**.
2. `@Cognee Agent A what are the next steps from the Checkout v2 launch readiness call? Give owner, team, due date and Linear issue for each.` It answered in 9 seconds in our test.
3. `@Cognee Agent A new fact for the team: Lena Fischer finished the first draft of the Checkout v2 launch announcement today. It is waiting for review by Omar Haddad.`
4. Terminal 2: Ctrl+C. Say what happens: "When an agent stops, its rooms move into the graph." Fill the minute by showing the one line in `06_band_agent.py`.
5. **New room**, select Cognee Agent B, **Create room**.
6. `@Cognee Agent B is the Checkout v2 launch announcement written yet, and who has to review it?` In our test agent B had the answer 52 seconds after agent A stopped.

Always type `@` and pick the agent from the list. BAND rejects a message with no mention,
and an agent that is not mentioned never receives the message.

## What BAND does (for you, not for the slides)

- BAND is where agents and people work together in shared rooms. You connect agents you run yourself, built on any framework (Pydantic AI, LangGraph, CrewAI, the Anthropic SDK and others). BAND does not run your agent's code.
- BAND routes each message to the participants it @mentions. No model takes part in routing. Agents mention each other to ask questions and hand off work.
- A BAND agent keeps nothing between rooms or restarts. The Cognee integration wraps the agent's adapter: it recalls memory before each message, stores each question and reply, and moves the room into the graph when the room ends or the agent stops.

More in `BAND_NOTES.md`.

## If you are short on time

Steps 1, 3 and 4 are the core (about 15 minutes). Step 5 stands alone. Step 6 can be shown on your screen only.

## If step 6 fails live, or you have no BAND agents

Run `uv run python 06_server.py` in one terminal and `uv run --env-file .env 06_check_memory.py` in another. It does what the integration does for a room: stores a fact as "room 1", ends it, and finds the fact from "room 2" about 12 seconds later. Then show the one wrapped line in `06_band_agent.py`. Do not debug BAND in front of the room.

## How long the steps take (measured on one laptop, 10 Nov)

Step 1: 48 to 52 s. Step 3: 17 to 23 s. Step 4: 47 to 67 s. Step 5: 12 to 13 s. Step 2 opens in about 10 s once the UI has been downloaded.
