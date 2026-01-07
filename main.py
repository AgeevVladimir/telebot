import logging
import asyncio
import time
import signal
import socket
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pytz

import responses as responses
from Utils import constants as keys

# Set socket timeout globally to prevent hanging on API calls
socket.setdefaulttimeout(30)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Allowed chat IDs - bot will respond in these chats only
ALLOWED_CHAT_IDS = [
    106709724,      # Your private chat with bot
    -4148217207     # Group chat with your wife
]

# Define the keyboard layout
keyboard = [['💰💰💰  Сколько у нас всего денег 💰💰💰'],
            ['📊 День', '📊 Неделя', '📊 Месяц', '📊 Год'],
            ['❌ Отмена', '🛒 Продукты', '👶 Дети', '🚇 Транспорт'],
            ['💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда', '🎢 Развлечения'],
            ['🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Ремонт'],
            ['🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if message is from allowed chat
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            logger.warning(f"Rejected start command from unauthorized chat {update.effective_chat.id}")
            return
        
        if not update.message:
            logger.warning("Received start command without message")
            return
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        chat_type = "group" if update.effective_chat.id < 0 else "private chat"
        await update.message.reply_text(f"Bot started in {chat_type}! Ready to track expenses.", reply_markup=reply_markup)
        logger.info(f"Bot started for user {update.effective_user.id} in chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Error in start command: {e}", exc_info=True)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if message is from allowed chat
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            logger.warning(f"Rejected message from unauthorized chat {update.effective_chat.id}")
            return
        
        if not update.message or not update.message.text:
            logger.warning("Received message without text")
            return
        
        text = update.message.text.strip()
        if not text:
            await update.message.reply_text("Please send a valid message.")
            return
        
        logger.info(f"Processing message from chat {update.effective_chat.id}: {text[:50]}...")
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        response = responses.sample_responses(text)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        logger.info(f"Message processed successfully in chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Error handling message in chat {update.effective_chat.id}: {e}", exc_info=True)
        try:
            await update.message.reply_text("Sorry, an error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors - log them but don't crash the bot"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text("Sorry, an error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command for adding expenses"""
    try:
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            return
        
        if not update.message or not context.args:
            await update.message.reply_text("Usage: /add <amount> <description>\nExample: /add 25.50 coffee")
            return
        
        text = ' '.join(context.args)
        response = responses.sample_responses(text)
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(response, reply_markup=reply_markup)
        logger.info(f"Expense added via command in chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Error in add_expense: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error adding expense. Please try again.")
        except:
            pass


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command for getting reports"""
    try:
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /report <type>\nTypes: day, week, month, year")
            return
        
        report_type = context.args[0].lower()
        report_map = {'day': '📊 День', 'week': '📊 Неделя', 'month': '📊 Месяц', 'year': '📊 Год'}
        
        if report_type not in report_map:
            await update.message.reply_text("Invalid report type. Use: day, week, month, or year")
            return
        
        response = responses.sample_responses(report_map[report_type])
        await update.message.reply_text(response)
        logger.info(f"Report generated in chat {update.effective_chat.id}: {report_type}")
    except Exception as e:
        logger.error(f"Error in report: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error generating report. Please try again.")
        except:
            pass


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command for checking total balance"""
    try:
        if update.effective_chat.id not in ALLOWED_CHAT_IDS:
            return
        
        response = responses.sample_responses('💰💰💰  Сколько у нас всего денег 💰💰💰')
        await update.message.reply_text(response)
        logger.info(f"Balance checked in chat {update.effective_chat.id}")
    except Exception as e:
        logger.error(f"Error in balance: {e}", exc_info=True)
        try:
            await update.message.reply_text("Error getting balance. Please try again.")
        except:
            pass


def main():
    """Main function to run the bot"""
    
    if not hasattr(keys, 'API_KEY') or not keys.API_KEY:
        logger.error("API_KEY not found in constants.py")
        return
    
    try:
        logger.info("Starting bot...")
        application = Application.builder().token(keys.API_KEY).build()
        logger.info('Bot application built successfully')

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add", add_expense))
        application.add_handler(CommandHandler("report", report))
        application.add_handler(CommandHandler("balance", balance))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error)

        logger.info(f'Bot ready for chats: {ALLOWED_CHAT_IDS}')
        logger.info('Starting polling...')
        
        # Run polling - this is blocking and manages its own event loop
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
