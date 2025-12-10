# main.py
import os
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات هوش مصنوعی آماده است.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("لطفاً پیامی بنویسید.")
        return
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {"model": "gpt-3.5-turbo", "messages":[{"role":"user","content": msg}]}
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    answer = resp.json()['choices'][0]['message']['content']
    await update.message.reply_text(answer)

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("لطفاً توضیح تصویر را بنویسید.")
        return
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    json_data = {"inputs": prompt}
    response = requests.post("https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4", headers=headers, json=json_data)
    image_bytes = response.content
    await update.message.reply_photo(photo=image_bytes)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", chat))
    app.add_handler(CommandHandler("img", img))
    print("Bot started")
    app.run_polling()
