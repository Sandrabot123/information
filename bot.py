import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------ CONFIG ------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and WEATHER_API_KEY")

WEBHOOK_URL = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"

# ------------------ FLASK ------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ------------------ TELEGRAM ------------------
bot = Bot(token=TELEGRAM_TOKEN)
app_bot = ApplicationBuilder().bot(bot).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send /weather <city>")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /weather <city>")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        import requests
        data = requests.get(url).json()

        if data.get("cod") != 200:
            await update.message.reply_text("City not found")
            return

        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]

        await update.message.reply_text(f"{city}: {desc}, {temp}°C")

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Add handlers
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("weather", weather))

# ------------------ WEBHOOK ------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)

    # ✅ FIXED: properly handle async queue
    asyncio.get_event_loop().create_task(
        app_bot.update_queue.put(update)
    )

    return "OK"

# ------------------ STARTUP ------------------
async def init_bot():
    await app_bot.initialize()
    await app_bot.start()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook set to {WEBHOOK_URL}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_bot())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
