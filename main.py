from flask import Flask, request
import requests
import os
from gtts import gTTS
import io

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
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

def send_audio(chat_id, audio_bytes, filename="audio.mp3"):
    url = f"{TELEGRAM_API}/sendAudio"
    files = {"audio": (filename, audio_bytes)}
    data = {"chat_id": chat_id}
    requests.post(url, data=data, files=files)

# ---------- هوش مصنوعی ساده ----------
def ai_chat(text):
    # تشخیص زبان و پاسخ ساده
    if any(word in text.lower() for word in ["hello", "hi", "how"]):
        return "Hello 👋\nThis reply is in English."
    elif any(word in text for word in ["سلام", "چطوری", "درود"]):
        return "سلام 😊\nاین پاسخ به زبان فارسی است."
    elif any(word in text for word in ["مرحبا", "أهلا"]):
        return "مرحباً 👋\nهذا الرد باللغة العربية."
    else:
        return "سلام 😊 این پاسخ به زبان فارسی است."

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
        send_message(chat_id,
            "🤖 سلام!\n\n"
            "دستورها:\n"
            "1️⃣ چت: فقط پیام بفرست\n"
            "2️⃣ عکس: /image توضیح\n"
            "3️⃣ موزیک: /music متن"
        )
        return {"ok": True}

    # ساخت تصویر (نمونه رایگان)
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح عکس را بنویسید")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            # استفاده از تصویر نمونه از اینترنت
            sample_image = "https://placekitten.com/512/512"
            send_photo(chat_id, sample_image, "تصویر ساخته شد ✅")
        return {"ok": True}

    # ساخت موزیک/صدا با gTTS
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً متن موزیک/شعر را بنویسید")
        else:
            tts = gTTS(prompt, lang="fa")
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            send_audio(chat_id, audio_bytes, filename="music.mp3")
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