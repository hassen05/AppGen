import requests
from bs4 import BeautifulSoup

def fetch_github_trending(limit=5):
    """Fetch trending repositories from GitHub Trending."""
    url = "https://github.com/trending"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        repos = []
        for repo in soup.select("article.Box-row")[:limit]:
            title = repo.h2.a.get_text(strip=True).replace("\n", "").replace(" ", "")
            href = repo.h2.a["href"]
            desc = repo.p.get_text(strip=True) if repo.p else ""
            lang = repo.find("span", itemprop="programmingLanguage")
            lang = lang.get_text(strip=True) if lang else ""
            stars = repo.select_one("a.Link--muted[href$='/stargazers']")
            stars = stars.get_text(strip=True) if stars else "0"
            repos.append({
                "title": title,
                "url": f"https://github.com{href}",
                "description": desc,
                "language": lang,
                "stars": stars
            })
        return repos
    except Exception as e:
        return [{"title": f"[ERROR] GitHub Trending fetch failed: {e}"}]
