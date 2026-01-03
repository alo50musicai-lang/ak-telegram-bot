from flask import Flask, request
import requests
import os
import random

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

TG = f"https://api.telegram.org/bot{BOT_TOKEN}"
HF_API = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

# ---------- ابزار ----------
def send_message(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(f"{TG}/sendMessage", json=payload)

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

def menu_keyboard():
    return {
        "keyboard": [
            ["🖼 ساخت تصویر", "🎵 موزیک واقعی"],
            ["💬 چت", "🫥 گـفتگو"]
        ],
        "resize_keyboard": True
    }

# ---------- تصویر ----------
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

# ---------- زبان ----------
def detect_lang(text):
    for c in text:
        if '\u0600' <= c <= '\u06FF':
            return "fa"
    return "en"

# ---------- Webhook ----------
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return {"ok": True}

    msg = data["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "🤖 خوش آمدی!\nیکی از گزینه‌ها را انتخاب کن:",
            menu_keyboard()
        )
        return {"ok": True}

    # --- دکمه تصویر ---
    if text == "🖼 ساخت تصویر":
        send_message(chat_id, "✍️ توضیح تصویر را بنویس")
        return {"ok": True}

    # --- دکمه موزیک ---
    if text == "🎵 موزیک واقعی":
        music_files = os.listdir("music")
        song = random.choice(music_files)
        send_audio(chat_id, f"music/{song}")
        return {"ok": True}

    # --- چت ---
    if text == "💬 چت":
        send_message(chat_id, "هر چی دوست داری بنویس 😊")
        return {"ok": True}

  # --- گفتگو---
    if text == "🫥 گفتگو":
        send_message(chat_id, "هر چی دوست داری بگو 😊")
        return {"ok": True}

    # --- ساخت تصویر با متن ---
    if "تصویر" in text or "image" in text:
        send_message(chat_id, "🎨 در حال ساخت تصویر...")
        img = make_image(text)
        if img:
            send_photo(chat_id, img)
        else:
            send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # --- پاسخ چت ---
    lang = detect_lang(text)
    if lang == "fa":
        send_message(chat_id, f"گفتی: «{text}»\nمن شنیدم 🙂")
    else:
        send_message(chat_id, f"You said: {text}")

    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "Bot is running ✅"