import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz

import responses as responses
from Utils import constants as keys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define the keyboard layout
keyboard = [['💰💰💰  Сколько у нас всего денег 💰💰💰'],
            ['📊 День', '📊 Неделя', '📊 Месяц', '📊 Год'],
            ['❌ Отмена', '🛒 Продукты', '👶 Дети', '🚇 Транспорт'],
            ['💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда', '🎢 Развлечения'],
            ['🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Ремонт'],
            ['🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message:
            logger.warning("Received start command without message")
            return
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Bot started! Daily notifications will be sent at 8 PM.", reply_markup=reply_markup)
        logger.info(f"Bot started for user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in start command: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            logger.warning("Received message without text")
            return
        
        text = update.message.text.strip()
        if not text:
            await update.message.reply_text("Please send a valid message.")
            return
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        response = responses.sample_responses(text)
        await update.message.reply_text(response, reply_markup=reply_markup)
        logger.info(f"Handled message from user {update.effective_user.id}: {text[:50]}...")
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        try:
            await update.message.reply_text("Sorry, an error occurred. Please try again.")
        except:
            pass


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_user:
        logger.error(f"Error for user {update.effective_user.id}")


def main():
    try:
        # Validate API key
        if not hasattr(keys, 'API_KEY') or not keys.API_KEY:
            logger.error("API_KEY not found in constants.py")
            return
        
        application = Application.builder().token(keys.API_KEY).job_queue(None).build()
        logger.info('Bot application built successfully')

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error)

        logger.info('Bot started and polling...')
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        return


if __name__ == "__main__":
    main()
