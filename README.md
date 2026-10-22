# Personal Task Automation Agent

A command-line AI agent that reads and sends Gmail on your behalf using LLM tool calling. Describe a task in plain English, and the agent picks the right tool, runs it, and reports back. Any action that can't be undone (like sending an email) needs your explicit approval first.

## Features

- **Natural-language tasks.** Type a prompt such as *"Send a birthday invite to a@example.com from Raghav, venue is Raghav's house at 8 pm."*
- **Tool calling loop.** The LLM decides when to call `read_mail` or `send_mail`, sees the result, and continues until the task is done.
- **Human-in-the-loop approval gate.** Tools are tagged by reversibility. Irreversible tools show a preview and wait for `y/n` before running.
- **Pluggable tool registry.** Adding a new tool is a schema, a function, and one registry entry.
- **Swappable LLM providers.** Any OpenAI-compatible endpoint works. Switch models by changing one line in `config.toml`.
- **Bounded execution.** A configurable `MAX_LOOP` stops runaway loops. On the final attempt, the agent is told to explain why the task could not be completed.

## How It Works

```
User prompt
    │
    ▼
main.py ── builds messages, calls LLM with tool schemas
    │
    ▼
LLM returns tool call(s)
    │
    ▼
function_call.select_service()
    ├─ looks up tool in TOOL_REGISTRY
    ├─ if "irreversible" → preview + ask user [y/n]
    │        ├─ n → returns "User rejected the action" to the LLM
    │        └─ y → continue
    └─ runs the tool function
    │
    ▼
Tool result appended to messages → loop again
    │
    ▼
finish_reason == "stop" (or MAX_LOOP reached) → done
```

## Project Structure

```
.
├── main.py                 # Entry point: prompt, LLM client, agent loop
├── function_call.py        # Tool dispatcher + approval gate
├── tool_registry.py        # Maps tool names → functions + reversibility
├── config.toml             # Model providers and loop settings
├── Functions/
│   ├── gmail_tools.py      # read_mail, send_mail + their JSON schemas
│   └── google_auth.py      # Google OAuth flow, builds Gmail/Calendar services
└── .gitignore              # Ignores .env and *.json (credentials, tokens)
```

## Tools

| Tool | Description | Reversibility | Approval |
|------|-------------|---------------|----------|
| `read_mail(n=5)` | Returns the `n` most recent inbox messages as `{id, snippet}` | `read` | Not required |
| `send_mail(to, subject, body)` | Sends a plain-text email from your Gmail account | `irreversible` | **Required** |

## Prerequisites

- Python 3.11+ (uses the built-in `tomllib`)
- A Google Cloud project with the **Gmail API** (and optionally Calendar API) enabled
- An OAuth client ID of type **Desktop app**, downloaded as `credentials.json`
- An API key for at least one LLM provider listed in `config.toml`

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/satyam-sharma7/Project_13_Personal_Task_Automation_Agent.git
   cd Project_13_Personal_Task_Automation_Agent
   ```

2. **Install dependencies**

   ```bash
   pip install openai python-dotenv google-api-python-client google-auth google-auth-oauthlib
   ```

3. **Add Google credentials.** Place `credentials.json` in the project root. On first run, a browser window opens for consent and `token.json` is created automatically.

4. **Create a `.env` file** with the key for the provider you select:

   ```env
   FREE_LLM_API=your_key
   # or one of:
   # OPENROUTER_API_KEY=...
   # GOOGLE_AI_STUDIO_3=...
   # HF_TOKEN=...
   # HF_TOKEN_2=...
   ```

5. **Pick a model** in `config.toml`:

   ```toml
   LLM_MODEL = "freellmapi"   # minmax | gemini | glm | qwen | freellmapi
   ```

## Usage

```bash
python main.py
```

```
Prompt: send a short thank-you mail to friend@example.com for yesterday's help

--- APPROVAL NEEDED ---
Send email to friend@example.com
Subject: Thank you!
Body: Hi, thanks a lot for your help yesterday...
Proceed? [y/n]: y
```

The agent then prints a summary of the result. Entering `n` rejects the action, and the LLM is told so and can respond accordingly.

## Configuration

All settings live in `config.toml`.

| Key | Purpose |
|-----|---------|
| `LLM_MODEL` | Which `[models.*]` block to use |
| `MAX_LOOP` | Maximum LLM/tool iterations per task (default `3`) |
| `[models.<name>].url` | OpenAI-compatible base URL |
| `[models.<name>].api` | Name of the env variable holding the API key |
| `[models.<name>].name` | Model identifier sent to the provider |

Preconfigured providers: OpenRouter (MiniMax), Google AI Studio (Gemini), Hugging Face router (GLM, Qwen), and a custom free LLM gateway.

## Adding a New Tool

1. Write the function and its JSON schema in a module under `Functions/`.
2. Register it in `tool_registry.py` with a reversibility level:

   ```python
   "create_event": {"func": calendar_tools.create_event, "reversibility": "reversible"},
   ```

3. Pass its schema in the `tools=[...]` list in `main.py`.
4. For irreversible tools, add a readable case in `format_preview()` in `function_call.py`.

## Security Notes

- `.gitignore` excludes `.env` and all `*.json` files so `credentials.json` and `token.json` are not committed. Never share them.
- The OAuth scopes requested are `gmail.send`, `gmail.readonly`, and `calendar`. Remove the ones you don't need in `Functions/google_auth.py`.
- The approval gate is the main safeguard against the model sending unintended emails. Keep new side-effecting tools marked `irreversible`.

## Known Limitations

- Only Gmail read and send are implemented. `search_mail` is a stub, and Calendar auth is set up but no calendar tools exist yet.
- `read_mail` returns only snippets, not full message bodies, sender, or subject.
- `MAX_CHARS`, `temperature`, and `max_tokens` in `config.toml` are defined but not yet used by `main.py`.
- There is no conversation memory across runs, and each run handles a single prompt.
- Tool errors (for example, a failed API call) are not caught, so they will crash the loop.

## Roadmap

- Calendar tools (`create_event`, `list_events`)
- Gmail search and full-message reading
- Error handling and retries around tool calls
- Multi-turn interactive session with persistent memory
- `requirements.txt` and tests

## Tech Stack

Python · OpenAI-compatible Chat Completions API · Gmail API · Google OAuth 2.0 · TOML config