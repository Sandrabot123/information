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

# ---------------------
# WEATHER FUNCTIONS
# ---------------------
def get_weather(city: str, day: str = "today"):
    city = city.strip()

    # Step 1: Geocoding (get lat/lon for any city)
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
    geo_resp = requests.get(geo_url, timeout=10).json()
    if not geo_resp:
        return None
    lat = geo_resp[0]["lat"]
    lon = geo_resp[0]["lon"]
    city_name = geo_resp[0]["name"]
    country = geo_resp[0]["country"]

    if day == "today":
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10).json()
        if resp.get("cod") != 200:
            return None
        temp = resp["main"]["temp"]
        desc = resp["weather"][0]["description"]
        humidity = resp["main"]["humidity"]
        return f"🌤 Weather in {city_name}, {country} today:\nTemperature: {temp}°C\nDescription: {desc}\nHumidity: {humidity}%"
    else:
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=10).json()
        if resp.get("cod") != "200":
            return None
        tomorrow_forecast = resp["list"][8]  # ~24h later
        temp = tomorrow_forecast["main"]["temp"]
        desc = tomorrow_forecast["weather"][0]["description"]
        return f"🌦 Weather in {city_name}, {country} tomorrow:\nTemperature: {temp}°C\nDescription: {desc}"

# ---------------------
# MESSAGE HANDLER
# ---------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    # Only process messages that contain 'weather'
    if "weather" not in text:
        return  # ignore other messages

    day = "today"
    if "tomorrow" in text:
        day = "tomorrow"
        text = text.replace("tomorrow", "")
    elif "today" in text:
        text = text.replace("today", "")

    # Extract city
    city = text.replace("weather", "").replace("forecast", "").strip()
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
# MAIN (for local testing)
# ---------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("weather_bot:app", host="0.0.0.0", port=port)
