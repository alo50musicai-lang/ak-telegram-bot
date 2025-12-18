from flask import Flask, request
import requests
import os
from openai import OpenAI

# ================= ENV =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ================= TELEGRAM =================
def send_message(chat_id, text):
    requests.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url, caption=None):
    requests.post(f"{TG_API}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    })

# ================= LANGUAGE AUTO =================
def detect_language(text):
    for c in text:
        if "\u0600" <= c <= "\u06FF":
            return "fa"
        if "a" <= c.lower() <= "z":
            return "en"
    return "fa"

# ================= CHAT =================
def ai_chat(prompt):
    lang = detect_language(prompt)
    system = {
        "fa": "فقط فارسی پاسخ بده",
        "en": "Reply only in English",
        "ar": "أجب باللغة العربية فقط"
    }[lang]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# ================= IMAGE (REAL & FREE) =================
def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    return url

# ================= WEBHOOK =================
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if text == "/start":
        send_message(chat_id,
            "🤖 ربات آماده است\n\n"
            "🖼 تصویر: تصویر یک گربه روی دیوار\n"
            "💬 چت: هرچی خواستی بنویس"
        )
        return "ok"

    if "تصویر" in text or "image" in text or "pic" in text:
        send_message(chat_id, "🎨 در حال ساخت تصویر...")
        img = generate_image(text)
        send_photo(chat_id, img, "✅ تصویر ساخته شد")
        return "ok"

    reply = ai_chat(text)
    send_message(chat_id, reply)
    return "ok"

# ================= TEST =================
@app.route("/", methods=["GET"])
def index():
    return "Bot running ✅"

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))