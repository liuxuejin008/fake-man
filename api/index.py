import os
import json
import requests
import threading
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

BANANA_API_KEY = os.environ.get("BANANA_API_KEY")
BANANA_API_URL = os.environ.get("BANANA_API_URL", "https://api.acedata.cloud/nano-banana/images")

# 存储生成任务状态
task_store = {}
task_lock = threading.Lock()

# 静态文件路由 - Vercel 需要
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    if not BANANA_API_KEY:
        return jsonify({"error": "BANANA API Key not configured."}), 500

    data = request.json
    prompt = data.get('prompt', 'A beautiful 20-year-old asian girl, cyberpunk city vibe, neon lights, clear details, trending on artstation')

    enhanced_prompt = f"Photo portrait of a youthful 20 year old individual. {prompt}. Ultra realistic, 8k resolution, cinematic lighting, photorealistic."

    try:
        response = requests.post(
            url=BANANA_API_URL,
            headers={
                "Authorization": f"Bearer {BANANA_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json={
                "action": "generate",
                "prompt": enhanced_prompt,
                "aspect_ratio": "9:16",
                "model": "nano-banana-2"
            },
            timeout=60
        )

        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get("success") and resp_json.get("data"):
            image_url = resp_json["data"][0].get("image_url", "")
            return jsonify({
                "task_id": resp_json.get("task_id"),
                "status": "completed",
                "image_url": image_url,
                "prompt_used": prompt
            })
        elif resp_json.get("task_id"):
            task_id = resp_json["task_id"]
            with task_lock:
                task_store[task_id] = {
                    "status": "processing",
                    "prompt": prompt,
                    "enhanced_prompt": enhanced_prompt
                }

            threading.Thread(target=poll_task, args=(task_id,), daemon=True).start()

            return jsonify({
                "task_id": task_id,
                "status": "processing",
                "message": "Image generation started. Poll /api/status/{task_id} for updates."
            })

        elif resp_json.get("error"):
            return jsonify({
                "error": resp_json["error"].get("message", "API error"),
                "raw_content": resp_json
            }), 400
        else:
            return jsonify({
                "error": "Could not parse API response",
                "raw_content": resp_json
            }), 500

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


def poll_task(task_id):
    """后台轮询任务状态"""
    time.sleep(5)
    max_attempts = 120
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.get(
                f"{BANANA_API_URL}/{task_id}",
                headers={
                    "Authorization": f"Bearer {BANANA_API_KEY}",
                    "Accept": "application/json"
                },
                timeout=30
            )

            if response.status_code == 200:
                resp_json = response.json()
                with task_lock:
                    if resp_json.get("success") and resp_json.get("data"):
                        image_url = resp_json["data"][0].get("image_url", "")
                        task_store[task_id] = {
                            "status": "completed",
                            "image_url": image_url
                        }
                        return
                    elif resp_json.get("finished_at"):
                        with task_lock:
                            task_store[task_id] = {
                                "status": "completed",
                                "image_url": resp_json.get("data", [{}])[0].get("image_url", ""),
                                "finished_at": resp_json.get("finished_at"),
                                "elapsed": resp_json.get("elapsed", 0)
                            }
                        return

            attempt += 1
            time.sleep(5)

        except Exception as e:
            attempt += 1
            time.sleep(5)

    with task_lock:
        task_store[task_id] = {
            "status": "failed",
            "error": "Timeout waiting for image generation"
        }


@app.route('/api/status/<task_id>', methods=['GET'])
def get_status(task_id):
    with task_lock:
        task = task_store.get(task_id, {})

    if not task:
        return jsonify({
            "status": "not_found",
            "error": f"Task {task_id} not found"
        }), 404

    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
