from flask import Flask, request
import requests
import os

# ================== تنظیمات ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
HF_HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

app = Flask(__name__)

# ================== توابع تلگرام ==================
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_photo(chat_id, image_bytes):
    files = {
        "photo": ("image.png", image_bytes)
    }
    data = {"chat_id": chat_id}
    requests.post(
        f"{TELEGRAM_API}/sendPhoto",
        data=data,
        files=files
    )

# ================== ساخت تصویر ==================
def generate_image(prompt):
    try:
        response = requests.post(
            HF_MODEL_URL,
            headers=HF_HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        if response.status_code != 200:
            return None

        return response.content
    except Exception:
        return None

# ================== Webhook ==================
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" not in update:
        return {"ok": True}

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🎨 ربات ساخت تصویر فعال شد\n\n"
            "برای ساخت تصویر بنویس:\n"
            "/image توضیح تصویر\n\n"
            "مثال:\n"
            "/image یک گربه روی دیوار در شب"
        )
        return {"ok": True}

    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()

        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح تصویر را بنویس")
            return {"ok": True}

        send_message(chat_id, "⏳ در حال ساخت تصویر...")

        image_bytes = generate_image(prompt)

        if image_bytes is None:
            send_message(
                chat_id,
                "❌ ساخت تصویر ناموفق بود\n"
                "احتمالاً محدودیت رایگان HuggingFace است\n"
                "کمی بعد دوباره امتحان کن"
            )
        else:
            send_photo(chat_id, image_bytes)

        return {"ok": True}

    send_message(chat_id, "ℹ️ برای ساخت تصویر از دستور /image استفاده کن")
    return {"ok": True}

# ================== تست ==================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)