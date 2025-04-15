import requests

def fetch_top_stories(limit=10, top_comments=5):
    base_url = "https://hacker-news.firebaseio.com/v0"
    top_ids = requests.get(f"{base_url}/topstories.json").json()[:limit]
    stories = []
    for story_id in top_ids:
        story = requests.get(f"{base_url}/item/{story_id}.json").json()
        if not story or story.get('type') != 'story':
            continue
        comments = []
        if 'kids' in story:
            for comment_id in story['kids'][:top_comments]:
                comment = requests.get(f"{base_url}/item/{comment_id}.json").json()
                if comment and comment.get('text'):
                    comments.append(comment['text'])
        stories.append({
            'title': story.get('title', ''),
            'url': story.get('url', ''),
            'score': story.get('score', 0),
            'id': story_id,
            'by': story.get('by', ''),
            'text': story.get('text', ''),
            'top_comments': comments
        })
    return stories

if __name__ == "__main__":
    stories = fetch_top_stories(limit=3)
    for s in stories:
        print(f"{s['title']} ({len(s['top_comments'])} comments)")
