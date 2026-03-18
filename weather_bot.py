import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I can give you the weather forecast.\n"
        "Try sending 'London weather' or 'Paris weather tomorrow'."
    )

def get_weather(city: str, day: str = "today"):
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
        tomorrow_forecast = response["list"][8]
        temp = tomorrow_forecast["main"]["temp"]
        desc = tomorrow_forecast["weather"][0]["description"]
        return f"🌦 Weather in {city} tomorrow:\nTemperature: {temp}°C\nDescription: {desc}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    day = "today"
    if "tomorrow" in text:
        day = "tomorrow"

    city = text.replace("weather", "").replace("forecast", "").replace("today", "").replace("tomorrow", "").strip()
    if not city:
        await update.message.reply_text("❗ Please provide a city, e.g., 'London weather tomorrow'")
        return

    weather_msg = get_weather(city, day)
    if weather_msg:
        await update.message.reply_text(weather_msg)
    else:
        await update.message.reply_text(f"❌ City '{city}' not found. Try again.")

def main():
    if not TELEGRAM_BOT_TOKEN or not WEATHER_API_KEY:
        print("ERROR: Missing TELEGRAM_TOKEN or WEATHER_API_KEY environment variables!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🌐 Weather bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
