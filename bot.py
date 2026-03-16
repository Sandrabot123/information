from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = 7303835691:AAGFigl28bU-UeeII5eDb2nvwMEt15ObyUc

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! My bot works!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
