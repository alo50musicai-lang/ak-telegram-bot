import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
HUGGINGFACE_KEY = os.environ.get("HUGGINGFACE_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثلا https://akbot.onrender.com

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات روشن شد ✔️")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        return await update.message.reply_text("پیام بعد /chat بنویس.")

    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role":"user", "content": text}]
    }

    try:
        r = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        msg = r.json()['choices'][0]['message']['content']
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(str(e))

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        return await update.message.reply_text("توضیح تصویر بعد /img بنویس.")

    try:
        r = requests.post(
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
            headers={"Authorization": f"Bearer {HUGGINGFACE_KEY}"},
            json={"inputs": prompt}
        )
        await update.message.reply_photo(photo=r.content)
    except Exception as e:
        await update.message.reply_text(str(e))

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", chat))
    app.add_handler(CommandHandler("img", img))

    port = int(os.environ.get("PORT", 10000))

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )
