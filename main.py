from flask import Flask, request
import requests
import os
from openai import OpenAI  # برای چت
import json

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")  # توکن HuggingFace شما

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
HF_API_URL = "https://api-inference.huggingface.co/models/hogiahien/counterfeit-v30-edited"  # مدل تصویرسازی رایگان مثال

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


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
    # تشخیص زبان
    lang = "fa"  # پیشفرض فارسی
    if any(c.isalpha() for c in prompt):
        if all(ord(c) < 128 for c in prompt):  # انگلیسی
            lang = "en"
        elif any('\u0600' <= c <= '\u06FF' for c in prompt):  # عربی
            lang = "ar"
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = response.choices[0].message.content
    return reply


def ai_image(prompt):
    # درخواست به HuggingFace
    payload = {"inputs": prompt}
    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    try:
        data = response.json()
        # اگر لینک مستقیم بود
        if isinstance(data, dict) and "image_url" in data:
            return data["image_url"]
        # اگر Base64 داده بود، ذخیره و ارسال
        if isinstance(data, list) and "generated_image" in data[0]:
            return data[0]["generated_image"]
    except Exception as e:
        print("❌ خطا در ساخت تصویر:", e)
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
            "1️⃣ چت: فقط پیام بفرست\n"
            "2️⃣ عکس: /image توضیح\n"
            "3️⃣ موزیک: /music توضیح"
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

    # موزیک (فعلاً شبیه‌سازی)
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        send_message(
            chat_id,
            "🎵 ساخت موزیک هوش مصنوعی:\n\n"
            f"سبک درخواستی: {prompt}\n\n"
            "❗ فعلاً نسخه نمایشی است"
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