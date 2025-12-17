from flask import Flask, request
import requests
import os
from openai import OpenAI
from gtts import gTTS
import base64
import time

# ---------- تنظیمات ----------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")  # Hugging Face Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ---------- توابع تلگرام ----------
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_photo(chat_id, photo_path, caption=None):
    files = {"photo": open(photo_path, "rb")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(f"{TELEGRAM_API}/sendPhoto", files=files, data=data)

def send_audio(chat_id, audio_path):
    files = {"audio": open(audio_path, "rb")}
    data = {"chat_id": chat_id}
    requests.post(f"{TELEGRAM_API}/sendAudio", files=files, data=data)

# ---------- هوش مصنوعی ----------
def ai_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ---------- تصویر با HuggingFace ----------
def hf_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return None
    result = response.json()
    if isinstance(result, list) and "generated_image" in result[0]:
        img_b64 = result[0]["generated_image"]
        with open("temp.png", "wb") as f:
            f.write(base64.b64decode(img_b64))
        return "temp.png"
    return None

# ---------- موزیک با HuggingFace MusicGen ----------
def hf_music(prompt):
    url = "https://api-inference.huggingface.co/models/suno/musicgen-small"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return None
    result = response.json()
    if "generated_audio" in result:
        audio_b64 = result["generated_audio"]
        with open("music.mp3", "wb") as f:
            f.write(base64.b64decode(audio_b64))
        return "music.mp3"
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
        send_message(chat_id, "🤖 سلام!\nدستورها:\n1️⃣ چت\n2️⃣ /image توضیح عکس\n3️⃣ /music توضیح موزیک")
        return {"ok": True}

    # تصویر
    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح عکس را بنویسید")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            img_path = hf_image(prompt)
            if img_path:
                send_photo(chat_id, img_path, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # موزیک
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح موزیک را بنویسید")
        else:
            send_message(chat_id, "🎵 در حال ساخت موزیک...")
            audio_path = hf_music(prompt)
            if audio_path:
                send_audio(chat_id, audio_path)
            else:
                send_message(chat_id, "❌ خطا در ساخت موزیک")
        return {"ok": True}

    # چت هوشمند
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