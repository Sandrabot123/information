import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

# --------------------------
# CONFIGURATION
# --------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")  # Get from https://openweathermap.org/api
if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Set TELEGRAM_TOKEN and WEATHER_API_KEY in Render environment variables")

WEBHOOK_URL = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"

BOT = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# --------------------------
# TELEGRAM HANDLERS
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Use /weather <city> to get weather info.")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a city, e.g., /weather London")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        if res.get("cod") != 200:
            await update.message.reply_text(f"City not found: {city}")
            return
        weather_desc = res["weather"][0]["description"]
        temp = res["main"]["temp"]
        await update.message.reply_text(f"Weather in {city}:\n{weather_desc}, {temp}°C")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# --------------------------
# SETUP BOT APPLICATION
# --------------------------
async def setup():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))

    await BOT.set_webhook(WEBHOOK_URL)

    async def handle_updates():
        while True:
            update = await application.update_queue.get()
            await application.process_update(update)

    asyncio.create_task(handle_updates())

# --------------------------
# FLASK WEBHOOK ROUTE
# --------------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), BOT)
    asyncio.create_task(APP_BOT.update_queue.put(update))
    return "OK", 200

# --------------------------
# RUN EVERYTHING
# --------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(setup())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
