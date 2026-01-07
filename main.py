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


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command for adding expenses in groups"""
    try:
        if not update.message or not context.args:
            await update.message.reply_text("Usage: /add <amount> <description>\nExample: /add 25.50 coffee")
            return
        
        text = ' '.join(context.args)
        response = responses.sample_responses(text)
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(response, reply_markup=reply_markup)
        logger.info(f"Added expense via command from user {update.effective_user.id}: {text}")
    except Exception as e:
        logger.error(f"Error in add_expense command: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command for getting reports in groups"""
    try:
        if not context.args:
            await update.message.reply_text("Usage: /report <type>\nTypes: day, week, month, year\nExample: /report day")
            return
        
        report_type = context.args[0].lower()
        if report_type == 'day':
            text = '📊 День'
        elif report_type == 'week':
            text = '📊 Неделя'
        elif report_type == 'month':
            text = '📊 Месяц'
        elif report_type == 'year':
            text = '📊 Год'
        else:
            await update.message.reply_text("Invalid report type. Use: day, week, month, or year")
            return
        
        response = responses.sample_responses(text)
        await update.message.reply_text(response)
        logger.info(f"Generated report via command from user {update.effective_user.id}: {report_type}")
    except Exception as e:
        logger.error(f"Error in report command: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command for checking total balance in groups"""
    try:
        text = '💰💰💰  Сколько у нас всего денег 💰💰💰'
        response = responses.sample_responses(text)
        await update.message.reply_text(response)
        logger.info(f"Checked balance via command from user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error in balance command: {e}")
        await update.message.reply_text("Sorry, an error occurred. Please try again.")


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
        application.add_handler(CommandHandler("add", add_expense))
        application.add_handler(CommandHandler("report", report))
        application.add_handler(CommandHandler("balance", balance))
        # Handle text messages in private chats and mentions/commands in groups
        application.add_handler(MessageHandler(
            (filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE) | 
            (filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS & filters.Mention()) |
            (filters.TEXT & ~filters.COMMAND & filters.ChatType.SUPERGROUP & filters.Mention()),
            handle_message
        ))
        application.add_error_handler(error)

        logger.info('Bot started and polling...')
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        return


if __name__ == "__main__":
    main()
