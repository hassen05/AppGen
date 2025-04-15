import requests
import os
from config import PRODUCT_HUNT_TOKEN

def fetch_producthunt_posts(limit=5):
    """Fetches trending products from Product Hunt."""
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        "Authorization": f"Bearer {PRODUCT_HUNT_TOKEN}",
        "Content-Type": "application/json",
    }
    query = '{ posts(order: VOTES, first: %d) { edges { node { name tagline url votesCount commentsCount } } } }' % limit
    data = {"query": query}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        posts = resp.json()["data"]["posts"]["edges"]
        return [
            {
                "title": p["node"]["name"],
                "url": p["node"]["url"],
                "description": p["node"].get("tagline", ""),
                "votes": p["node"].get("votesCount", 0),
                "comments": p["node"].get("commentsCount", 0)
            }
            for p in posts
        ]
    except Exception as e:
        return [{"title": f"[ERROR] Product Hunt fetch failed: {e}"}]
