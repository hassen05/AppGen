from openai import OpenAI
import os

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3-0324:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def generate_text(prompt, max_tokens=512, temperature=0.8):
    """Generate text using OpenRouter's API with the DeepSeek model"""
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://appgenerator.dev",  # Replace with your actual site URL
                "X-Title": "AppGenerator",  # Replace with your actual site name
            },
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenRouter API call failed: {e}")
        return None

def generate_and_pick_best_ideas(posts_by_source, top_n=5, per_source_limit=2):
    """
    posts_by_source: dict of {source_name: [posts]}
    Returns: { 'per_source': {source: [ideas]}, 'best_overall': [ideas] }
    """
    # Optimized prompt for minimal token usage
    prompt = (
        f"For each source, generate up to 3 unique app ideas based only on the titles below. "
        f"Then pick the top {top_n} ideas overall. "
        "Respond in this format:\n"
        "Source: <name>\n1. ...\n\nTop Ideas:\n1. ...\n"
    )
    for source, posts in posts_by_source.items():
        prompt += f"\nSource: {source}\n"
        for p in posts[:per_source_limit]:
            title = p.get('title', '')[:70]  # Aggressively truncate
            prompt += f"- {title}\n"
    try:
        content = generate_text(prompt, max_tokens=384, temperature=0.8)
        if not content or not isinstance(content, str):
            print('[DEBUG] LLM raw response:', content)
            return {"error": f"[ERROR] LLM call failed: No output returned. Raw response: {content}"}
        # Parse per-source ideas and best overall
        per_source = {}
        best_overall = []
        current_source = None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('Source:'):
                current_source = line.replace('Source:', '').strip()
                per_source[current_source] = []
            elif line and line[0].isdigit() and '.' in line and current_source:
                per_source[current_source].append(line[line.index('.')+1:].strip())
            elif line.startswith('Top Ideas'):
                current_source = 'BEST_OVERALL'
            elif line and line[0].isdigit() and '.' in line and current_source == 'BEST_OVERALL':
                best_overall.append(line[line.index('.')+1:].strip())
        return {"per_source": per_source, "best_overall": best_overall}
    except Exception as e:
        return {"error": f"[ERROR] LLM call failed: {e}"}

def generate_app_ideas(posts, max_ideas=3):
    post_summaries = ""
    for i, p in enumerate(posts[:3]):  # Limit to 3 posts max to save tokens
        post_summaries += f"\nPOST {i+1}:\nTitle: {p['title'][:50]}\n"
        if p.get('selftext'):
            post_summaries += f"Summary: {p['selftext'][:100]}\n"  # Further truncate
        if p.get('top_comments'):
            for j, c in enumerate(p['top_comments'][:1]):  # Just 1 comment
                post_summaries += f"Comment: {c[:80]}\n"  # More aggressive truncation
    
    prompt = (
        f"You are an app idea generator. Based on the following Reddit posts, generate exactly {max_ideas} "
        f"innovative mobile app ideas. Each idea should have a clear name and brief description.\n\n"
        f"Reddit posts:{post_summaries}\n\n"
        f"Respond with a numbered list (1-{max_ideas}) of app ideas. Format as:\n"
        f"1. [App Name] - [Brief description]\n"
        f"2. [App Name] - [Brief description]\n"
        f"..."
    )
    
    try:
        content = generate_text(prompt, max_tokens=512, temperature=0.8)
        if not content or not isinstance(content, str):
            print('[DEBUG] LLM raw response:', content)
            return [f"[ERROR] LLM call failed: No output returned. Raw response: {content}"]
            
        # Clean up response and extract numbered ideas
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        ideas = []
        for line in lines:
            if line[0].isdigit() and '. ' in line:
                ideas.append(line[line.index('.')+1:].strip())
        
        # If parsing failed, just return raw lines
        if not ideas and lines:
            return lines
            
        return ideas
    except Exception as e:
        return [f"[ERROR] LLM call failed: {e}"]

def pick_best_ideas(ideas, top_n=5):
    prompt = (
        f"Analyze the following app ideas, and select the top {top_n} most promising and innovative ones. "
        "Here are the ideas:\n" +
        "\n".join(f"- {idea}" for idea in ideas)
    )
    try:
        content = generate_text(prompt, max_tokens=256, temperature=0.7)
        if not content or not isinstance(content, str):
            print('[DEBUG] LLM raw response:', content)
            return [f"[ERROR] LLM call failed: No output returned. Raw response: {content}"]
        best = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]
        return best
    except Exception as e:
        return [f"[ERROR] LLM call failed: {e}"]