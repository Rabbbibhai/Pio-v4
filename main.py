import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, CommandHandler
from gtts import gTTS
from io import BytesIO
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_URL = os.getenv("APP_URL")  # Example: https://pio-v4.onrender.com
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আসসালামু আলাইকুম! আপুনি কেমনে আছেন?")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    sylheti_prompt = f"User: {user_message}\nBot (in Sylheti Bangla, friendly and feminine tone):"

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": sylheti_prompt}]
        }
    )

    try:
        reply_text = response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        reply_text = "মাফ করবেন, কিছু একটা সমস্যা হইছে।"

    await update.message.reply_text(reply_text)

    # Voice generation
    tts = gTTS(reply_text, lang="bn", tld="co.in")
    voice_fp = BytesIO()
    tts.write_to_fp(voice_fp)
    voice_fp.seek(0)

    await update.message.reply_voice(voice_fp)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", start))
application.add_handler(CommandHandler("hello", start))
application.add_handler(CommandHandler("chat", reply))
application.add_handler(CommandHandler("", reply))
application.add_handler(CommandHandler("message", reply))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

async def setup_webhook():
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{APP_URL}/{TOKEN}")

if __name__ == "__main__":
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
