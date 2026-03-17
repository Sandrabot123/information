import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------ CONFIG ------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")  # e.g., https://mybot.onrender.com

if not TELEGRAM_TOKEN or not WEATHER_API_KEY or not RENDER_EXTERNAL_URL:
    raise ValueError("Please set TELEGRAM_TOKEN, WEATHER_API_KEY, and RENDER_EXTERNAL_URL as environment variables")

BOT = Bot(token=TELEGRAM_TOKEN)
APP = Flask(__name__)

# ------------------ TELEGRAM HANDLERS ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send /weather <city> to get weather info.")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a city name, e.g., /weather London")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            await update.message.reply_text(f"Error: {data.get('message', 'City not found')}")
            return

        weather_desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]

        message = f"Weather in {city}:\nCondition: {weather_desc}\nTemperature: {temp}°C\nHumidity: {humidity}%"
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error fetching weather: {e}")

# ------------------ SET UP APPLICATION ------------------
APP_BOT = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
APP_BOT.add_handler(CommandHandler("start", start))
APP_BOT.add_handler(CommandHandler("weather", weather))

# ------------------ FLASK WEBHOOK ------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), BOT)
    # Use the application object to process update
    APP_BOT.update_queue.put(update)
    return "OK"

@app.route("/")
def home():
    return "Bot is running!"

# ------------------ RUN ON RENDER ------------------
if __name__ == "__main__":
    webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
    BOT.set_webhook(webhook_url)

    port = int(os.environ.get("PORT", 10000))
    APP.run(host="0.0.0.0", port=port)
