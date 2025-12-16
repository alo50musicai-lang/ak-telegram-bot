from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ← مهم

app = Flask(__name__)

# ------------------ handlers ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 ربات با وبهوک فعاله ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# ------------------ telegram app ------------------
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ------------------ routes ------------------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK", 200

# ------------------ startup ------------------
async def on_startup():
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    main()
    