import pandas as pd
from datetime import datetime

def saveSpending(text):
    # Split the text into amount and description
    amount, description = text.split(maxsplit=1)

    # Get the current date, year, and month
    current_date = datetime.now().strftime("%d")
    current_year = datetime.now().strftime("%Y")
    current_month = datetime.now().strftime("%m %B").lower()

    # Load the existing Excel file or create a new DataFrame if the file does not exist
    try:
        with pd.ExcelFile('spendings.xlsx') as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['year', 'month', 'date', 'sum', 'comment', 'category'])

    # Append the new data
    new_data = pd.DataFrame({
        'year': [current_year],
        'month': [current_month],
        'date': [current_date],
        'sum': [amount],
        'comment': [description],
        'category': ['']
    })

    df = pd.concat([df, new_data], ignore_index=True)

    # Save back to the Excel file
    with pd.ExcelWriter('spendings.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    return "Saved"

# Example usage
print(saveSpending("10 coffee"))
