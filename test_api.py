import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_image():
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "FakeHumanGen"
        },
        data=json.dumps({
            "model": "google/imagen-3-fast", # or "openai/dall-e-3"
            "messages": [
                {
                    "role": "user",
                    "content": "A beautiful 20-year-old asian girl, cyberpunk city, neon lights, highly detailed photography."
                }
            ]
        })
    )
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    generate_image()
