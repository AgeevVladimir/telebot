import openAI
import spendings

categories = ['🛒 Продукты', '👶 Дети', '🚇 Транспорт',
              '💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда жилья', '🎢 Развлечения',
              '🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Дом, ремонт',
              '🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']


def sample_responses(user_message):
    if user_message[0].isdigit():
        return spendings.save_spending(user_message)

    if user_message in "❌ Отмена":
        return spendings.delete_last_spending()

    if user_message in categories:
        return spendings.update_last_spending_category(user_message)

    if user_message.startswith('📊'):
        return spendings.get_report(user_message)

    # Подключение к ChatGPT

    if user_message.startswith("chatgpt"):
        return openAI.getChatGPTanswer(user_message)

    return "I don't understand you"
