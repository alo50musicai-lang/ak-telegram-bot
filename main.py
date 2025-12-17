from flask import Flask, request
import os
import requests
import openai

# ====== تنظیمات ======
app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ====== توابع تلگرام ======
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def send_photo(chat_id, photo_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, json={"chat_id": chat_id, "photo": photo_url})

# ====== هوش مصنوعی ======
def ai_chat(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "تو یک دستیار فارسی هستی و با لحن دوستانه پاسخ بده."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def ai_image(prompt):
    result = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return result["data"][0]["url"]

# ====== موزیک (ساده، لینک آماده) ======
def ai_music(prompt):
    # اینجا برای مبتدی‌ها فقط لینک می‌دهیم
    # بعداً می‌توان API Suno یا Replicate اضافه کرد
    return f"https://example.com/music/{prompt.replace(' ', '_')}.mp3"

# ====== مسیر اصلی وب‌هوک ======
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text.startswith("/start"):
            send_message(chat_id,
            "🤖 ربات هوش مصنوعی فعال شد ✅\n\n"
            "/chat متن → چت هوشمند\n"
            "/img توضیح → ساخت تصویر\n"
            "/music توضیح → ساخت موزیک"
            )
        elif text.startswith("/chat"):
            prompt = text.replace("/chat", "").strip()
            answer = ai_chat(prompt)
            send_message(chat_id, answer)
        elif text.startswith("/img"):
            prompt = text.replace("/img", "").strip()
            img_url = ai_image(prompt)
            send_photo(chat_id, img_url)
        elif text.startswith("/music"):
            prompt = text.replace("/music", "").strip()
            music_link = ai_music(prompt)
            send_message(chat_id, f"🎵 موزیک آماده است: {music_link}")
        else:
            send_message(chat_id, "دستور نامعتبر است. /start را بزنید.")

    return "ok", 200

# ====== اجرای سرور ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))