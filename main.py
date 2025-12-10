# main.py (Flask webhook version)
import os
import requests
from flask import Flask, request, jsonify

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set")

app = Flask(__name__)


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def chat_with_openai(prompt):
    if not OPENAI_KEY:
        return "OpenAI key not configured."
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      json=data, headers=headers)
    try:
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "خطا در دریافت پاسخ از OpenAI."


@app.route("/", methods=["GET"])
def home():
    return "Bot is live!"


@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return jsonify({}), 200

    msg = update.get("message")
    if not msg:
        return jsonify({}), 200

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, "ربات با موفقیت فعال شد 🎉")
        return jsonify({}), 200

    if text.startswith("/chat"):
        prompt = text.replace("/chat", "").strip()
        if not prompt:
            send_message(chat_id, "متن را بعد از /chat بنویس.")
        else:
            ans = chat_with_openai(prompt)
            send_message(chat_id, ans)
        return jsonify({}), 200

    send_message(chat_id, "دستور ناشناس — از /chat استفاده کن.")
    return jsonify({}), 200


@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    r = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={url}"
    )
    return jsonify(r.json())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
