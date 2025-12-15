import os
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ.get("TOKEN")  # توکن از محیط میاد

async def start(update: Update, context):
    await update.message.reply_text("🤖 ربات فعال!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()