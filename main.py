from flask import Flask, request
import requests
import os
import base64
import uuid

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_API_TOKEN")

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"
HEADERS_HF = {"Authorization": f"Bearer {HF_TOKEN}"}

app = Flask(__name__)
TMP_DIR = "/tmp"  # رندر اجازه نوشتن در این مسیر را دارد

# ---------- توابع تلگرام ----------
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_photo_file(chat_id, file_path, caption=None):
    with open(file_path, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        requests.post(f"{TELEGRAM_API}/sendPhoto", data=data, files=files)

def send_audio_file(chat_id, file_path, caption=None):
    with open(file_path, "rb") as f:
        files = {"audio": f}
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        requests.post(f"{TELEGRAM_API}/sendAudio", data=data, files=files)

# ---------- هوش مصنوعی چت ----------
def ai_chat(prompt):
    url = "https://api-inference.huggingface.co/models/gpt2"
    payload = {"inputs": prompt}
    r = requests.post(url, headers=HEADERS_HF, json=payload)
    if r.status_code == 200:
        resp = r.json()
        if isinstance(resp, list) and "generated_text" in resp[0]:
            return resp[0]["generated_text"]
        return str(resp)
    else:
        return "❌ خطا در تولید پاسخ"

# ---------- هوش مصنوعی تصویر ----------
def ai_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    payload = {"inputs": prompt}
    r = requests.post(url, headers=HEADERS_HF, json=payload)
    if r.status_code == 200:
        data = r.json()
        # اگر Base64 برگردد
        if isinstance(data, list) and "generated_image" in data[0]:
            img_b64 = data[0]["generated_image"]
            file_path = f"{TMP_DIR}/{uuid.uuid4().hex}.png"
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            return file_path
    return None

# ---------- هوش مصنوعی موزیک ----------
def ai_music(prompt):
    url = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    payload = {"inputs": prompt}
    r = requests.post(url, headers=HEADERS_HF, json=payload)
    if r.status_code == 200:
        data = r.json()
        # اگر Base64 برگردد
        if isinstance(data, dict) and "generated_audio" in data:
            audio_b64 = data["generated_audio"]
            file_path = f"{TMP_DIR}/{uuid.uuid4().hex}.mp3"
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            return file_path
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
            send_message(chat_id, "❌ توضیح عکس را بنویس")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            file_path = ai_image(prompt)
            if file_path:
                send_photo_file(chat_id, file_path, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    # ساخت موزیک
    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ سبک موزیک را بنویس")
        else:
            send_message(chat_id, "🎵 در حال ساخت موزیک...")
            file_path = ai_music(prompt)
            if file_path:
                send_audio_file(chat_id, file_path, "موزیک ساخته شد ✅")
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