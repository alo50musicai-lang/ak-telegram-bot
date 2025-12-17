from flask import Flask, request
import requests
import os

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")  # توکن ربات تلگرام
HF_TOKEN = os.getenv("HF_TOKEN")      # توکن HuggingFace برای تصویر
HF_MODEL = "stabilityai/stable-diffusion-2-1"  # مدل رایگان تصویر

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

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

# ---------- هوش مصنوعی تصویر با HuggingFace ----------
def hf_image(prompt):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        # HF به طور مستقیم URL نمی‌ده، ولی می‌تونیم بفرستیم raw image
        image_bytes = response.content
        # ذخیره موقت روی سرور
        path = f"temp_image.png"
        with open(path, "wb") as f:
            f.write(image_bytes)
        return path
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
            "شما می‌توانید:\n"
            "1️⃣ چت: فقط پیام بفرستید\n"
            "2️⃣ عکس: /image توضیح\n"
        )
        return {"ok": True}

    # ساخت تصویر
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح عکس را بنویسید")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            image_path = hf_image(prompt)
            if image_path:
                send_photo(chat_id, open(image_path, "rb"), "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # چت ساده (فعلاً فقط پاسخ ثابت)
    send_message(chat_id, "سلام 😊 این ربات آماده ساخت تصویر است!")
    return {"ok": True}

# ---------- تست دستی ----------
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

# ---------- اجرا ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)