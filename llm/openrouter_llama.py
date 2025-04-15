from openai import OpenAI
from config import OPENROUTER_API_KEY

OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
LLAMA_MODEL = "meta-llama/llama-4-maverick:free"

client = OpenAI(
    base_url=OPENROUTER_API_URL,
    api_key=OPENROUTER_API_KEY,
)

def generate_app_ideas(posts, max_ideas=3):
    if not OPENROUTER_API_KEY:
        return ["[ERROR] Please set your OPENROUTER_API_KEY in config.py."]
    post_summaries = ""
    for p in posts:
        post_summaries += f"\n---\nTitle: {p['title']}\n"
        if p.get('selftext'):
            post_summaries += f"Body: {p['selftext']}\n"
        if p.get('top_comments'):
            post_summaries += "Top Comments:\n"
            for c in p['top_comments']:
                post_summaries += f"- {c}\n"
    prompt = f"""
Given the following Reddit posts and their top comments, extract key daily problems or pain points discussed and generate {max_ideas} creative app ideas to solve those problems. Focus on things that could be turned into useful apps or tools.\n\nPosts:{post_summaries}\n\nRespond with a numbered list of app ideas, each with a title and 1-2 sentence description.\n"""
    try:
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert startup idea generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.8
        )
        content = completion.choices[0].message.content
        # Split numbered list into separate ideas
        ideas = [line.strip() for line in content.split("\n") if line.strip()]
        return ideas
    except Exception as e:
        return [f"[ERROR] LLM call failed: {e}"]
