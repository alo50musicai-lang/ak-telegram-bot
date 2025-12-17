from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

# ---------------- handlers ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 ربات فعاله")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# ---------------- application ----------------
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ---------------- routes ----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    print("POST received!")
    data = request.get_json(force=True)
    print(data)
    return "ok"

# ---------------- run ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)