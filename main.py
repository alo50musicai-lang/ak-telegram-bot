from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# -------------------------
# پاسخ نمونه هوش مصنوعی
# -------------------------
def ai_answer(text):
    return f"پاسخ هوش مصنوعی: {text}"

# -------------------------
# Handlers
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋 ربات با موفقیت فعال شد ✅")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    reply = ai_answer(text)
    await update.message.reply_text(reply)

# -------------------------
# main
# -------------------------
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot started...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())