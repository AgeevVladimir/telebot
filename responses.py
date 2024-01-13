from datetime import datetime

import openAI
import spendings

categories = ['🛒 Продукты', '👶 Дети', '🚇 Транспорт',
              '💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда жилья', '🎢 Развлечения',
              '🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Дом, ремонт',
              '🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']


def sample_responses(user_message):
    if user_message in ("hi", "hello"):
        return "Hey! How is it going?"

    if user_message in "who are you":
        return "I'm MyFinance1514_bot"

    if user_message in "time":
        now = datetime.now()
        date_time = now.strftime("%d/%m/%y, %H:%M:%S")
        return str(date_time)

    # Handle sum and category

    if user_message[0].isdigit():
        return spendings.saveSpending(user_message)

    if user_message in "❌ Отмена":
        return spendings.deleteLastSpending()

    if user_message in categories:
        return spendings.updateLastSpendingCategory(user_message)

    if user_message.startswith('📊'):
        return spendings.getReport(user_message)

    # Подключение к ChatGPT

    if user_message.startswith("chatgpt"):
        return openAI.getChatGPTanswer(user_message)

    return "I don't understand you"
