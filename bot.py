import os
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ---------------------
# CONFIG
# ---------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN environment variable set!")

RENDER_URL = os.environ.get("RENDER_URL")
if not RENDER_URL:
    raise ValueError("No RENDER_URL environment variable set! Example: https://your-app.onrender.com")

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
    await update.message.reply_text("Hello! Your bot is running ✅")

# Echo handler for testing
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Got your message: {update.message.text}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

# ---------------------
# WEBHOOK ENDPOINT
# ---------------------
@app.post(f"/{TELEGRAM_TOKEN}")
async def telegram_webhook(request: Request):
    """Receive updates from Telegram asynchronously."""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# Health check
@app.get("/")
async def home():
    return {"status": "Bot is running!"}

# ---------------------
# AUTO-SET WEBHOOK
# ---------------------
def set_webhook():
    url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={url}")
    if r.status_code == 200:
        print("Webhook set successfully ✅")
    else:
        print("Failed to set webhook:", r.text)

# ---------------------
# MAIN
# ---------------------
if __name__ == "__main__":
    import uvicorn
    set_webhook()
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("bot:app", host="0.0.0.0", port=port, log_level="info")
