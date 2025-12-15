from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 ربات فعال شد")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/")
def home():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)

    asyncio.run(application.process_update(update))
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)