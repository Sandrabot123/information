import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get your API keys from environment variables
TELEGRAM_TOKEN = os.getenv("7303835691:AAGFigl28bU-UeeII5eDb2nvwMEt15ObyUc")  # Your bot token
WEATHER_API_KEY = os.getenv("be2d3cb02e4949a6ba7152141261603 ")  # OpenWeatherMap API key

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and WEATHER_API_KEY as environment variables")

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

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))

    print("Bot is running...")
    app.run_polling()
