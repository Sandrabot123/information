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

    # prevent crash if message is None
    if update.message:
        await update.message.reply_text("Hello! Your bot is working ✅")


# Add handlers
application.add_handler(CommandHandler("start", start))


# --- WEBHOOK ROUTE ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        print("INCOMING:", data)  # 👈 DEBUG

        update = Update.de_json(data, application.bot)

        asyncio.run(application.process_update(update))

    except Exception as e:
        import traceback
        print("ERROR OCCURRED:")
        traceback.print_exc()  # 👈 VERY IMPORTANT

    return "ok"


# --- HOME ROUTE ---
@app.route("/")
def home():
    return "Bot is running!"


# --- MAIN ---
if __name__ == "__main__":
    # 🔥 IMPORTANT: initialize the bot (this was missing before)
    asyncio.run(application.initialize())

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
