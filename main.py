from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import asyncio

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# -------------------------
# پاسخ مصنوعی نمونه
# -------------------------
def ai_answer(text):
    return f"پاسخ هوش مصنوعی: {text}"

# -------------------------
#  HANDLERS
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات فعال شد ✔")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    answer = ai_answer(user_text)
    await update.message.reply_text(answer)

# -------------------------
#  ساخت Bot (بدون اجرا)
# -------------------------
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# -------------------------
#  Flask routes
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    # ارسال مستقیم آپدیت به Application
    await application.process_update(update)

    return "OK", 200

# -------------------------
# اجرای Flask فقط
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
