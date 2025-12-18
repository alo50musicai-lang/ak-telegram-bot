from flask import Flask, request
import requests
import os
from gtts import gTTS
import uuid

# -------- تنظیمات --------
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

TG = f"https://api.telegram.org/bot{BOT_TOKEN}"
HF_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

app = Flask(__name__)

# -------- ابزار --------
def send_message(chat_id, text):
    requests.post(f"{TG}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, img):
    requests.post(
        f"{TG}/sendPhoto",
        data={"chat_id": chat_id},
        files={"photo": img}
    )

def send_audio(chat_id, path):
    with open(path, "rb") as f:
        requests.post(
            f"{TG}/sendAudio",
            data={"chat_id": chat_id},
            files={"audio": f}
        )

def detect_lang(text):
    for c in text:
        if '\u0600' <= c <= '\u06FF':
            return "fa"
    if any(c.isalpha() for c in text):
        return "en"
    return "fa"

# -------- تصویر --------
def make_image(prompt):
    r = requests.post(
        HF_API,
        headers={"Authorization": f"Bearer {HF_TOKEN}"},
        json={"inputs": prompt},
        timeout=60
    )
    if r.status_code == 200:
        return r.content
    return None

# -------- صدا --------
def make_voice(text, lang):
    tts = gTTS(
        text=text,
        lang="fa" if lang == "fa" else "en",
        slow=False
    )
    path = f"/tmp/{uuid.uuid4()}.mp3"
    tts.save(path)
    return path

# -------- webhook --------
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    if text == "/start":
        send_message(chat_id,
            "🤖 ربات آماده است\n"
            "🖼 بنویس: تصویر یک گربه\n"
            "🎵 بنویس: صدا بساز\n"
            "💬 هر چیز دیگر = چت"
        )
        return {"ok": True}

    lang = detect_lang(text)

    # --- تصویر ---
    if "تصویر" in text or "image" in text:
        send_message(chat_id, "🎨 در حال ساخت تصویر...")
        img = make_image(text)
        if img:
            send_photo(chat_id, img)
        else:
            send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # --- صدا ---
    if "صدا" in text or "voice" in text:
        reply = {
            "fa": "این یک نمونه صدای فارسی است",
            "en": "This is an English voice sample"
        }[lang]
        path = make_voice(reply, lang)
        send_audio(chat_id, path)
        return {"ok": True}

    # --- چت واقعی ---
    if lang == "fa":
        send_message(chat_id, f"گفتی: «{text}»\nمن شنیدم 😊")
    else:
        send_message(chat_id, f"You said: {text}")

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "Bot running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))