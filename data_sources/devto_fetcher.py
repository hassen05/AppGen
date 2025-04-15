import requests

def fetch_devto_articles(limit=5):
    """Fetches the latest/top articles from Dev.to."""
    url = f"https://dev.to/api/articles?top=1&per_page={limit}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        articles = resp.json()
        return [
            {
                "title": a["title"],
                "url": a["url"],
                "description": a.get("description", ""),
                "published_at": a.get("published_at", ""),
                "tags": a.get("tags", []),
                "comments_count": a.get("comments_count", 0),
                "positive_reactions_count": a.get("positive_reactions_count", 0)
            }
            for a in articles
        ]
    except Exception as e:
        return [{"title": f"[ERROR] Dev.to fetch failed: {e}"}]
