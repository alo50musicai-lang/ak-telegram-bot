from flask import Flask, request
import requests
import os
from openai import OpenAI

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ---------- توابع تلگرام ----------
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_photo(chat_id, photo_url, caption=None):
    data = {"chat_id": chat_id, "photo": photo_url}
    if caption:
        data["caption"] = caption
    requests.post(f"{TELEGRAM_API}/sendPhoto", json=data)

# ---------- هوش مصنوعی ----------
def ai_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def ai_image(prompt):
    image = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )
    return image.data[0].url

# ---------- Webhook ----------
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" not in update:
        return {"ok": True}

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    # /start
    if text == "/start":
        send_message(
            chat_id,
            "🤖 سلام!\n\n"
            "دستورها:\n"
            "1️⃣ چت: فقط پیام بفرست\n"
            "2️⃣ عکس: /image توضیح\n"
            "3️⃣ موزیک: /music توضیح"
        )
        return {"ok": True}

    # ساخت تصویر
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ توضیح عکس را بنویس")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            url = ai_image(prompt)
            send_photo(chat_id, url, "تصویر ساخته شد ✅")
        return {"ok": True}

    # موزیک (فعلاً شبیه‌سازی)
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        send_message(
            chat_id,
            "🎵 ساخت موزیک هوش مصنوعی:\n\n"
            f"سبک درخواستی: {prompt}\n\n"
            "❗ فعلاً نسخه نمایشی است\n"
            "در مرحله بعد وصل می‌کنیم به سرویس موزیک"
        )
        return {"ok": True}

    # چت عادی
    reply = ai_chat(text)
    send_message(chat_id, reply)

    return {"ok": True}

# ---------- تست دستی ----------
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

# ---------- اجرا ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)