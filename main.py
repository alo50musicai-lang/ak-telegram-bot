from flask import Flask, request
import os
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL رندر تو

# Route اصلی webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    print("POST received!\n", update)

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")

        # پاسخ ساده
        send_message(chat_id, f"پیام شما دریافت شد: {text}")

    return "OK", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# صفحه اصلی فقط برای تست
@app.route('/')
def index():
    return "Bot is running ✅", 200

if __name__ == "__main__":
    # برای تست محلی
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))