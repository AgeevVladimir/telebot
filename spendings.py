from datetime import datetime, timedelta

import pandas as pd

day_abbreviations = {
    'Monday': 'пн',
    'Tuesday': 'вт',
    'Wednesday': 'ср',
    'Thursday': 'чт',
    'Friday': 'пт',
    'Saturday': 'сб',
    'Sunday': 'вс'
}


def get_day_abbreviation(day):
    return day_abbreviations.get(day, day)


def saveSpending(text):
    # Split the text into amount and description
    amount, description = text.split(maxsplit=1)

    # Get the current date, year, and month
    current_date = datetime.now().strftime("%d.%m.%Y")
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

    return "Spending saved"


def deleteLastSpending():
    try:
        # Load the existing Excel file
        with pd.ExcelFile('spendings.xlsx') as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')

        # Check if there are rows to delete
        if not df.empty:
            # Drop the last row
            df = df.drop(df.index[-1])

            # Save back to the Excel file
            with pd.ExcelWriter('spendings.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)

            return "Last spending deleted"
        else:
            return "No spending to delete"
    except FileNotFoundError:
        return "File 'spendings.xlsx' not found"


def updateLastSpendingCategory(text):
    try:
        # Load the existing Excel file
        with pd.ExcelFile('spendings.xlsx') as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')

        # Check if there are rows to update
        if not df.empty:
            # Update the 'category' field of the last row
            df.at[df.index[-1], 'category'] = text

            # Save back to the Excel file
            with pd.ExcelWriter('spendings.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)

            return "Category updated for the last spending"
        else:
            return "No spending to update"
    except FileNotFoundError:
        return "File 'spendings.xlsx' not found"


def getReport(text, currency='€'):
    try:
        # Load the existing Excel file
        with pd.ExcelFile('spendings.xlsx') as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')

        # Get the current date
        current_date = datetime.now()

        if text == '📊 День':
            # Report for today
            today_report = df[(df['date'] == datetime.now().strftime("%d.%m.%Y")) &
                              (df['month'].str.contains(datetime.now().strftime("%m"))) &
                              (df['year'] == int(datetime.now().strftime("%Y")))]
            return formatReport(today_report, currency)

        elif text == '📊 Неделя':

            df['date'] = pd.to_datetime(df['date'], format="%d.%m.%Y", dayfirst=True)
            start_of_week = current_date - timedelta(days=current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            week_report = df[(df['date'] >= start_of_week.strftime("%Y.%m.%d")) &
                             (df['date'] <= end_of_week.strftime("%Y.%m.%d"))]

            return formatReport(week_report, currency)

        elif text == '📊 Категории за месяц':
            # Report for the current month aggregated by categories
            category_month_report = df[(df['month'].str.contains(datetime.now().strftime("%m"))) &
                                       (df['year'] == int(datetime.now().strftime("%Y")))]
            df_excluded_sum = category_month_report.drop(columns=['date']).groupby(
                'category').sum().reset_index()
            return formatMonthReport(df_excluded_sum, currency)

        elif text == '📊 Категории за год':
            # Report for the current month aggregated by categories
            category_year_report = df[df['year'] == int(datetime.now().strftime("%Y"))]
            df_excluded_sum = category_year_report.drop(columns=['date']).groupby(
                'category').sum().reset_index()
            return formatYearReport(df_excluded_sum, currency)

        else:
            return "Invalid report type"

    except FileNotFoundError:
        return "File 'spendings.xlsx' not found"


def formatReport(report_df, currency):
    formatted_report = ""
    report_df.loc[:, 'date'] = pd.to_datetime(report_df['date'], format='%d.%m.%Y', dayfirst=True)
    total_sum = 0

    for _, row in report_df.iterrows():
        day_abbreviation = get_day_abbreviation(row['date'].strftime('%A'))
        formatted_report += f"{day_abbreviation}. {row['category']:<10} {currency}{row['sum']:<4} {row['comment']}\n"
        total_sum += row['sum']  # Accumulate total sum

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def formatMonthReport(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y.%m")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += row['sum']

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def formatYearReport(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += row['sum']  # Accumulate total sum

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()
