% project-weather — AI helper instructions

Short goal
- This repository is a small console application that shows weather data by city name or coordinates. The runtime entry points live under `app/`.

Architecture & important files
- `app/main.py` — CLI entrypoint (reads args, orchestrates calls).
- `app/client/REST_API/controller.py` — REST API client / controller layer (currently empty placeholder; extend here for HTTP integration or business logic).
- `requirements.txt` — Python dependencies (check before running).

How to be productive quickly
- Look for business logic in `app/` first. Follow the pattern: `main.py` orchestrates -> `client/` contains API or IO code -> `REST_API` contains controller logic.
- If you add or modify request/response handling, keep parsing and network code inside `client/` and keep `main.py` minimal (CLI args and orchestration).

Conventions and patterns discovered
- Small script-style project: single package under `app/`. Prefer simple functions over heavy frameworks.
- Tests not present — add minimal unit tests under `tests/` if you introduce new logic.

Run / debug
- Ensure dependencies are installed: `pip install -r requirements.txt` (file may be empty or missing; check repository root). Then run `python -m app.main` from repo root.

Integration points
- External weather API (not specified in code). If you add an API key, do NOT commit it — use environment variables (e.g., `WEATHER_API_KEY`).

Examples from repo
- Controller to implement: `app/client/REST_API/controller.py` — currently empty. Implement functions here such as `get_weather_by_city(city: str) -> dict` and keep network calls in `client/`.

If you are unsure
- Ask: where should API configuration (base URL, key) live — a new `config.py` under `app/` or environment variables?
- Ask: expected output format for CLI (plain text, JSON, or both)?

What I will do next
- If you want, I can implement a starter `controller.py` with a simple HTTP client using `requests`, a small CLI arg parser in `main.py`, and a `README` run example.
