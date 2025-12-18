from flask import Flask, request
import requests
import os

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")  # توکن HuggingFace برای تصویر

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

# ---------- هوش مصنوعی (چت ساده) ----------
def ai_chat(prompt):
    # تشخیص زبان برای پیام‌ها
    if any("\u0600" <= c <= "\u06FF" for c in prompt):
        return "سلام 😊 این پاسخ به زبان فارسی است."  # برای فارسی و عربی
    elif any("\u0621" <= c <= "\u064A" for c in prompt):
        return "مرحباً 👋 هذا الرد باللغة العربية."
    else:
        return "Hello 👋 This reply is in English."

# ---------- ساخت تصویر با HuggingFace ----------
def ai_image(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    json_data = {"inputs": prompt}
    response = requests.post(
        "https://api-inference.huggingface.co/models/hogiahien/counterfeit-v30-edited",
        headers=headers,
        json=json_data
    )
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and "generated_image_url" in data[0]:
            return data[0]["generated_image_url"]
        elif isinstance(data, dict) and "error" in data:
            return None
        else:
            return None
    else:
        return None

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
            "1️⃣ فقط پیام بفرست (چت)\n"
            "2️⃣ تصویر: /image توضیح"
        )
        return {"ok": True}

    # ساخت تصویر
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح عکس را بنویسید")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            url = ai_image(prompt)
            if url:
                send_photo(chat_id, url, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
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