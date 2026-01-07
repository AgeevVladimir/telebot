import openAI
import spendings

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
            result, row_number = spendings.save_spending(line)
            if "saved" in result.lower():
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
                results.append(f"✅ {line}: {result}")
            else:
                results.append(f"❌ {line}: {result}")
        except Exception as e:
            results.append(f"❌ {line}: Error - {str(e)}")
    
    summary = f"📊 Processed {successful_count}/{len([l for l in expense_lines if l.strip()])} expenses"
    if total_amount > 0:
        summary += f" (Total: {total_amount:.2f})"
    
    # If we have pending expenses, start category assignment
    if pending_expenses:
        summary += f"\n\n🎯 Now let's assign categories. First expense: '{pending_expenses[0][0]}'\nPlease select a category:"
    
    return summary + "\n\n" + "\n".join(results)


def sample_responses(user_message):
    global pending_expenses
    
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

    if user_message[0].isdigit():
        return spendings.save_spending(user_message)

    if user_message in "❌ Отмена":
        return spendings.delete_last_spending()

    if user_message in categories:
        return spendings.update_last_spending_category(user_message)

    if user_message.startswith('📊'):
        return spendings.get_report(user_message)

    if user_message.startswith('💰💰💰  Сколько у нас всего денег 💰💰💰'):
        return spendings.get_total_amount()

    # Подключение к ChatGPT
    if user_message.lower().startswith("chatgpt"):
        return openAI.getChatGPTanswer(user_message)

    return "I don't understand you. Try:\n• Record single expense: '25.99 coffee'\n• Record multiple expenses (with category assignment):\n  55 аренда\n  35 перевод папе\n  56 продукты\n• Use keyboard buttons for reports\n• Send 'chatgpt <question>' for AI help."