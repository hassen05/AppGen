from data_sources.reddit_fetcher import fetch_top_posts
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET

SUBREDDITS = ["startups", "entrepreneur", "InternetIsBeautiful", "AskReddit"]


def main():
    print("AppGenerator started\nFetching top Reddit posts...")
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        print("[ERROR] Please set your Reddit API credentials in config.py before running.")
        return
    posts = fetch_top_posts(SUBREDDITS, limit=3)
    for post in posts:
        print(f"[{post['subreddit']}] {post['title']} ({post['score']} upvotes)")

if __name__ == "__main__":
    main()
