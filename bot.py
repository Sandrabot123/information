import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------------
# CONFIG
# ---------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN environment variable set!")

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

# Add the command handler
application.add_handler(CommandHandler("start", start))

# ---------------------
# WEBHOOK ROUTE
# ---------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    # Get incoming update from Telegram
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    
    # Process the update asynchronously
    asyncio.run(application.process_update(update))
    return "ok"

# ---------------------
# HOME ROUTE (test)
# ---------------------
@app.route("/")
def home():
    return "Bot is running!"

# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    # Run Flask on Render's port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
