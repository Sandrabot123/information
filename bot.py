import os
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get your API keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and WEATHER_API_KEY as environment variables")

# ------------------ FLASK PART ------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ------------------ TELEGRAM BOT ------------------
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

def run_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("weather", weather))

    print("Bot is running...")
    app_bot.run_polling()

# ------------------ RUN BOTH ------------------
if __name__ == "__main__":
    # Run bot in background thread
    threading.Thread(target=run_bot).start()

    # Start Flask (for Render port)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
