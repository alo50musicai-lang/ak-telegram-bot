from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ------------------------------
#   CHATGPT HANDLER
# ------------------------------
def ai_answer(text):
    # نمونه پاسخ هوش مصنوعی – هرطور خواستی تغییر بدم
    return f"پاسخ هوش مصنوعی: {text}"

# ------------------------------
#   تلگرام هندلرها
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋 من ربات هوش مصنوعی هستم.\nهمه‌چیز می‌سازم: چت، عکس، موزیک، ویدیو 😊")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # پاسخ هوش مصنوعی
    reply = ai_answer(user_text)

    await update.message.reply_text(reply)


# ------------------------------
#   ساخت Bot + Webhook
# ------------------------------
application = Application.builder().token(TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT, message_handler))

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    application.update_queue.put(update)
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
