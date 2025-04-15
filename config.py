import os
from dotenv import load_dotenv

# Load environment variables from .env if present (for local development)
load_dotenv()

# OpenRouter (LLM) API key (for app idea generation)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Reddit API credentials (for PRAW)
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")

# Product Hunt API token (for trending products)
PRODUCT_HUNT_TOKEN = os.environ.get("PRODUCT_HUNT_TOKEN", "")

# (Optional) Telegram and Notion keys (for notifications or future integrations)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
