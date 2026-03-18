import os
import requests
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Load your environment variables
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # set your bot token too

def get_weather(city: str, day: str = "today"):
    """Fetch weather info for today or tomorrow using OpenWeatherMap"""
    city = city.strip()
    if day == "today":
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != 200:
            return None
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        humidity = response["main"]["humidity"]
        return f"🌤 Weather in {city} today:\nTemperature: {temp}°C\nDescription: {desc}\nHumidity: {humidity}%"
    else:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") != "200":
            return None
        # forecast ~24h later (8 * 3h intervals)
        tomorrow_forecast = response["list"][8]
        temp = tomorrow_forecast["main"]["temp"]
        desc = tomorrow_forecast["weather"][0]["description"]
        return f"🌦 Weather in {city} tomorrow:\nTemperature: {temp}°C\nDescription: {desc}"

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    day = "today"
    if "tomorrow" in text:
        day = "tomorrow"

    # Extract city name by removing keywords
    city = text.replace("weather", "").replace("forecast", "").replace("today", "").replace("tomorrow", "").strip()
    if not city:
        update.message.reply_text("❗ Please provide a city, e.g., 'London weather tomorrow'")
        return

    weather_msg = get_weather(city, day)
    if weather_msg:
        update.message.reply_text(weather_msg)
    else:
        update.message.reply_text(f"❌ City '{city}' not found. Try again.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("🌐 Weather bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
