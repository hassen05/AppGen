# AppGenerator

An AI-powered agent that fetches trending content, extracts problems, and generates app ideas daily using Llama via openrouter.

## Quick Start
1. Fill in your API keys in `config.py` or `.env`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Structure
- `main.py` — Entry point
- `data_sources/` — Fetch Reddit, HN, Product Hunt
- `llm/` — LLM prompt/response logic
- `output/` — Save results, notifications
- `config.py` — API keys/settings
uvicorn app.web:app --reload --port 8000
