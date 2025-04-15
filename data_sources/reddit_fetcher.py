import praw
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET

def get_reddit_client():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent="AppGeneratorBot/0.1 by YourUsername"
    )

def fetch_top_posts(subreddits, limit=10, time_filter="day", top_comments=5):
    reddit = get_reddit_client()
    posts = []
    for subreddit in subreddits:
        for post in reddit.subreddit(subreddit).top(time_filter=time_filter, limit=limit):
            post.comments.replace_more(limit=0)
            comments = [comment.body for comment in post.comments[:top_comments]]
            posts.append({
                "title": post.title,
                "score": post.score,
                "url": post.url,
                "id": post.id,
                "subreddit": subreddit,
                "created_utc": post.created_utc,
                "num_comments": post.num_comments,
                "selftext": post.selftext,
                "top_comments": comments
            })
    return posts

if __name__ == "__main__":
    # Example usage
    SUBREDDITS = ["startups", "entrepreneur", "InternetIsBeautiful", "AskReddit"]
    posts = fetch_top_posts(SUBREDDITS, limit=3)
    for post in posts:
        print(f"[{post['subreddit']}] {post['title']} ({post['score']} upvotes)")
