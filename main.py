from flask import Flask, request
import requests
import os
import re

# ================== تنظیمات ==================
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set in Render Environment Variables")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# ================== توابع تلگرام ==================
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )

# ================== تشخیص زبان ==================
def detect_language(text):
    if re.search(r'[\u0600-\u06FF]', text):
        return "fa_or_ar"
    if re.search(r'[a-zA-Z]', text):
        return "en"
    return "fa"

# ================== پاسخ هوشمند ==================
def ai_chat(text):
    lang = detect_language(text)

    if lang == "en":
        return "Hello 👋\nThis is an English response."
    elif lang == "fa_or_ar":
        if any(word in text for word in ["مرحبا", "كيف", "أهلا"]):
            return "مرحباً 👋\nهذا رد باللغة العربية."
        else:
            return "سلام 😊\nاین پاسخ به زبان فارسی است."
    else:
        return "سلام 👋"

# ================== Webhook ==================
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    if not update or "message" not in update:
        return {"ok": True}

    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🤖 ربات فعال شد ✅\n\n"
            "هرچی بنویسی، به همون زبان جواب می‌دم:\n"
            "🇮🇷 فارسی\n"
            "🇸🇦 عربی\n"
            "🇬🇧 انگلیسی"
        )
        return {"ok": True}

    reply = ai_chat(text)
    send_message(chat_id, reply)
    return {"ok": True}

# ================== تست ==================
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

# ================== اجرا ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)