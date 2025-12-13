import os
import io
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputMediaPhoto, InputMediaAudio
from huggingface_hub import InferenceApi

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# گرفتن توکن‌ها از متغیرهای محیطی Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# اتصال به مدل‌های Hugging Face
# مدل چت (متن سبک برای پاسخ‌های کوتاه)
text_model = InferenceApi(repo_id="gpt2", token=HF_TOKEN)

# مدل تصویر (نسخه سبک‌تر؛ خروجی را به بایت تبدیل می‌کنیم)
image_model = InferenceApi(repo_id="stabilityai/stable-diffusion", token=HF_TOKEN)

# مدل صوتی سبک (متن به گفتار برای دمو موزیک/ویس سبک)
# می‌توانی مدل دیگری مانند "facebook/fastspeech2-en" جایگزین کنی؛ این فقط دمو است.
tts_model = InferenceApi(repo_id="suno-ai/bark", token=HF_TOKEN)

def start(update, context):
    update.message.reply_text(
        "سلام! من ربات هوش مصنوعی هستم 🤖\n"
        "دستورات:\n"
        "/chat متن → پاسخ هوشمند\n"
        "/image توضیح عکس → ساخت تصویر کم‌حجم\n"
        "/music متن کوتاه → ساخت فایل صوتی سبک\n"
        "یا فقط متن بفرست تا جواب بدم."
    )

def chat_cmd(update, context):
    prompt = " ".join(context.args) if context.args else (update.message.text or "سلام")
    try:
        result = text_model(inputs=prompt, params={"max_new_tokens": 60})
        # برخی مدل‌ها خروجی را به شکل دیکشنری‌های مختلف می‌دهند؛ حالت عمومی:
        text = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
        if not text.strip():
            text = "نتونستم پاسخی بسازم؛ یه متن کوتاه‌تر بفرست 🙂"
        update.message.reply_text(text[:1000])
    except Exception as e:
        logger.exception(e)
        update.message.reply_text("اشکالی پیش اومد. لطفاً دوباره امتحان کن.")

def chat_auto(update, context):
    # پاسخ خودکار برای هر متن غیر دستوری
    chat_cmd(update, context)

def image_cmd(update, context):
    prompt = " ".join(context.args) if context.args else "a simple scenic landscape, low detail"
    try:
        # ساخت تصویر؛ برخی مدل‌ها خروجی bytes می‌دهند
        img_bytes = image_model(inputs=prompt)
        if isinstance(img_bytes, (bytes, bytearray)):
            bio = io.BytesIO(img_bytes)
            bio.name = "image.jpg"
            bio.seek(0)
            # کاهش حجم: تلگرام خودش فشرده می‌کند؛ می‌توانی اندازه مدل یا کیفیت را پایین نگه داری
            update.message.reply_photo(photo=bio, caption="✅ تصویر آماده شد.")
        else:
            # اگر لینک یا شیء دیگری برگشت
            update.message.reply_text(f"نتیجه تصویر: {str(img_bytes)[:500]}")
    except Exception as e:
        logger.exception(e)
        update.message.reply_text("ساخت تصویر ناموفق بود. یک توضیح کوتاه‌تر و ساده‌تر بده.")

def music_cmd(update, context):
    text = " ".join(context.args) if context.args else "hello world"
    try:
        # برای کم‌حجم بودن: متن کوتاه بده و مدت را محدود نگه دار
        audio_bytes = tts_model(inputs=text)
        if isinstance(audio_bytes, (bytes, bytearray)):
            bio = io.BytesIO(audio_bytes)
            bio.name = "voice.wav"  # یا .mp3 اگر مدل خروجی mp3 بدهد
            bio.seek(0)
            update.message.reply_audio(audio=bio, caption="✅ فایل صوتی سبک آماده شد.")
        else:
            update.message.reply_text(f"نتیجه صوت: {str(audio_bytes)[:500]}")
    except Exception as e:
        logger.exception(e)
        update.message.reply_text("ساخت صوت ناموفق بود. یک متن کوتاه‌تر امتحان کن.")

def main():
    if not TELEGRAM_TOKEN or not HF_TOKEN:
        raise RuntimeError("توکن‌ها تنظیم نشده‌اند. Environment Variables را در Render اضافه کن.")

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # دستورات
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("chat", chat_cmd))
    dp.add_handler(CommandHandler("image", image_cmd))
    dp.add_handler(CommandHandler("music", music_cmd))

    # پاسخ خودکار به هر متن
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_auto))

    # اجرا با polling (برای Worker در Render مناسب است)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
