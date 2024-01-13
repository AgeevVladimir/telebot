import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

import responses as responses
from Utils import constants as keys

# Define the keyboard layout
keyboard = [['📊 День', '📊 Неделя', '📊 Месяц', '📊 Год'],
            ['❌ Отмена', '🛒 Продукты', '👶 Дети', '🚇 Транспорт'],
            ['💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда жилья', '🎢 Развлечения'],
            ['🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Дом, ремонт'],
            ['🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']]

reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def send_daily_notification(context: CallbackContext):
    # Get the chat ID (replace CHAT_ID with the actual chat ID)
    chat_id = -4148217207
    # Send the notification
    context.bot.send_message(chat_id=chat_id, text="🕗 День подходит к концу, не забудьте внести расходы")


def start(update, context):
    update.message.reply_text("Bot started! Daily notifications will be sent at 8 PM.")


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    response = responses.sample_responses(text)
    update.message.reply_text(response, reply_markup=reply_markup)


def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher
    print('Bot started')

    # Add handlers for the commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()

    # Schedule the daily notification job at 8 PM
    job_queue = updater.job_queue
    job_queue.run_daily(send_daily_notification, time=datetime.time(20, 00), days=(0, 1, 2, 3, 4, 5, 6))

    updater.idle()


if __name__ == "__main__":
    main()
