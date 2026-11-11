# Start here: Cognee memory for BAND agents

Welcome. In this session you build a memory for a small team with Cognee, then connect
two BAND agents to it. At the end, one agent knows what the other one was told.

## Before the session (10 minutes)

1. Get an OpenAI API key: https://platform.openai.com/api-keys
2. Open a terminal and paste one line. It downloads the workshop and installs everything.
   You do not need to install anything first.

   Windows (PowerShell):

   ```powershell
   irm https://raw.githubusercontent.com/jure-cognee/band-cognee-workshop/main/install.ps1 | iex
   ```

   macOS or Linux:

   ```bash
   curl -LsSf https://raw.githubusercontent.com/jure-cognee/band-cognee-workshop/main/install.sh | bash
   ```

3. Make a free BAND account at https://app.band.ai (needed for the last step).

## In the session (30 minutes)

Seven short steps, one command each:

0. Install
1. Give Cognee the data
2. Look at the graph
3. An agent asks the memory questions
4. Give feedback and improve the memory
5. Permissions for a second user
6. Two BAND agents share the memory

Every step in the README shows the command, what you should see, and what happened.

## The data

The sample data is in the `data/` folder of the repo and in this Drive folder: two calls,
two Linear issues and one email. It is fictional.
