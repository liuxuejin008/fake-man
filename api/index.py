import os
import sys
import requests
import threading
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.dirname(os.path.abspath(__file__))
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from db import save_generation, list_gallery  # noqa: E402

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

BANANA_API_KEY = os.environ.get("BANANA_API_KEY")
BANANA_API_URL = os.environ.get("BANANA_API_URL", "https://api.acedata.cloud/nano-banana/images")
BANANA_SUBMIT_TIMEOUT = int(os.environ.get("BANANA_SUBMIT_TIMEOUT", "30"))
BANANA_CALLBACK_URL = os.environ.get("BANANA_CALLBACK_URL")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "minimax/minimax-m2.7")
OPENROUTER_URL = os.environ.get("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
OPENROUTER_HTTP_REFERER = os.environ.get("OPENROUTER_HTTP_REFERER", "https://fake-man.vercel.app")
OPENROUTER_APP_TITLE = os.environ.get("OPENROUTER_APP_TITLE", "fake-man")
OPENROUTER_TIMEOUT = int(os.environ.get("OPENROUTER_TIMEOUT", "90"))

STYLE_GUIDANCE = {
    "alternate": (
        "「伪人」Alternates：源自《曼德拉记录》一类模仿人类的存在，恐怖谷——远看像普通人，近看眼神空洞或对焦不对、微笑略宽、"
        "肢体角度略反关节、影子/比例微妙错位；中文语境也常指《寻找伪人》式日常场景里的怪异非人感，可带一点网络玩梗式的「不对劲」，"
        "但核心仍是违和与不安，不是普通帅哥美女写真。画质倾向监控、门铃摄像头、伪纪录片或褪色家庭录像。"
        "避免血腥直白描写。"
    ),
    "cyberpunk": "赛博朋克：霓虹、雨夜、义体/全息元素，人物与场景统一。",
    "anime": "日系动漫风：角色造型、色彩、背景符合该风格。",
    "realistic": "写实摄影风：自然光或棚拍质感，细节可信。",
    "fantasy": "奇幻：魔法、异世界、史诗氛围，人物与服饰统一。",
}

INSPIRE_SYSTEM_DEFAULT = (
    "你是文生图提示词助手。只输出一段可直接粘贴进绘图模型的中文描述，"
    "不要标题、不要列表、不要引号包裹、不要解释过程。"
    "长度约 80～200 字，信息具体（人物外观、服装、环境、光线、镜头感）。"
)

INSPIRE_SYSTEM_ALTERNATE = (
    "你是文生图提示词助手，专精「伪人 / Alternate」题材。只输出一段可直接粘贴进绘图模型的中文描述，"
    "不要标题、不要列表、不要引号包裹、不要解释过程。长度约 80～200 字。"
    "必须写出恐怖谷：外表像日常里的普通人，但在眼神、眨眼频率、嘴角弧度、脖颈或手指关节、皮肤蜡感、"
    "与门框/台阶的比例等处写出「说不清哪里不对」的违和；场景用走廊、电梯口、楼道窗、便利店角落、"
    "教室后排等日常或阈限空间，镜头像监控、行车记录仪、门铃鱼眼或褪色家庭录像。"
    "禁止把主轴写成网红精致妆容、潮流穿搭、影棚布光；可略带中文互联网的调侃式「非人感」但不要写成纯搞笑段子。"
)

PROMPT_WRAP_REALISTIC = (
    "Photo portrait of a youthful 20 year old individual. {prompt}. "
    "Ultra realistic, 8k resolution, cinematic lighting, photorealistic."
)

PROMPT_WRAP_ALTERNATE = (
    "Analog horror, Mandela Catalogue–style uncanny human figure. {prompt}. "
    "Surveillance CCTV or doorbell camera angle, heavy grain, slight lens distortion, "
    "liminal empty interior, subtly wrong anatomy or facial symmetry, dead empty eyes; "
    "not a glamorous beauty portrait, no explicit gore."
)

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


@app.route('/api/gallery', methods=['GET'])
def gallery():
    """Recent images saved from successful generations (callback or sync)."""
    limit = request.args.get('limit', default=24, type=int)
    items = list_gallery(limit)
    return jsonify({"items": items})


def resolve_callback_url():
    if BANANA_CALLBACK_URL:
        return BANANA_CALLBACK_URL
    return f"{request.url_root.rstrip('/')}/api/banana/callback"


@app.route('/api/inspire', methods=['POST'])
def inspire():
    """用 OpenRouter 大模型生成一条文生图描述（供「随机灵感」使用）。"""
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OPENROUTER_API_KEY not configured."}), 500

    data = request.get_json(silent=True) or {}
    style = (data.get("style") or "realistic").strip()
    guidance = STYLE_GUIDANCE.get(style, STYLE_GUIDANCE["realistic"])

    system = INSPIRE_SYSTEM_ALTERNATE if style == "alternate" else INSPIRE_SYSTEM_DEFAULT
    user = (
        f"当前风格代码：{style}。\n"
        f"风格要点：{guidance}\n"
        "请生成一条新的、与常见套路不太重复的描述。"
    )

    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": OPENROUTER_HTTP_REFERER,
                "X-Title": OPENROUTER_APP_TITLE,
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.95,
                "max_tokens": 500,
            },
            timeout=OPENROUTER_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
        err = payload.get("error")
        if err:
            msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            return jsonify({"error": msg, "raw": payload}), 502

        choices = payload.get("choices") or []
        if not choices:
            return jsonify({"error": "Empty choices from OpenRouter", "raw": payload}), 502

        content = (choices[0].get("message") or {}).get("content") or ""
        text = content.strip()
        if not text:
            return jsonify({"error": "Model returned empty text", "raw": payload}), 502

        return jsonify({"prompt": text, "style": style, "model": OPENROUTER_MODEL})

    except requests.exceptions.Timeout:
        return jsonify({"error": f"OpenRouter request timed out after {OPENROUTER_TIMEOUT}s."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"OpenRouter request failed: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate():
    if not BANANA_API_KEY:
        return jsonify({"error": "BANANA API Key not configured."}), 500

    data = request.json or {}
    prompt = data.get(
        'prompt',
        'A beautiful 20-year-old asian girl, cyberpunk city vibe, neon lights, clear details, trending on artstation',
    )
    gen_style = (data.get("style") or "realistic").strip()
    if gen_style == "alternate":
        enhanced_prompt = PROMPT_WRAP_ALTERNATE.format(prompt=prompt)
    else:
        enhanced_prompt = PROMPT_WRAP_REALISTIC.format(prompt=prompt)
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
                        "prompt": prompt,
                        "style": gen_style,
                    }
            save_generation(
                image_url,
                prompt,
                gen_style,
                str(task_id) if task_id else None,
            )
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
                    "style": gen_style,
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

    to_save = None
    with task_lock:
        existing = task_store.get(task_id, {})
        merged = {**existing, **callback_result}
        if existing.get("prompt"):
            merged["prompt"] = existing["prompt"]
        task_store[task_id] = merged
        if merged.get("status") == "completed" and merged.get("image_url"):
            to_save = (
                merged["image_url"],
                merged.get("prompt") or "",
                merged.get("style") or "",
                str(task_id),
            )

    if to_save:
        save_generation(to_save[0], to_save[1], to_save[2], to_save[3])

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
