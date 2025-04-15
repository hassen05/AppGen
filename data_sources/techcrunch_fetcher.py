import requests
from bs4 import BeautifulSoup

def fetch_techcrunch_articles(limit=5):
    """Fetch latest articles from TechCrunch RSS feed."""
    url = "https://techcrunch.com/feed/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.find_all("item")[:limit]
        articles = []
        for item in items:
            articles.append({
                "title": item.title.text,
                "url": item.link.text,
                "description": item.description.text,
                "published": item.pubDate.text
            })
        return articles
    except Exception as e:
        return [{"title": f"[ERROR] TechCrunch fetch failed: {e}"}]
