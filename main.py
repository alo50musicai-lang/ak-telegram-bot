from flask import Flask, request
import requests
import os
from gtts import gTTS
from io import BytesIO

# ================== تنظیمات ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)

# ================== توابع تلگرام ==================
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

def send_audio(chat_id, audio_bytes, filename="music.mp3"):
    files = {"audio": (filename, audio_bytes)}
    data = {"chat_id": chat_id}
    requests.post(f"{TELEGRAM_API}/sendAudio", data=data, files=files)

# ================== چت چندزبانه ==================
def ai_chat(text):
    persian_chars = set("پچژگکگیی")
    arabic_chars = set("ضصثقغعخحجشسیبلاتنمكطظزوةى")

    has_persian = any(c in persian_chars for c in text)
    has_arabic = any(c in arabic_chars for c in text)
    has_english = any("a" <= c.lower() <= "z" for c in text)

    if has_persian:
        return "سلام 😊\nاین پاسخ به زبان فارسی است."
    elif has_english:
        return "Hello 👋\nThis reply is in English."
    elif has_arabic:
        return "مرحباً 👋\nهذا الرد باللغة العربية."
    else:
        return "سلام! پیام شما دریافت شد."

# ================== ساخت تصویر ==================
def ai_image(prompt):
    # HuggingFace Space رایگان
    url = "https://hf.space/embed/stabilityai/stable-diffusion-2-1/api/predict"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"data": [prompt]}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        result = r.json()
        return result["data"][0]["url"]
    except:
        return None

# ================== ساخت موزیک (TTS) ==================
def ai_music(text):
    tts = gTTS(text=text, lang="fa")
    mp3 = BytesIO()
    tts.write_to_fp(mp3)
    mp3.seek(0)
    return mp3

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
            "🤖 سلام!\n\n"
            "دستورها:\n"
            "🗨 چت: فقط پیام بفرست\n"
            "🖼 عکس: /image توضیح\n"
            "🎵 موزیک: /music متن"
        )
        return {"ok": True}

    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ توضیح عکس را بنویس")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            img_url = ai_image(prompt)
            if img_url:
                send_photo(chat_id, img_url, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ متن موزیک را بنویس")
        else:
            send_message(chat_id, "🎵 در حال ساخت موزیک...")
            audio = ai_music(prompt)
            send_audio(chat_id, audio)
        return {"ok": True}

    reply = ai_chat(text)
    send_message(chat_id, reply)
    return {"ok": True}

# ================== تست ==================
@app.route("/", methods=["GET"])
def index():
    return "Bot running ✅"

# ================== اجرا ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)