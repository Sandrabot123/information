import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# ------------------ ENVIRONMENT VARIABLES ------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Set TELEGRAM_TOKEN and WEATHER_API_KEY as environment variables!")

# ------------------ FLASK SETUP ------------------
app = Flask(__name__)

# ------------------ TELEGRAM BOT SETUP ------------------
BOT = Bot(token=TELEGRAM_TOKEN)
APP_BOT = Application.builder().token(TELEGRAM_TOKEN).build()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send /weather <city> to get weather info."
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a city, e.g., /weather London")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        import requests
        data = requests.get(url).json()

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

APP_BOT.add_handler(CommandHandler("start", start))
APP_BOT.add_handler(CommandHandler("weather", weather))

# ------------------ FLASK WEBHOOK ROUTE ------------------
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), BOT)
    asyncio.create_task(APP_BOT.update_queue.put(update))  # properly schedule coroutine
    return "OK"

@app.route("/")
def index():
    return "Bot is running!"

# ------------------ SET WEBHOOK ------------------
async def set_webhook():
    url = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"
    await BOT.set_webhook(url)
    print(f"Webhook set to {url}")

# ------------------ RUN FLASK ------------------
if __name__ == "__main__":
    # Set webhook before starting Flask
    asyncio.run(set_webhook())

    # Flask must listen on Render's port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
