import requests
from bs4 import BeautifulSoup

def fetch_dribbble_shots(limit=5):
    """Fetch latest popular shots from Dribbble RSS."""
    url = "https://dribbble.com/shots/popular.rss"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:limit]
        shots = []
        for item in items:
            shots.append({
                "title": item.title.text,
                "url": item.link.text,
                "description": item.description.text,
                "published": item.pubDate.text
            })
        return shots
    except Exception as e:
        return [{"title": f"[ERROR] Dribbble fetch failed: {e}"}]
