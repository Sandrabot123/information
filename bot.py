import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ------------------ CONFIG ------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Please set TELEGRAM_TOKEN and WEATHER_API_KEY as environment variables")

WEBHOOK_URL = f"https://information-jgk7.onrender.com/{TELEGRAM_TOKEN}"

# ------------------ FLASK APP ------------------
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Receive updates from Telegram."""
    update_json = request.get_json(force=True)
    update = Update.de_json(update_json, bot)
    asyncio.run(app_bot.update_queue.put(update))
    return "OK"

# ------------------ TELEGRAM BOT ------------------
bot = Bot(token=TELEGRAM_TOKEN)

app_bot = ApplicationBuilder().bot(bot).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send /weather <city> to get weather info."
    )

# /weather command
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a city, e.g., /weather London")
        return

    city = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

    try:
        import requests
        res = requests.get(url).json()

        if res.get("cod") != 200:
            await update.message.reply_text(f"Error: {res.get('message', 'City not found')}")
            return

        weather_desc = res["weather"][0]["description"].title()
        temp = res["main"]["temp"]
        humidity = res["main"]["humidity"]

        await update.message.reply_text(
            f"Weather in {city}:\nCondition: {weather_desc}\nTemperature: {temp}°C\nHumidity: {humidity}%"
        )
    except Exception as e:
        await update.message.reply_text(f"Error fetching weather: {e}")

# Add handlers
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("weather", weather))

# ------------------ SET WEBHOOK ------------------
bot.set_webhook(WEBHOOK_URL)
print(f"Webhook set to {WEBHOOK_URL}")

# ------------------ RUN FLASK ------------------
if __name__ == "__main__":
    # Run the Telegram bot queue
    asyncio.get_event_loop().create_task(app_bot.start())
    
    # Run Flask server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
