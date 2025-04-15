import requests

def fetch_lobsters_stories(limit=5):
    """Fetches the latest/top stories from Lobsters."""
    url = f"https://lobste.rs/hottest.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        stories = resp.json()[:limit]
        return [
            {
                "title": s["title"],
                "url": s["url"],
                "description": s.get("description", ""),
                "created_at": s.get("created_at", ""),
                "tags": s.get("tags", []),
                "comments_count": s.get("comments_count", 0),
                "score": s.get("score", 0)
            }
            for s in stories
        ]
    except Exception as e:
        return [{"title": f"[ERROR] Lobsters fetch failed: {e}"}]
