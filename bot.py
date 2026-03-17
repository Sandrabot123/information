import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# ------------------ CONFIG ------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Missing environment variables")

WEBHOOK_URL = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"

# ------------------ INIT ------------------
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# ------------------ COMMANDS ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send /weather <city>")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /weather <city>")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        data = requests.get(url).json()

        if data.get("cod") != 200:
            await update.message.reply_text("City not found")
            return

        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        await update.message.reply_text(f"{city}: {desc}, {temp}°C")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("weather", weather))

# ------------------ WEBHOOK ------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)

        # 🔥 CRITICAL FIX: use existing loop safely
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        loop.close()

        return "OK"
    except Exception as e:
        print("ERROR:", e)  # 👈 THIS WILL SHOW REAL ERROR IN LOGS
        return "ERROR", 500

@app.route("/")
def home():
    return "Bot is running!"

# ------------------ START ------------------
async def setup():
    await application.initialize()
    await application.start()
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set:", WEBHOOK_URL)

if __name__ == "__main__":
    asyncio.run(setup())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
