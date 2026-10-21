# Personal Task Automation Agent

A command-line AI agent that takes a plain-English instruction, decides which tool to use, and carries out the task against your Gmail account. It is built on the OpenAI-compatible chat completions API with function calling, so it works with many LLM providers by changing one line in a config file.

Irreversible actions, such as sending an email, are never executed silently. The agent shows a preview and waits for your explicit approval first.

```
Prompt: send a birthday invite to friend@example.com from Raghav, venue is Raghav's house at 8 pm

--- APPROVAL NEEDED ---
Send email to friend@example.com
Subject: You're invited: Raghav's Birthday Party!
Body: ...
Proceed? [y/n]: y
```

## Features

- **Natural-language tasks**: describe what you want, and the LLM picks the right tool and arguments.
- **Gmail tools**: read the latest inbox messages and send emails through the Gmail API.
- **Human-in-the-loop approval**: tools marked `irreversible` require a `y/n` confirmation with a readable preview before they run.
- **Tool registry**: each tool is tagged with a reversibility level (`read`, `reversible`, `irreversible`), so new tools get the right safety behaviour by registration alone.
- **Bounded agent loop**: `MAX_LOOP` caps the number of LLM calls. On the final attempt the agent is told to explain to the user why the task could not be completed.
- **Swappable LLM providers**: OpenRouter, Google Gemini, Hugging Face router, or a custom endpoint, all selected from `config.toml`.
- **Secrets kept out of git**: `.env` and `*.json` (OAuth `credentials.json` / `token.json`) are git-ignored.

## How It Works

```
        ┌──────────┐   prompt    ┌──────────┐  tool_calls  ┌────────────────┐
        │   User   │ ──────────▶ │ main.py  │ ───────────▶ │ function_call  │
        └──────────┘             │ (agent   │              │ select_service │
              ▲                  │  loop)   │ ◀─────────── └───────┬────────┘
              │                  └────┬─────┘  tool result         │
              │ approval y/n          │ LLM API                    ▼
              │                       ▼                    ┌────────────────┐
              │                ┌──────────────┐            │ tool_registry  │
              └─────────────── │  LLM Provider │            │ read / irrev.  │
                               └──────────────┘            └───────┬────────┘
                                                                   ▼
                                                           ┌────────────────┐
                                                           │ Functions/     │
                                                           │ gmail_tools.py │──▶ Gmail API
                                                           └────────────────┘
```

1. `main.py` loads `config.toml` and `.env`, builds an OpenAI-compatible client for the selected provider, and asks you for a prompt.
2. The system prompt, your message, and the tool schemas (`read_mail`, `send_mail`) are sent to the LLM with `tool_choice="auto"`.
3. If the model returns tool calls, each one is passed to `select_service()` in `function_call.py`.
4. `select_service()` looks the tool up in `TOOL_REGISTRY`. If it is `irreversible`, it prints a preview and asks for approval. A rejection is returned to the model as the tool result so it can respond accordingly.
5. The tool result is appended to the conversation and the loop continues until the model stops (`finish_reason == "stop"`) or `MAX_LOOP` is reached.
6. The full message history is printed at the end.

## Project Structure

```
Project_13_Personal_Task_Automation_Agent/
├── main.py                  # Entry point: config, LLM client, agent loop
├── function_call.py         # Tool dispatch + approval gate + preview formatting
├── tool_registry.py         # Maps tool names to functions and reversibility level
├── config.toml              # Active model, loop limit, provider definitions
├── Functions/
│   ├── gmail_tools.py       # read_mail, send_mail + their JSON tool schemas
│   └── google_auth.py       # Google OAuth flow, builds Gmail & Calendar services
├── .gitignore               # Ignores .env and *.json (credentials/tokens)
└── README.md
```

## Available Tools

| Tool | Description | Reversibility | Approval |
|------|-------------|---------------|----------|
| `read_mail(n=5)` | Returns the `n` most recent inbox messages as `{id, snippet}` | `read` | Not required |
| `send_mail(to, subject, body)` | Sends a plain-text email from your Gmail account | `irreversible` | **Required** |

## Prerequisites

