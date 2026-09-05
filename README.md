# CLI-KML

CLI-KML is a from-scratch mobile-first AI coding agent for local projects. It uses FastAPI, httpx, a real OpenAI-compatible HTTP provider, filesystem tools, a permission system, and an agent tool loop.

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 python_cli/main.py
```

Open `http://127.0.0.1:8787` in the Android browser. In Termux, use the same localhost address in Chrome/Firefox on the device.

Configure API key, Base URL and model in Settings. API keys are stored in `~/.cli_kml_config.json` with mode 0600 and are never returned by `/api/config`.

## Agent loop

User request → LLM → native tool calls → permission → real tool execution → structured result → LLM → verification/further tools → final response. The loop is capped at 30 steps.

## Tools

`read_file`, `write_file`, `edit_file`, `grep`, `glob`, `tree`, `bash`.

## Security

Filesystem paths are sandboxed to the selected workspace. Secret/vendor paths are ignored by default. Dangerous shell patterns are denied. Remote HTTP uses httpx TLS verification (`verify=True`). HTTP localhost/internal endpoints can be configured intentionally; remote providers should use HTTPS.

## Testing

Run:

```bash
python3 -m pytest -q
```
