from flask import Flask, request
from telegram import Bot
import os

app = Flask(__name__)

# توکن ربات رو از Environment Variable بگیر
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(TOKEN)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    if "message" in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text == "/start":
            bot.send_message(chat_id=chat_id, text="سلام! ربات فعال شد ✅")
        else:
            bot.send_message(chat_id=chat_id, text=f"پیام شما: {text}")

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Telegram bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)