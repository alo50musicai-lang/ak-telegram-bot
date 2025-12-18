from flask import Flask, request
import requests, os
from gtts import gTTS
import uuid

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

def send_audio(chat_id, file_path):
    with open(file_path, "rb") as f:
        requests.post(
            f"{TELEGRAM_API}/sendAudio",
            data={"chat_id": chat_id},
            files={"audio": f}
        )

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_message(
            chat_id,
            "🎵 ربات موزیک فعال شد\n\n"
            "مثال:\n"
            "/music آهنگ شاد محلی\n"
            "/music لالایی آرام"
        )
        return "ok"

    if text.startswith("/music"):
        prompt = text.replace("/music", "").strip()
        if not prompt:
            send_message(chat_id, "❌ توضیح موزیک را بنویس")
            return "ok"

        send_message(chat_id, "🎧 در حال ساخت فایل صوتی...")

        filename = f"/tmp/{uuid.uuid4()}.mp3"
        tts = gTTS(
            text=f"این یک نمونه صوتی برای موزیک با حال و هوای {prompt} است",
            lang="fa"
        )
        tts.save(filename)

        send_audio(chat_id, filename)
        return "ok"

    send_message(chat_id, "❓ از دستور /music استفاده کن")
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot running ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)