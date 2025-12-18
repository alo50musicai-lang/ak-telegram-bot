from flask import Flask, request
import requests
import os
from gtts import gTTS
import uuid

# ----------------- تنظیمات -----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
HF_IMAGE_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

app = Flask(__name__)

# ----------------- تشخیص زبان -----------------
def detect_lang(text):
    for c in text:
        if '\u0600' <= c <= '\u06FF':
            if 'سلام' in text:
                return "fa"
            return "ar"
    if any(c.isalpha() for c in text):
        return "en"
    return "fa"

# ----------------- تلگرام -----------------
def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(f"{TELEGRAM_API}/sendMessage", json=data)

def send_photo(chat_id, image_bytes):
    files = {"photo": image_bytes}
    data = {"chat_id": chat_id}
    requests.post(f"{TELEGRAM_API}/sendPhoto", data=data, files=files)

def send_audio(chat_id, file_path):
    with open(file_path, "rb") as f:
        files = {"audio": f}
        data = {"chat_id": chat_id}
        requests.post(f"{TELEGRAM_API}/sendAudio", data=data, files=files)

# ----------------- تصویر -----------------
def generate_image(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(
        HF_IMAGE_API,
        headers=headers,
        json={"inputs": prompt},
        timeout=60
    )
    if r.status_code == 200:
        return r.content
    return None

# ----------------- موزیک MP3 -----------------
def generate_music(text, lang):
    tts = gTTS(text=text, lang="fa" if lang == "fa" else "en")
    path = f"/tmp/{uuid.uuid4()}.mp3"
    tts.save(path)
    return path

# ----------------- منوی دکمه -----------------
def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "🎨 ساخت تصویر", "callback_data": "image"}],
            [{"text": "🎵 ساخت موزیک", "callback_data": "music"}],
            [{"text": "💬 چت", "callback_data": "chat"}]
        ]
    }

# ----------------- Webhook -----------------
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    # ---------- دکمه ----------
    if "callback_query" in update:
        q = update["callback_query"]
        chat_id = q["message"]["chat"]["id"]
        data = q["data"]

        if data == "image":
            send_message(chat_id, "✍️ بنویس:\nتصویر یک گربه روی دیوار")
        elif data == "music":
            send_message(chat_id, "✍️ بنویس:\nیک موزیک شاد بساز")
        elif data == "chat":
            send_message(chat_id, "💬 هر چی دوست داری بنویس")

        return {"ok": True}

    # ---------- پیام ----------
    if "message" not in update:
        return {"ok": True}

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "🤖 خوش اومدی!\nیکی از گزینه‌ها رو انتخاب کن:",
            main_menu()
        )
        return {"ok": True}

    lang = detect_lang(text)

    # ---------- تصویر ----------
    if "تصویر" in text or "image" in text:
        send_message(chat_id, "🎨 در حال ساخت تصویر...")
        img = generate_image(text)
        if img:
            send_photo(chat_id, img)
        else:
            send_message(chat_id, "❌ ساخت تصویر ناموفق بود (محدودیت رایگان)")
        return {"ok": True}

    # ---------- موزیک ----------
    if "موزیک" in text or "music" in text or "آهنگ" in text:
        msg = {
            "fa": "این یک نمونه موزیک صوتی است",
            "en": "This is a sample audio music",
            "ar": "هذا نموذج موسيقى صوتية"
        }[lang]
        path = generate_music(msg, lang)
        send_audio(chat_id, path)
        return {"ok": True}

    # ---------- چت ----------
    replies = {
        "fa": "سلام 😊 من اینجام",
        "en": "Hello 😊 I'm here",
        "ar": "مرحباً 😊 أنا هنا"
    }
    send_message(chat_id, replies[lang])
    return {"ok": True}

# ----------------- تست -----------------
@app.route("/", methods=["GET"])
def index():
    return "Bot running ✅"

# ----------------- اجرا -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)