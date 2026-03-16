from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests

TOKEN = "7303835691:AAGFigl28bU-UeeII5eDb2nvwMEt15ObyUc"
WEATHER_API_KEY = "be2d3cb02e4949a6ba7152141261603 "

# Map OpenWeather icons to emojis
weather_emojis = {
    "Thunderstorm": "⛈️",
    "Drizzle": "🌦️",
    "Rain": "🌧️",
    "Snow": "❄️",
    "Clear": "☀️",
    "Clouds": "☁️",
    "Mist": "🌫️",
    "Smoke": "🌫️",
    "Haze": "🌫️",
    "Dust": "🌫️",
    "Fog": "🌫️",
    "Sand": "🌫️",
    "Ash": "🌋",
    "Squall": "🌬️",
    "Tornado": "🌪️"
}

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /weather <city> <today|tomorrow>")
        return

    city = context.args[0]
    day = context.args[1].lower()

    # Step 1: Get city coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
    geo_resp = requests.get(geo_url).json()
    if not geo_resp:
        await update.message.reply_text("City not found!")
        return

    lat = geo_resp[0]['lat']
    lon = geo_resp[0]['lon']

    if day == "today":
        # Current weather
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        w = requests.get(weather_url).json()
        temp = w['main']['temp']
        condition = w['weather'][0]['main']
        desc = w['weather'][0]['description'].capitalize()
        emoji = weather_emojis.get(condition, "")
        await update.message.reply_text(
            f"🌆 Weather in {city.capitalize()} today:\n{emoji} {desc}\n🌡 Temperature: {temp}°C"
        )

    elif day == "tomorrow":
        # One Call API for tomorrow
        weather_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={WEATHER_API_KEY}&units=metric"
        w = requests.get(weather_url).json()
        tomorrow = w['daily'][1]  # index 1 is tomorrow
        temp_day = tomorrow['temp']['day']
        temp_min = tomorrow['temp']['min']
        temp_max = tomorrow['temp']['max']
        condition = tomorrow['weather'][0]['main']
        desc = tomorrow['weather'][0]['description'].capitalize()
        emoji = weather_emojis.get(condition, "")
        await update.message.reply_text(
            f"🌆 Weather in {city.capitalize()} tomorrow:\n{emoji} {desc}\n"
            f"🌡 Temperature: {temp_day}°C (min: {temp_min}°C, max: {temp_max}°C)"
        )

    else:
        await update.message.reply_text("Please choose 'today' or 'tomorrow'.")

# Setup bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("weather", weather))

app.run_polling()