- Python 3.11 or newer (`tomllib` is used from the standard library)
- A Google Cloud project with the **Gmail API** enabled (and the **Calendar API** if you plan to extend the agent, since the Calendar scope is already requested)
- An OAuth client of type *Desktop app*, downloaded as `credentials.json`
- An API key for at least one LLM provider listed in `config.toml`

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/satyam-sharma7/Project_13_Personal_Task_Automation_Agent.git
cd Project_13_Personal_Task_Automation_Agent
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install openai python-dotenv google-api-python-client google-auth-oauthlib google-auth-httplib2
```

**3. Add Google credentials**

Place your OAuth client file in the project root as `credentials.json`. On the first run, a browser window opens for consent, and a `token.json` is created and reused afterwards. If you change the scopes in `google_auth.py`, delete `token.json` and sign in again.

**4. Create a `.env` file**

Add the key for the provider you select in `config.toml`:

```env
FREE_LLM_API=your_key        # models.freellmapi (default)
OPENROUTER_API_KEY=your_key  # models.minmax
GOOGLE_AI_STUDIO_3=your_key  # models.gemini
HF_TOKEN=your_token          # models.glm
HF_TOKEN_2=your_token        # models.qwen
```

Only the key for the active model is required.

## Configuration

All settings live in `config.toml`:

```toml
MAX_LOOP = 3                  # Max LLM calls per task
MAX_CHARS = 10000             # Reserved (not used yet)
LLM_MODEL = "freellmapi"      # Which [models.*] entry to use

[models.freellmapi]
provider = "freellmapi"
url = "https://freellmapi-seyc.onrender.com/v1"
api = "FREE_LLM_API"          # Name of the env var holding the API key
name = "auto"                 # Model name sent to the API
temperature = 0.3
max_tokens = 10000
```

| Provider key | Endpoint | Model | Env var |
|--------------|----------|-------|---------|
| `freellmapi` (default) | `freellmapi-seyc.onrender.com/v1` | `auto` | `FREE_LLM_API` |
| `minmax` | OpenRouter | `minimax/minimax-m2.5:free` | `OPENROUTER_API_KEY` |
| `gemini` | Google Generative Language API | `gemini-3-flash-preview` | `GOOGLE_AI_STUDIO_3` |
| `glm` | Hugging Face router | `zai-org/GLM-5.1:fireworks-ai` | `HF_TOKEN` |
| `qwen` | Hugging Face router | `Qwen/Qwen3.6-35B-A3B:featherless-ai` | `HF_TOKEN_2` |

To use another provider, add a new `[models.<name>]` block with any OpenAI-compatible endpoint and set `LLM_MODEL` to its name.

## Usage

```bash
python main.py
```

Then type a task at the prompt. Examples:

```
Prompt: read my last 3 emails and summarize them
Prompt: send a birthday invite to friend@example.com, venue is my house at 8 pm
```

For `send_mail`, review the preview and type `y` to send or `n` to cancel.

## Extending the Agent

Adding a new tool takes four steps:

1. Write the function in `Functions/` (for example `calendar_tools.py`).
2. Define its JSON schema in the same file, following `read_mail_schema` and `send_mail_schema`.
3. Register it in `tool_registry.py` with a `reversibility` of `"read"`, `"reversible"`, or `"irreversible"`.
4. Add the schema to the `tools=[...]` list in `main.py`.

Irreversible tools automatically get the approval prompt. For a nicer preview than the generic fallback, add a branch in `format_preview()` in `function_call.py`.

## Current Limitations and Roadmap

- `search_mail()` is a stub, and the `create_event` calendar tool is commented out in the registry. The Calendar scope and service are already set up in `google_auth.py`.
- `read_mail` returns only the message `id` and `snippet`, not the sender, subject or full body, and fetches messages one by one.
- Tool schemas are listed manually in `main.py` rather than generated from the registry.
- `MAX_CHARS`, `temperature` and `max_tokens` in `config.toml` are defined but not yet passed to the API call.
- `google_auth.py` authenticates both Gmail and Calendar at import time, so any run triggers the OAuth flow, even for tasks that don't need Calendar.
- There is no conversation memory between runs, and the agent handles one prompt per run.
- No `requirements.txt` yet, and `__pycache__/` files are committed. Adding a `requirements.txt` and ignoring `__pycache__/` would be a good cleanup.

## Security Notes

- Never commit `.env`, `credentials.json` or `token.json`. The `.gitignore` already excludes `.env` and all `*.json` files.
- The `gmail.send` and `calendar` scopes grant significant access, so use a test account while developing.
- The approval step is the main safeguard against the model sending an unintended email. Keep new side-effecting tools marked `irreversible`.

## Tech Stack

Python · OpenAI Python SDK (OpenAI-compatible endpoints) · Gmail API · Google OAuth 2.0 · python-dotenv · TOML configuration
