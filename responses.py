import logging
import openAI
import spendings

logger = logging.getLogger(__name__)

categories = ['🛒 Продукты', '👶 Дети', '🚇 Транспорт',
              '💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда', '🎢 Развлечения',
              '🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Ремонт',
              '🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']


def sample_responses(user_message):
    """
    Process user message and return appropriate response.
    Handles spending tracking, reports, and AI queries.
    """
    try:
        if not user_message or not isinstance(user_message, str):
            logger.warning("Invalid user message received")
            return "Please send a valid text message."
        
        user_message = user_message.strip()
        if not user_message:
            return "Please send a non-empty message."
        
        # Check for spending input (starts with digit)
        if user_message and user_message[0].isdigit():
            try:
                return spendings.save_spending(user_message)
            except Exception as e:
                logger.error(f"Error saving spending: {e}")
                return "Error saving spending. Please try again."
        
        # Check for cancel command
        if user_message == "❌ Отмена":
            try:
                return spendings.delete_last_spending()
            except Exception as e:
                logger.error(f"Error deleting spending: {e}")
                return "Error canceling last spending."
        
        # Check for category selection
        if user_message in categories:
            try:
                return spendings.update_last_spending_category(user_message)
            except Exception as e:
                logger.error(f"Error updating category: {e}")
                return "Error updating spending category."
        
        # Check for report requests
        if user_message.startswith('📊'):
            try:
                return spendings.get_report(user_message)
            except Exception as e:
                logger.error(f"Error getting report: {e}")
                return "Error generating report."
        
        # Check for total balance request
        if user_message.startswith('💰💰💰  Сколько у нас всего денег 💰💰💰'):
            try:
                return spendings.get_total_amount()
            except Exception as e:
                logger.error(f"Error getting total amount: {e}")
                return "Error retrieving total balance."
        
        # Check for AI queries
        if user_message.lower().startswith("chatgpt"):
            try:
                return openAI.getChatGPTanswer(user_message)
            except Exception as e:
                logger.error(f"Error getting AI response: {e}")
                return "Sorry, AI service is currently unavailable."
        
        logger.info(f"Unrecognized message: {user_message[:50]}...")
        return "I don't understand you. Try using the keyboard buttons or send 'chatgpt <question>' for AI help."
    
    except Exception as e:
        logger.error(f"Unexpected error in sample_responses: {e}")
        return "An unexpected error occurred. Please try again."
