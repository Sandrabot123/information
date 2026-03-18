import os
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ---------------------
# CONFIG
# ---------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not RENDER_URL or not WEATHER_API_KEY:
    raise ValueError("TELEGRAM_TOKEN, RENDER_URL, and WEATHER_API_KEY must be set!")

# ---------------------
# FASTAPI APP
# ---------------------
app = FastAPI()

# ---------------------
# TELEGRAM BOT
# ---------------------
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I can give you the weather forecast.\n"
        "Try sending 'London weather' or 'Paris weather tomorrow'."
    )

# Weather function with auto city formatting
def get_weather(city: str, day: str = "today"):
    city = city.strip().title()  # Capitalize each word

    # Fix small countries/cities that need country codes
    city_corrections = {
        "Singapore": "Singapore,SG",
        "Hong Kong": "Hong Kong,HK",
        "Macau": "Macau,MO",
        "London": "London,GB"
    }
    city = city_corrections.get(city, city)

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
        tomorrow_forecast = response["list"][8]  # ~24h later
        temp = tomorrow_forecast["main"]["temp"]
        desc = tomorrow_forecast["weather"][0]["description"]
        return f"🌦 Weather in {city} tomorrow:\nTemperature: {temp}°C\nDescription: {desc}"

# Message handler
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

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# ---------------------
# STARTUP EVENT - initialize bot and set webhook
# ---------------------
@app.on_event("startup")
async def startup_event():
    await application.initialize()
    await application.start()

    # Set webhook
    url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={url}")
    if r.status_code == 200:
        print("Webhook set successfully ✅")
    else:
        print("Failed to set webhook:", r.text)

# ---------------------
# WEBHOOK ENDPOINT
# ---------------------
@app.post(f"/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# ---------------------
# HEALTH CHECK
# ---------------------
@app.get("/")
async def home():
    return {"status": "Bot is running!"}

# ---------------------
# MAIN (optional, for local testing)
# ---------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("weather_bot:app", host="0.0.0.0", port=port)
