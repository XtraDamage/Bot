import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токены (на Render мы их добавим в панели управления)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "user", "content": update.message.text}]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            data = response.json()
            answer = data['choices'][0]['message']['content']
            await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Бот временно приуныл. Попробуй позже.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        logger.error("Забыли добавить TELEGRAM_TOKEN в Environment Variables!")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        logger.info("Бот запущен на Render!")
        app.run_polling()