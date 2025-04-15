from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from data_sources.reddit_fetcher import fetch_top_posts
from data_sources.hn_fetcher import fetch_top_stories
from llm.openrouter_llama import generate_app_ideas
from fastapi.responses import RedirectResponse
from app.cache_utils import save_results, load_results

app = FastAPI()

SUBREDDITS = ["startups", "entrepreneur", "InternetIsBeautiful", "AskReddit"]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    cache = load_results()
    if not cache:
        # If no cache, force refresh
        return RedirectResponse(url="/refresh")

    reddit_posts = cache.get("reddit_posts", [])
    hn_stories = cache.get("hn_stories", [])
    trends = cache.get("trends", [])
    ideas = cache.get("ideas", [])

    # Check if Google Trends failed
    trends_error = False
    if trends and isinstance(trends[0], dict) and trends[0].get("title", "").startswith("[ERROR]"):
        trends_error = True

    def get_ideas_for(posts, max_ideas=5):
        def standardize_post(p, source):
            if source == "reddit":
                return {"title": p.get("title", ""), "selftext": p.get("selftext", ""), "top_comments": p.get("top_comments", [])}
            elif source == "hn":
                return {"title": p.get("title", ""), "selftext": p.get("text", ""), "top_comments": p.get("top_comments", [])}
            elif source == "trends":
                return {"title": p.get("title", ""), "selftext": "", "top_comments": []}
            return {"title": "", "selftext": "", "top_comments": []}
        # Guess source based on input
        if posts and 'subreddit' in posts[0]:
            source = 'reddit'
        elif posts and 'score' in posts[0]:
            source = 'hn'
        else:
            source = 'trends'
        return generate_app_ideas([standardize_post(p, source) for p in posts], max_ideas=max_ideas)

    html = '''
    <html>
    <head>
        <title>AppGenerator - Trending Content & AI Suggestions</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f6fa; margin: 0; padding: 0; }
            .sticky-bar { position: sticky; top: 0; background: #fff; z-index: 10; box-shadow: 0 2px 6px #0001; padding: 8px 0 8px 0; margin-bottom: 12px; }
            .container { max-width: 700px; margin: 24px auto; background: #fff; border-radius: 14px; box-shadow: 0 2px 16px #0002; padding: 16px 10px 28px 10px; }
            h1 { text-align: center; margin: 12px 0 18px 0; font-size: 1.5em; letter-spacing: 0.04em; }
            .section { margin-bottom: 22px; border-radius: 10px; background: #fafbfc; box-shadow: 0 1px 4px #0001; padding: 14px 14px 8px 14px; }
            .site-title { display: flex; align-items: center; gap: 9px; margin-bottom: 3px; color: #1976d2; font-weight: 600; font-size: 1.08em; }
            .site-title .icon { font-size: 1.2em; }
            ul.sites { margin: 0 0 6px 0; padding: 0; list-style: none; }
            ul.sites li { margin-bottom: 5px; font-size: 0.98em; }
            .suggestions { background: #f0f4f8; border-radius: 6px; padding: 7px 12px; margin-top: 6px; transition: max-height 0.3s; }
            .suggestions-title { font-weight: 500; margin-bottom: 2px; font-size: 0.97em; display: flex; align-items: center; gap: 4px; cursor: pointer; }
            .suggestion-list { margin: 0; padding-left: 16px; display: none; }
            .suggestions.open .suggestion-list { display: block; }
            .suggestion-toggle { margin-left: 6px; font-size: 0.95em; color: #888; }
            .refresh-btn { display: block; margin: 0 auto; padding: 8px 20px; font-size: 1em; background: #1976d2; color: #fff; border: none; border-radius: 5px; cursor: pointer; transition: background 0.2s; box-shadow: 0 1px 4px #1976d220; }
            .refresh-btn:hover { background: #1256a3; }
            @media (max-width: 600px) {
                .container { max-width: 98vw; padding: 2vw; }
                h1 { font-size: 1.1em; }
                .section { padding: 8px 3vw 5px 3vw; }
            }
        </style>
        <script>
        function toggleSuggestions(id) {
            var el = document.getElementById(id);
            if (el.classList.contains('open')) {
                el.classList.remove('open');
            } else {
                el.classList.add('open');
            }
        }
        </script>
    </head>
    <body>
        <div class="sticky-bar">
            <form method="post" action="/refresh"><button class="refresh-btn" type="submit">🔄 Refresh</button></form>
        </div>
        <div class="container">
            <h1>AppGenerator: Daily Trends & AI Suggestions</h1>
            <div class="section">
                <div class="site-title"><span class="icon">👽</span>Reddit <span style="margin-left:10px;font-size:0.95em;color:#888;">({len(reddit_posts)} posts)</span></div>
                <details>
                  <summary style="cursor:pointer;font-size:1em;padding:6px 0;outline:none;"><b>Show Reddit posts</b></summary>
                  <ul class="sites">
    '''
    for post in reddit_posts:
        html += f'<li><b>[{post.get("subreddit", "?")}]</b> <a href="{post.get("url", "#")}" target="_blank">{post.get("title", "[No Title]")}</a> <span style="color:#888;font-size:0.93em">({post.get("score", 0)} upvotes)</span></li>'
    html += '''
                  </ul>
                </details>
                <div class="suggestions" id="sugg-reddit">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-reddit')">💡 AI Suggestions for Reddit <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(reddit_posts, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="site-title"><span class="icon">📰</span>Hacker News</div>
                <ul class="sites">
    '''
    for story in hn_stories:
        html += f'<li><a href="{story.get("url", "#")}" target="_blank">{story.get("title", "[No Title]")}</a> <span style="color:#888;font-size:0.93em">({story.get("score", 0)} points)</span></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-hn">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-hn')">💡 AI Suggestions for Hacker News <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(hn_stories, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="site-title"><span class="icon">🌐</span>Google Trends</div>
                <ul class="sites">
    '''
    if trends_error:
        html += '<li style="color:#d32f2f;font-weight:500;">Google Trends is currently unavailable. Please try again later.</li>'
    else:
        for trend in trends:
            html += f'<li>{trend.get("title", "[No Title]")}</li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-trends">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-trends')">💡 AI Suggestions for Google Trends <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    if not trends_error:
        for idea in get_ideas_for(trends, max_ideas=5):
            if idea.strip():
                html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    return HTMLResponse(content=html)


from fastapi import Request
from fastapi import APIRouter

from data_sources.google_trends_fetcher import fetch_trending_searches

@app.api_route("/refresh", methods=["GET", "POST"])
def refresh(request: Request):
    reddit_posts = fetch_top_posts(SUBREDDITS, limit=5)
    hn_stories = fetch_top_stories(limit=5)
    trends = fetch_trending_searches(limit=5)

    def standardize_post(p, source):
        if source == "reddit":
            return {
                "title": p.get("title", ""),
                "selftext": p.get("selftext", ""),
                "top_comments": p.get("top_comments", [])
            }
        elif source == "hn":
            return {
                "title": p.get("title", ""),
                "selftext": p.get("text", ""),
                "top_comments": p.get("top_comments", [])
            }
        elif source == "trends":
            return {
                "title": p.get("title", ""),
                "selftext": "",
                "top_comments": []
            }
        return {"title": "", "selftext": "", "top_comments": []}

    all_posts = [standardize_post(p, "reddit") for p in reddit_posts] \
                + [standardize_post(s, "hn") for s in hn_stories] \
                + [standardize_post(t, "trends") for t in trends]

    ideas = generate_app_ideas(all_posts, max_ideas=3)
    save_results({
        "reddit_posts": reddit_posts,
        "hn_stories": hn_stories,
        "trends": trends,
        "ideas": ideas
    })
    return RedirectResponse(url="/", status_code=303)
