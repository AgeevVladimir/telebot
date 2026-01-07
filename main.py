from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import pytz

import responses as responses
from Utils import constants as keys

# Define the keyboard layout
keyboard = [['💰💰💰  Сколько у нас всего денег 💰💰💰'],
            ['📊 День', '📊 Неделя', '📊 Месяц', '📊 Год'],
            ['❌ Отмена', '🛒 Продукты', '👶 Дети', '🚇 Транспорт'],
            ['💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда', '🎢 Развлечения'],
            ['🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Ремонт'],
            ['🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']]

reply_markup = None  # Will be set in handlers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Bot started! Daily notifications will be sent at 8 PM.", reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    text = update.message.text
    response = responses.sample_responses(text)
    await update.message.reply_text(response, reply_markup=reply_markup)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


def main():
    application = Application.builder().token(keys.API_KEY).job_queue(None).build()
    print('Bot started')

    # Add handlers for the commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    application.run_polling()


if __name__ == "__main__":
    main()
