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

# Allowed chat ID - bot will only respond in this chat
ALLOWED_CHAT_ID = 106709724

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
        if update.effective_chat.id != ALLOWED_CHAT_ID:
            logger.warning(f"Rejected start command from chat {update.effective_chat.id}")
            return
        
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
        # Check if message is from allowed chat
        if update.effective_chat.id != ALLOWED_CHAT_ID:
            logger.warning(f"Rejected message from chat {update.effective_chat.id}")
            return
        
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
    """Handle errors - log them but don't crash the bot"""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    if update and update.effective_user:
        logger.error(f"Error for user {update.effective_user.id}")
    # Try to send error message to user
    if update and update.message:
        try:
            await update.message.reply_text("Sorry, an error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")


async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command for adding expenses in groups"""
    try:
        # Check if message is from allowed chat
        if update.effective_chat.id != ALLOWED_CHAT_ID:
            logger.warning(f"Rejected add command from chat {update.effective_chat.id}")
            return
        
        if not update.message or not context.args:
            try:
                await update.message.reply_text("Usage: /add <amount> <description>\nExample: /add 25.50 coffee")
            except Exception as e:
                logger.error(f"Error sending usage message in add_expense: {e}")
            return
        
        text = ' '.join(context.args)
        try:
            response = responses.sample_responses(text)
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(response, reply_markup=reply_markup)
            logger.info(f"Added expense via command from user {update.effective_user.id}: {text}")
        except Exception as response_error:
            logger.error(f"Error processing expense in add_expense: {response_error}", exc_info=True)
            try:
                await update.message.reply_text(f"Error adding expense: {str(response_error)[:80]}")
            except Exception as e:
                logger.error(f"Error sending error message in add_expense: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in add_expense command: {e}", exc_info=True)
        try:
            await update.message.reply_text("Sorry, an unexpected error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error reply in add_expense: {send_error}")


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command for getting reports in groups"""
    try:
        # Check if message is from allowed chat
        if update.effective_chat.id != ALLOWED_CHAT_ID:
            logger.warning(f"Rejected report command from chat {update.effective_chat.id}")
            return
        
        if not context.args:
            try:
                await update.message.reply_text("Usage: /report <type>\nTypes: day, week, month, year\nExample: /report day")
            except Exception as e:
                logger.error(f"Error sending usage message in report: {e}")
            return
        
        report_type = context.args[0].lower()
        try:
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
        except Exception as response_error:
            logger.error(f"Error processing report in report: {response_error}", exc_info=True)
            try:
                await update.message.reply_text(f"Error getting report: {str(response_error)[:80]}")
            except Exception as e:
                logger.error(f"Error sending error message in report: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in report command: {e}", exc_info=True)
        try:
            await update.message.reply_text("Sorry, an unexpected error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error reply in report: {send_error}")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command for checking total balance in groups"""
    try:
        # Check if message is from allowed chat
        if update.effective_chat.id != ALLOWED_CHAT_ID:
            logger.warning(f"Rejected balance command from chat {update.effective_chat.id}")
            return
        
        text = '💰💰💰  Сколько у нас всего денег 💰💰💰'
        try:
            response = responses.sample_responses(text)
            await update.message.reply_text(response)
            logger.info(f"Checked balance via command from user {update.effective_user.id}")
        except Exception as response_error:
            logger.error(f"Error processing balance in balance: {response_error}", exc_info=True)
            try:
                await update.message.reply_text(f"Error getting balance: {str(response_error)[:80]}")
            except Exception as e:
                logger.error(f"Error sending error message in balance: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in balance command: {e}", exc_info=True)
        try:
            await update.message.reply_text("Sorry, an unexpected error occurred. Please try again.")
        except Exception as send_error:
            logger.error(f"Error sending error reply in balance: {send_error}")


def main():
    """Main function with restart capability"""
    
    # Validate API key
    if not hasattr(keys, 'API_KEY') or not keys.API_KEY:
        logger.error("API_KEY not found in constants.py")
        return
    
    try:
        logger.info("Bot startup")
        application = Application.builder().token(keys.API_KEY).build()
        logger.info('Bot application built successfully')

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add", add_expense))
        application.add_handler(CommandHandler("report", report))
        application.add_handler(CommandHandler("balance", balance))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error)

        logger.info('Bot started and polling...')
        
        # Run polling
        application.run_polling(allowed_updates=[])
        
    except Exception as e:
        logger.critical(f"Bot crashed with error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
