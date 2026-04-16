import os
import requests
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

BANANA_API_KEY = os.environ.get("BANANA_API_KEY")
BANANA_API_URL = os.environ.get("BANANA_API_URL", "https://api.acedata.cloud/nano-banana/images")
BANANA_SUBMIT_TIMEOUT = int(os.environ.get("BANANA_SUBMIT_TIMEOUT", "30"))
BANANA_CALLBACK_URL = os.environ.get("BANANA_CALLBACK_URL")

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


def resolve_callback_url():
    if BANANA_CALLBACK_URL:
        return BANANA_CALLBACK_URL
    return f"{request.url_root.rstrip('/')}/api/banana/callback"

@app.route('/api/generate', methods=['POST'])
def generate():
    if not BANANA_API_KEY:
        return jsonify({"error": "BANANA API Key not configured."}), 500

    data = request.json
    prompt = data.get('prompt', 'A beautiful 20-year-old asian girl, cyberpunk city vibe, neon lights, clear details, trending on artstation')

    enhanced_prompt = f"Photo portrait of a youthful 20 year old individual. {prompt}. Ultra realistic, 8k resolution, cinematic lighting, photorealistic."
    callback_url = resolve_callback_url()

    try:
        request_body = {
            "action": "generate",
            "prompt": enhanced_prompt,
            "aspect_ratio": "9:16",
            "model": "nano-banana-2",
            "callback_url": callback_url
        }
        response = requests.post(
            url=BANANA_API_URL,
            headers={
                "Authorization": f"Bearer {BANANA_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=request_body,
            timeout=BANANA_SUBMIT_TIMEOUT
        )

        response.raise_for_status()
        resp_json = response.json()

        if resp_json.get("success") and resp_json.get("data"):
            image_url = resp_json["data"][0].get("image_url", "")
            task_id = resp_json.get("task_id")
            if task_id:
                with task_lock:
                    task_store[task_id] = {
                        "status": "completed",
                        "image_url": image_url,
                        "prompt": prompt
                    }
            return jsonify({
                "task_id": task_id,
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
                    "enhanced_prompt": enhanced_prompt,
                    "callback_url": callback_url,
                    "trace_id": resp_json.get("trace_id")
                }

            return jsonify({
                "task_id": task_id,
                "status": "processing",
                "message": "Image generation started. Result will be updated by callback.",
                "status_url": f"/api/status/{task_id}"
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

    except requests.exceptions.Timeout:
        return jsonify({
            "error": f"API submit timed out after {BANANA_SUBMIT_TIMEOUT}s."
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/banana/callback', methods=['POST'])
def banana_callback():
    payload = request.get_json(silent=True) or {}
    task_id = payload.get("task_id")

    if not task_id:
        return jsonify({"error": "Missing task_id in callback payload"}), 400

    callback_result = {
        "status": "completed" if payload.get("success") and payload.get("data") else "failed",
        "trace_id": payload.get("trace_id"),
        "raw_content": payload
    }

    if payload.get("data"):
        callback_result["image_url"] = payload["data"][0].get("image_url", "")
        callback_result["prompt"] = payload["data"][0].get("prompt", "")

    if payload.get("error"):
        callback_result["error"] = payload["error"].get("message", "Callback returned error")

    with task_lock:
        existing = task_store.get(task_id, {})
        merged = {**existing, **callback_result}
        task_store[task_id] = merged

    return jsonify({"ok": True, "task_id": task_id})


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
