from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from data_sources.reddit_fetcher import fetch_top_posts
from data_sources.hn_fetcher import fetch_top_stories
from data_sources.devto_fetcher import fetch_devto_articles
from data_sources.lobsters_fetcher import fetch_lobsters_stories
from data_sources.github_trending_fetcher import fetch_github_trending
from data_sources.dribbble_fetcher import fetch_dribbble_shots
from data_sources.techcrunch_fetcher import fetch_techcrunch_articles
from llm.openrouter_llama import generate_app_ideas, pick_best_ideas
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
    devto_articles = cache.get("devto_articles", [])
    lobsters_stories = cache.get("lobsters_stories", [])
    github_trending = cache.get("github_trending", [])
    dribbble_shots = cache.get("dribbble_shots", [])
    techcrunch_articles = cache.get("techcrunch_articles", [])
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
        if posts and posts and isinstance(posts[0], dict):
            if 'subreddit' in posts[0]:
                source = 'reddit'
            elif 'score' in posts[0]:
                source = 'hn'
            else:
                source = 'trends'
        else:
            source = 'trends'
        return generate_app_ideas([standardize_post(p, source) for p in posts], max_ideas=max_ideas)

    # Generate ideas for each source
    reddit_ideas = get_ideas_for(reddit_posts, max_ideas=5)
    hn_ideas = get_ideas_for(hn_stories, max_ideas=5)
    devto_ideas = get_ideas_for(devto_articles, max_ideas=5)
    lobsters_ideas = get_ideas_for(lobsters_stories, max_ideas=5)
    github_ideas = get_ideas_for(github_trending, max_ideas=5)
    dribbble_ideas = get_ideas_for(dribbble_shots, max_ideas=5)
    techcrunch_ideas = get_ideas_for(techcrunch_articles, max_ideas=5)
    trends_ideas = get_ideas_for(trends, max_ideas=5)

    # Aggregate all ideas
    all_ideas = []
    for ideas in [reddit_ideas, hn_ideas, devto_ideas, lobsters_ideas, github_ideas, dribbble_ideas, techcrunch_ideas, trends_ideas]:
        if isinstance(ideas, list):
            all_ideas.extend(ideas)
        elif isinstance(ideas, str):
            all_ideas.append(ideas)
    best_ideas = pick_best_ideas(all_ideas, top_n=5)

    # Batch all sources and generate ideas + pick best in one LLM call
    from llm.openrouter_llama import generate_and_pick_best_ideas
    posts_by_source = {
        "Reddit": reddit_posts,
        "Hacker News": hn_stories,
        "Dev.to": devto_articles,
        "Lobsters": lobsters_stories,
        "GitHub Trending": github_trending,
        "Dribbble": dribbble_shots,
        "TechCrunch": techcrunch_articles,
        "Google Trends": trends
    }
    ideas_result = generate_and_pick_best_ideas(posts_by_source, top_n=5, per_source_limit=2)
    per_source_ideas = ideas_result.get("per_source", {})
    best_ideas = ideas_result.get("best_overall", [])
    # Save all ideas to a JSON file
    import json
    ideas_to_save = {**per_source_ideas, "best_ideas": best_ideas}
    with open("latest_app_ideas.json", "w", encoding="utf-8") as f:
        json.dump(ideas_to_save, f, ensure_ascii=False, indent=2)

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
            <span style="font-weight:600;letter-spacing:0.03em;">AppGenerator</span>
            <a href="/refresh" style="float:right;margin-right:18px;background:#1976d2;color:#fff;padding:4px 12px;border-radius:7px;text-decoration:none;font-size:0.97em;">🔄 Refresh</a>
        </div>
        <div class="container">
            <h1>Trending Content & AI App Ideas</h1>

            <div class="best-ideas-section" style="background:#e3f2fd;border:2px solid #1976d2;padding:18px 16px 14px 16px;border-radius:14px;margin-bottom:28px;box-shadow:0 2px 8px #1976d222;">
                <div class="best-ideas-title" style="font-size:1.18em;font-weight:bold;color:#1976d2;margin-bottom:8px;display:flex;align-items:center;gap:8px;">🏆 Top 5 App Ideas (All Sources)</div>
                <ul class="best-ideas-list" style="margin:0 0 0 10px;padding:0;">
    '''
    for idea in best_ideas:
        html += f'<li>{idea}</li>'
    html += '''
                </ul>
            </div>

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
                <div class="site-title"><span class="icon">📝</span>Dev.to</div>
                <ul class="sites">
    '''
    for article in devto_articles:
        html += f'<li><a href="{article.get("url", "#")}" target="_blank">{article.get("title", "[No Title]")}</a> <span style="color:#888;font-size:0.93em">({article.get("positive_reactions_count", 0)} reactions)</span></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-devto">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-devto')">💡 AI Suggestions for Dev.to <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(devto_articles, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="site-title"><span class="icon">🦞</span>Lobsters</div>
                <ul class="sites">
    '''
    for story in lobsters_stories:
        html += f'<li><a href="{story.get("url", "#")}" target="_blank">{story.get("title", "[No Title]")}</a> <span style="color:#888;font-size:0.93em">({story.get("score", 0)} points)</span></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-lobsters">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-lobsters')">💡 AI Suggestions for Lobsters <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(lobsters_stories, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            {% for idea in best_ideas %}
                <li>{{ idea }}</li>
            {% endfor %}
                </ul>
            </div>

            <div class="section">
                <div class="site-title"><span class="icon">💻</span>GitHub Trending</div>
                <ul class="sites">
    '''
    for repo in github_trending:
        html += f'<li><a href="{repo.get("url", "#")}" target="_blank">{repo.get("title", "[No Title]")}</a> <span style="color:#888;font-size:0.93em">({repo.get("stars", 0)} ★, {repo.get("language", "")} )</span></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-github">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-github')">💡 AI Suggestions for GitHub Trending <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(github_trending, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="site-title"><span class="icon">🎨</span>Dribbble</div>
                <ul class="sites">
    '''
    for shot in dribbble_shots:
        html += f'<li><a href="{shot.get("url", "#")}" target="_blank">{shot.get("title", "[No Title]")}</a></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-dribbble">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-dribbble')">💡 AI Suggestions for Dribbble <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(dribbble_shots, max_ideas=5):
        if idea.strip():
            html += f'<li>{idea}</li>'
    html += '''
                    </ul>
                </div>
            </div>
            <div class="section">
                <div class="site-title"><span class="icon">📰</span>TechCrunch</div>
                <ul class="sites">
    '''
    for article in techcrunch_articles:
        html += f'<li><a href="{article.get("url", "#")}" target="_blank">{article.get("title", "[No Title]")}</a></li>'
    html += '''
                </ul>
                <div class="suggestions" id="sugg-techcrunch">
                    <div class="suggestions-title" onclick="toggleSuggestions('sugg-techcrunch')">💡 AI Suggestions for TechCrunch <span class="suggestion-toggle">▼</span></div>
                    <ul class="suggestion-list">
    '''
    for idea in get_ideas_for(techcrunch_articles, max_ideas=5):
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
    devto_articles = fetch_devto_articles(limit=5)
    lobsters_stories = fetch_lobsters_stories(limit=5)
    github_trending = fetch_github_trending(limit=5)
    dribbble_shots = fetch_dribbble_shots(limit=5)
    techcrunch_articles = fetch_techcrunch_articles(limit=5)
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
        "devto_articles": devto_articles,
        "lobsters_stories": lobsters_stories,
        "github_trending": github_trending,
        "dribbble_shots": dribbble_shots,
        "techcrunch_articles": techcrunch_articles,
        "trends": trends,
        "ideas": ideas
    })
    return RedirectResponse(url="/", status_code=303)
