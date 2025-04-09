import os
import requests
from flask import Flask, request, send_file
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from gtts import gTTS

TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! আমি পিও। কিতা লাগি কইও, আমি সহায় করতে রেডি আছি।")

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openrouter/openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Respond in Sylheti Bangla as a supportive female therapist friend."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()
        ai_reply = res.json()["choices"][0]["message"]["content"]

        # Send text reply
        await update.message.reply_text(ai_reply)

        # Generate feminine Bangla voice reply
        tts = gTTS(ai_reply, lang='bn', tld='com')  # feminine tone with 'com' TLD
        voice_path = f"voice_{update.effective_user.id}.mp3"
        tts.save(voice_path)

        # Send voice reply
        with open(voice_path, "rb") as voice:
            await update.message.reply_voice(voice)

        os.remove(voice_path)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("দুঃখিত, কিছু সমস্যা হয়েছে। পরে আবার চেষ্টা করুন।")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

@app.route("/")
def index():
    return "Pio bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put(update)
    return "OK"

if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
