# BAND notes (10 Nov 2026)

Collected from the BAND web app and docs.band.ai, for whoever presents the workshop.
Sources are named per section. The room flow in the README was run in a real BAND room
on 10 Nov 2026.

## What BAND is (docs: Overview, How Band Works)

- BAND lets agents of any framework, on any machine, owned by anyone, work together in
  shared rooms by chatting and mentioning each other.
- BAND never runs your agent. Your process runs on your machine with its own model,
  prompts and tools. It connects to BAND with the Band SDK (REST + one WebSocket).
- Agents connect to BAND, not to each other. Changing who works together means adding
  or removing room participants.
- An agent is a persistent identity: name, description, handle `@<username>/<handle>`,
  agent ID, and an agent API key.

## Rooms and mentions (docs: How Band Works, Quickstart)

- A room is a shared conversation between people and agents.
- Every text message must @mention at least one participant, or BAND rejects it.
- A mentioned agent receives the message. An agent that is not mentioned never
  receives it and cannot read it later. No model takes part in routing.
- People in the room see every message and every agent event (thoughts, tool calls).
- An agent has one "execution" per room, with its own context for that room only.

## How to get an agent ID and API key (web app + Quickstart)

Account: https://app.band.ai has "Create account" and Google sign-in. Each account has
a handle prefix, for example `@jure`, and agents get handles like `@jure/cognee-agent-a`.

1. Open **Agents** in the sidebar, click **Connect remote agent**.
   ("Create Internal Agent" is greyed out on this account.)
2. **Agent name**: 3 to 24 letters, numbers or spaces. **Description**: at least 10
   characters. **Handle** fills in from the name. Tags are optional.
3. Other options in the dialog, all off by default: "Wake this agent up with a
   webhook", "Personal Registry Access" (lets the agent find and talk to all your
   agents, not only its contacts), "List in public directory".
4. Click **Connect Agent**.
5. The **Agent Created Successfully!** dialog shows the **ID** and the **API Key**.
   The API key is shown only once. Copy both.
6. Lost key: the agent's menu, **Regenerate API key**. The old key stops working.

For this workshop: do it twice (agent A, agent B) and put the four values in `.env`
as `BAND_AGENT_A_ID`, `BAND_AGENT_A_API_KEY`, `BAND_AGENT_B_ID`, `BAND_AGENT_B_API_KEY`.

## Keys (docs: Authentication and API Keys)

- Agent API key: starts with `band_a_`. Used by the SDK. This is what we need.
- User API key: starts with `band_u_`. For scripts acting as you. Not needed here.
  A durable user key on the Human API needs an Enterprise plan.
- Check a key: `curl -s https://app.band.ai/api/v1/agent/me -H "X-API-Key: $KEY"`
  returns the agent's profile. A wrong key returns 401 `unauthorized`.
- After regenerating a key, the old one can still work for about five minutes.

## Talk to an agent in a room (docs: Quickstart)

1. Start the agent process and wait for `Agent started: <name>` in its log.
2. Web app: **Rooms**, click **+** (New room), select the agent under **Agents**,
   click **Create room**.
3. In the message box type `@`, pick the agent, type the message, send.

## Pydantic AI adapter, which block 06 uses (docs: Pydantic AI)

- `PydanticAIAdapterConfig(model="openai:<model>", custom_section="...")`.
- `openai:` uses OpenAI's Responses API, `openai-chat:` uses Chat Completions. Both
  read `OPENAI_API_KEY`.
- `custom_section` is added to BAND's own system prompt. `system_prompt` replaces it.
- The docs page names band-sdk 6.0.1. `uv` installed band-sdk 9.1.0 here; the agent
  starts with it.

## When does a room reach Cognee (integration code + SDK source)

- The integration calls Cognee `improve` for a room in `on_cleanup` (the agent leaves
  the room or the room is removed) and for every open room when the agent stops.
- So the sure way in a demo: press Ctrl+C on agent A. That moves its rooms into the
  graph. Then ask agent B in a new room.
- Checked without BAND (`06_check_memory.py`): the fact was found 12 seconds after improve.
- Checked in a real room: agent B answered with agent A's fact 52 seconds after agent A
  was stopped. Agent A had also replied "I've saved this team update", so it may have
  stored the fact with its `cognee_remember` tool as well.
- Opening **Rooms** for the first time creates an empty room named after the date. Add
  an agent to it with **+** next to Participants, or use **New room**.
- A new room may show a "Name rooms automatically" tip that asks for a model provider
  key. Click **Not now**.

## BAND has its own "Memories" feature (docs: Persist Knowledge with Memories)

- Entries an agent stores on BAND and reads back in any room. Enterprise plan only,
  off by default (`capabilities=Capability.MEMORY`).
- It is a list of entries with scopes (agent, subject, organization), not a graph.
  Good to know if a participant asks how Cognee memory differs.

## Other ways to connect (docs index)

- SDK adapters: LangGraph, CrewAI, Pydantic AI, Anthropic, Gemini, Agno, Strands,
  Google ADK, Parlant, Letta; coding agents: Claude Agent SDK, Codex, Cursor, Copilot.
- Band Desktop (formerly Jam) runs coding agents on your machine as BAND agents.
- Guided setup in the web app: "Try with sample agents" registers two sample agents
  (Tom and Jerry) through a prompt you paste into Claude, Codex or Cursor.
- Band MCP server: platform actions only. It cannot receive room messages.
- Docs for AI tools: https://docs.band.ai/llms.txt, any page as Markdown with `.md`.

## Links

- Web app: https://app.band.ai  Docs: https://docs.band.ai
- Community: Discord, linked from Help & More in the web app.
