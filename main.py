from flask import Flask, request
import requests
import os
import json
from gtts import gTTS  # برای تبدیل متن به صدا MP3
from io import BytesIO

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن ربات تلگرام
HF_TOKEN = os.getenv("HF_TOKEN")      # توکن HuggingFace (برای تصویر)
app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ---------- توابع تلگرام ----------
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_photo(chat_id, photo_url, caption=None):
    data = {"chat_id": chat_id, "photo": photo_url}
    if caption:
        data["caption"] = caption
    requests.post(f"{TELEGRAM_API}/sendPhoto", json=data)

def send_audio(chat_id, audio_bytes, filename="voice.mp3"):
    files = {"audio": (filename, audio_bytes)}
    data = {"chat_id": chat_id}
    requests.post(f"{TELEGRAM_API}/sendAudio", data=data, files=files)

# ---------- هوش مصنوعی / چت ----------
def ai_chat(text):
    # اگر میخوای میشه OpenAI اضافه کنی، فعلاً ساده چت برگشت میده
    # تشخیص زبان ساده:
    if any("\u0600" <= c <= "\u06FF" for c in text):  # عربی
        return "مرحباً! این پاسخ عربی است."
    elif any("a" <= c.lower() <= "z" for c in text):  # انگلیسی
        return "Hello! This is an English response."
    else:  # فارسی
        return "سلام! این پاسخ به فارسی است."

# ---------- تصویر ----------
def ai_image(prompt):
    # استفاده از HuggingFace Space رایگان
    HF_API_URL = "https://hf.space/embed/stabilityai/stable-diffusion-2-1/api/predict/"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {"data": [prompt]}
    response = requests.post(HF_API_URL, headers=headers, json=data)
    result = response.json()
    try:
        image_url = result["data"][0]["url"]
    except:
        image_url = None
    return image_url

# ---------- موزیک ساده (TTS) ----------
def ai_music(text):
    tts = gTTS(text=text, lang="fa")
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return mp3_fp

# ---------- webhook ----------
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" not in update:
        return {"ok": True}
    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    if text == "/start":
        send_message(chat_id,
                     "🤖 سلام!\nدستورها:\n"
                     "1️⃣ چت: فقط پیام بفرست\n"
                     "2️⃣ عکس: /image توضیح\n"
                     "3️⃣ موزیک: /music متن برای خواندن")
        return {"ok": True}

    # ساخت تصویر
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح عکس را بنویس")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            url = ai_image(prompt)
            if url:
                send_photo(chat_id, url, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # ساخت موزیک (TTS)
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً متن موزیک را بنویس")
        else:
            send_message(chat_id, "🎵 در حال ساخت موزیک...")
            mp3_fp = ai_music(prompt)
            send_audio(chat_id, mp3_fp, "music.mp3")
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