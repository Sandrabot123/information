import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get token from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")

# Set up Flask app
app = Flask(__name__)

# Set up the bot
BOT = Bot(token=TELEGRAM_TOKEN)
APPLICATION = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! This is your bot. Send /weather to get the weather.")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Replace with your actual weather logic
    await update.message.reply_text("Weather feature is coming soon!")

APPLICATION.add_handler(CommandHandler("start", start))
APPLICATION.add_handler(CommandHandler("weather", weather))

# Webhook route — must match your full token URL
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), BOT)
    # Dispatch the update to your handlers
    APPLICATION.update_queue.put_nowait(update)
    return "OK"

if __name__ == "__main__":
    # Use your Render URL for webhook
    webhook_url = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"
    BOT.set_webhook(webhook_url)
    
    # Run Flask on port 10000 for Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
