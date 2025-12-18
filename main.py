from flask import Flask, request
import requests
import os
import base64

# ---------- تنظیمات ----------
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

app = Flask(__name__)
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# ---------- توابع تلگرام ----------
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_photo(chat_id, file_path, caption=None):
    files = {"photo": open(file_path, "rb")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    requests.post(f"{TELEGRAM_API}/sendPhoto", data=data, files=files)

# ---------- ساخت تصویر ----------
def generate_image(prompt):
    HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
        data = response.json()

        if isinstance(data, dict) and "error" in data:
            print("❌ خطا:", data["error"])
            return None

        image_base64 = data[0]["image_base64"]
        image_bytes = base64.b64decode(image_base64)
        filename = "temp_image.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        return filename
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

    if text == "/start":
        send_message(chat_id, "🤖 سلام!\nبرای ساخت تصویر، بنویس:\n/image توضیح تصویر")
        return {"ok": True}

    if text.startswith("/image"):
        prompt = text.replace("/image", "").strip()
        if not prompt:
            send_message(chat_id, "❌ لطفاً توضیح تصویر را بنویسید")
        else:
            send_message(chat_id, "🎨 در حال ساخت تصویر...")
            filename = generate_image(prompt)
            if filename:
                send_photo(chat_id, filename, "تصویر ساخته شد ✅")
            else:
                send_message(chat_id, "❌ خطا در ساخت تصویر")
        return {"ok": True}

    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅"

# ---------- اجرا ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)