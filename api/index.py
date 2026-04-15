import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

BANANA_API_KEY = os.environ.get("BANANA_API_KEY")
BANANA_API_URL = os.environ.get("BANANA_API_URL", "https://api.acedata.cloud/nano-banana/images")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    if not BANANA_API_KEY:
        return jsonify({"error": "BANANA API Key not configured."}), 500

    data = request.json
    prompt = data.get('prompt', 'A beautiful 20-year-old asian girl, cyberpunk city vibe, neon lights, clear details, trending on artstation')
    
    # Optional enhancement for better "fake human" quality
    enhanced_prompt = f"Photo portrait of a youthful 20 year old individual. {prompt}. Ultra realistic, 8k resolution, cinematic lighting, photorealistic."

    try:
        response = requests.post(
            url=BANANA_API_URL,
            headers={
                "Authorization": f"Bearer {BANANA_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": enhanced_prompt,
                "aspect_ratio": "9:16"  # typical portrait mode
            },
            timeout=60
        )
        
        response.raise_for_status()
        resp_json = response.json()
        
        # Parse the Banana API response. Acedata typically returns { "success": true, "data": { "image_url": "..." } } or { "data": [{ "url": "..." }] }
        image_url = ""
        
        if "data" in resp_json:
            if isinstance(resp_json["data"], list) and len(resp_json["data"]) > 0:
                # DALL-E style
                image_url = resp_json["data"][0].get("url", "")
            elif isinstance(resp_json["data"], dict):
                # Another common style
                image_url = resp_json["data"].get("image_url", "")
            else:
                image_url = str(resp_json["data"])
        elif "url" in resp_json:
            image_url = resp_json["url"]
        elif "response" in resp_json: # Midjourney style maybe
            image_url = resp_json["response"]
        
        # If we didn't find the url properly, just send back the whole raw json for debugging on frontend or assume it failed
        if not image_url:
             # Let's stringify the JSON payload and send it to front-end for debug
             return jsonify({
                "error": "Could not parse image URL from API response", 
                "raw_content": resp_json
             }), 500

        return jsonify({
            "image_url": image_url,
            "raw_content": resp_json,
            "prompt_used": prompt
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
