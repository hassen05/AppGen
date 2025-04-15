import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY", "")
print(api_key)
if not api_key:
    print("[ERROR] OPENROUTER_API_KEY is missing.")
    exit(1)

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "meta-llama/llama-4-maverick:free",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ],
    "max_tokens": 10
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    response.raise_for_status()
    result = response.json()
    print(result)  # Print the full response for debugging
    if "choices" not in result:
        print(f"[ERROR] OpenRouter API test failed: {result}")
        exit(1)
    print("[SUCCESS] API responded:", result["choices"][0]["message"]["content"])
except Exception as e:
    print("[ERROR] OpenRouter API test failed:", e)
    if hasattr(e, 'response') and e.response is not None:
        print("Status code:", e.response.status_code)
        print("Response:", e.response.text)
