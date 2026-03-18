import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN set")

app = Flask(__name__)

# Create Telegram application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("START command received")
    await update.message.reply_text("Hello! Your bot is working ✅")

# Add handlers
application.add_handler(CommandHandler("start", start))


# --- WEBHOOK ROUTE ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    # Run async handler manually
    asyncio.run(application.process_update(update))

    return "ok"


# --- HOME ROUTE (for testing) ---
@app.route("/")
def home():
    return "Bot is running!"


# --- MAIN ---
if __name__ == "__main__":
    # IMPORTANT: DO NOT set webhook here (causes warning)
    # Set it manually once (see below)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
