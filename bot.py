import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# ---------------------
# CONFIG
# ---------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN environment variable set!")

RENDER_URL = os.environ.get("RENDER_URL")
if not RENDER_URL:
    raise ValueError("No RENDER_URL environment variable set! Example: https://your-app.onrender.com")

# ---------------------
# FLASK APP
# ---------------------
app = Flask(__name__)

# ---------------------
# TELEGRAM BOT
# ---------------------
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is running ✅")

application.add_handler(CommandHandler("start", start))

# Optional: Echo handler to test messages
from telegram.ext import MessageHandler, filters
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Got your message: {update.message.text}")

application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

# ---------------------
# WEBHOOK ROUTE
# ---------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    """Receive Telegram updates via webhook."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    # Run async handler synchronously
    asyncio.run(application.process_update(update))
    return "ok"

# Health check
@app.route("/")
def home():
    return "Bot is running!"

# ---------------------
# AUTO-SET TELEGRAM WEBHOOK
# ---------------------
def set_webhook():
    url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={url}")
    if r.status_code == 200:
        print("Webhook set successfully ✅")
    else:
        print("Failed to set webhook:", r.text)

# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
