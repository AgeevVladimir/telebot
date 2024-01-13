from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler

from datetime import datetime

import responses as responses
from Utils import constants as keys

# Define the keyboard layout
keyboard = [['📊 День', '📊 Неделя', '📊 Категории за месяц', '📊 Категории за год'],
            ['❌ Отмена', '🛒 Продукты', '👶 Дети', '🚇 Транспорт'],
            ['💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда жилья', '🎢 Развлечения'],
            ['🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Дом, ремонт'],
            ['🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']]

reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    response = responses.sample_responses(text)

    # Send the response along with the keyboard
    update.message.reply_text(response, reply_markup=reply_markup)


def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher
    print('Bot started')

    # Add handlers for the commands
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
