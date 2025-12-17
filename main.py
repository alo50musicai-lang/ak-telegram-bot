from flask import Flask, request
import requests
import os
from openai import OpenAI
import base64

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)
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

def send_audio(chat_id, audio_url, caption=None):
    data = {"chat_id": chat_id, "audio": audio_url}
    if caption:
        data["caption"] = caption
    requests.post(f"{TELEGRAM_API}/sendAudio", json=data)

# ---------- هوش مصنوعی ----------
def ai_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ---------- HuggingFace تصویر ----------
def hf_image(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    data = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        # خروجی تصویر باینری است
        img_bytes = response.content
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{img_b64}"
    else:
        return None

# ---------- HuggingFace موزیک ----------
def hf_music(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    data = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        audio_bytes = response.content
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return f"data:audio/wav;base64,{audio_b64}"
    else:
        return None

# ---------- تشخیص زبان ساده ----------
def detect_language(text):
    # چک فارسی و عربی و انگلیسی
    arabic_chars = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    persian_chars = "اآبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهي"
    if any(c in arabic_chars for c in text):
        return "ar"
    elif any(c in persian_chars for c in text):
        return "fa"
    else:
        return "en"

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
            send_message(chat_id, "❌ توضیح عکس را بنویس")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            url = hf_image(prompt)
            if url:
                send_photo(chat_id, url, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # ساخت موزیک
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ سبک یا توضیح موزیک را بنویس")
        else:
            send_message(chat_id, "🎵 در حال ساخت موزیک...")
            url = hf_music(prompt)
            if url:
                send_audio(chat_id, url, "موزیک ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت موزیک")
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