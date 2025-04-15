import json
from pathlib import Path

CACHE_FILE = Path(__file__).parent / "latest_results.json"

def save_results(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_results():
    if not CACHE_FILE.exists():
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
