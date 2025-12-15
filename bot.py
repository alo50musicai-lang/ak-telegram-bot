import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات - فقط همین خط رو تغییر بده!
TOKEN = "توکن_رباتت_را_اینجا_بنویس"

async def start(update: Update, context):
    """دستور /start"""
    await update.message.reply_text(
        "🎉 سلام! ربات فعال شد!\n"
        "هر پیامی بفرستی برمی‌گردونم\n"
        "دستورات:\n"
        "/start - شروع\n"
        "/help - راهنما"
    )

async def help_command(update: Update, context):
    """دستور /help"""
    await update.message.reply_text("💡 راهنما: فقط پیام بفرست، جواب میدم!")

async def echo(update: Update, context):
    """جواب دادن به پیام‌های کاربر"""
    user_text = update.message.text
    await update.message.reply_text(f"📨 شما گفتید: {user_text}")

def main():
    """تابع اصلی"""
    print("🤖 در حال راه‌اندازی ربات...")
    
    # ساخت اپلیکیشن
    app = Application.builder().token(TOKEN).build()
    
    # اضافه کردن دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # اضافه کردن هندلر برای پیام‌های معمولی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("✅ ربات فعال شد!")
    print("📱 به تلگرام برو و با رباتت چت کن...")
    
    # شروع ربات
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()