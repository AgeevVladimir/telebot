import logging
import spendings

logger = logging.getLogger(__name__)

categories = ['🛒 Продукты', '👶 Дети', '🚇 Транспорт',
              '💊 Здоровье', '🍔 Еда вне дома', '🏠 Аренда', '🎢 Развлечения',
              '🎁 Подарки', '👕 Шоппинг', '🐈‍⬛ Котики', '🏡 Ремонт',
              '🌐 Сервисы', '📚 Образование', '✈️ Путешествия', '🌎 Прочее']

pending_expenses = []  # List of tuples: (expense_text, row_number)


def process_multiple_expenses(expense_lines):
    """Process multiple expense lines, save them, and queue for category assignment."""
    global pending_expenses
    results = []
    total_amount = 0.0
    successful_count = 0
    
    # Clear any previous pending expenses
    pending_expenses.clear()
    
    for line in expense_lines:
        line = line.strip()
        if not line:
            continue
            
        try:
            result = spendings.save_spending(line)
            # Handle both tuple and string returns for backward compatibility
            if isinstance(result, tuple):
                msg, row_number = result
            else:
                msg = result
                row_number = None
            
            if "saved" in msg.lower() and row_number is not None:
                successful_count += 1
                # Extract amount from the line for total calculation
                parts = line.split()
                if parts:
                    try:
                        amount = float(parts[0])
                        total_amount += amount
                        # Add to pending expenses for category assignment with row number
                        pending_expenses.append((line, row_number))
                    except ValueError:
                        pass
                results.append(f"✅ {line}: {msg}")
            else:
                results.append(f"❌ {line}: {msg}")
        except Exception as e:
            logger.error(f"Error processing line in process_multiple_expenses: {line} - {e}", exc_info=True)
            results.append(f"❌ {line}: Error - {str(e)}")
    
    summary = f"📊 Processed {successful_count}/{len([l for l in expense_lines if l.strip()])} expenses"
    if total_amount > 0:
        summary += f" (Total: {total_amount:.2f})"
    
    # If we have pending expenses, start category assignment
    if pending_expenses:
        summary += f"\n\n🎯 Now let's assign categories. First expense: '{pending_expenses[0][0]}'\nPlease select a category:"
    
    return summary + "\n\n" + "\n".join(results)


def sample_responses(user_message):
    """
    Process user message and return appropriate response.
    Handles spending tracking, reports, and AI queries.
    """
    global pending_expenses
    
    try:
        if not user_message or not isinstance(user_message, str):
            logger.warning("Invalid user message received")
            return "Please send a valid text message."
        
        user_message = user_message.strip()
        if not user_message:
            return "Please send a non-empty message."
        
        # Check for multi-row expenses (multiple lines, each starting with digit)
        lines = [line.strip() for line in user_message.split('\n') if line.strip()]
        if len(lines) > 1 and all(line[0].isdigit() for line in lines):
            return process_multiple_expenses(lines)

        # Handle category selection for pending expenses
        if pending_expenses and user_message in categories:
            # Get the first pending expense (expense_text, row_number)
            expense_text, row_number = pending_expenses[0]
            # Assign category to the specific row
            result = spendings.update_spending_category(user_message, row_number)
            # Remove the processed expense from pending list
            pending_expenses.pop(0)
            
            if pending_expenses:
                # More expenses to categorize
                next_expense_text, _ = pending_expenses[0]
                return f"✅ Category '{user_message}' assigned to '{expense_text}'\n\n🎯 Next expense: '{next_expense_text}'\nPlease select a category:"
            else:
                # All expenses categorized
                return f"✅ Category '{user_message}' assigned to '{expense_text}'\n\n🎉 All expenses have been categorized!"

        # Check for spending input (starts with digit)
        if user_message and user_message[0].isdigit():
            try:
                result = spendings.save_spending(user_message)
                # Handle both tuple and string returns
                if isinstance(result, tuple):
                    return result[0]
                return result
            except Exception as e:
                logger.error(f"Error saving spending: {e}", exc_info=True)
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
        
        logger.info(f"Unrecognized message: {user_message[:50]}...")
        return "I don't understand you. Try:\n• Record single expense: '25.99 coffee'\n• Record multiple expenses (with category assignment):\n  55 аренда\n  35 перевод папе\n  56 продукты\n• Use keyboard buttons for reports."
    
    except Exception as e:
        logger.error(f"Unexpected error in sample_responses: {e}")
        return "An unexpected error occurred. Please try again."
