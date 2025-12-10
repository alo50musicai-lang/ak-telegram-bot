import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, webhook

# دریافت توکن‌ها از Environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL سرویس Render، مثل https://your-bot.onrender.com/

# دستورات ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات هوش مصنوعی آماده است.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = " ".join(context.args)
    if not msg:
        await update.message.reply_text("لطفاً پیامی بنویسید.")
        return
    headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
    data = {"model": "gpt-3.5-turbo", "messages":[{"role":"user","content": msg}]}
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        answer = resp.json()['choices'][0]['message']['content']
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"خطا در ارتباط با OpenAI: {e}")

async def img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("لطفاً توضیح تصویر را بنویسید.")
        return
    headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
    json_data = {"inputs": prompt}
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4",
            headers=headers,
            json=json_data
        )
        image_bytes = response.content
        await update.message.reply_photo(photo=image_bytes)
    except Exception as e:
        await update.message.reply_text(f"خطا در تولید تصویر: {e}")

# ساخت اپلیکیشن Webhook
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("chat", chat))
app.add_handler(CommandHandler("img", img))

# فعال کردن Webhook
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # پورت Render
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    )
    print("Bot started via Webhook")
