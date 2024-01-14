from datetime import datetime, timedelta
import pandas as pd

FILE_NAME = 'spendings.xlsx'
CURRENCY = '€'

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


def get_current_date():
    current_date = datetime.now()
    return {
        'day': current_date.strftime('%d.%m.%Y'),
        'year': current_date.strftime('%Y'),
        'month': current_date.strftime('%m %B').lower()
    }


def load_spending_data():
    try:
        df = pd.read_excel(FILE_NAME, sheet_name='Sheet1')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['year', 'month', 'date', 'sum', 'comment', 'category'])
    return df


def save_spending(text):
    amount, description = text.split(maxsplit=1)
    current_date = get_current_date()

    df = load_spending_data()
    new_data = pd.DataFrame({
        'year': [current_date['year']],
        'month': [current_date['month']],
        'date': [current_date['day']],
        'sum': [amount],
        'comment': [description],
        'category': ['']
    })

    df = pd.concat([df, new_data], ignore_index=True)
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    return "Don't forget to choose Category"


def delete_last_spending():
    df = load_spending_data()
    if not df.empty:
        df = df.drop(df.index[-1])
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        return "Last spending deleted"
    else:
        return "No spending to delete"


def update_last_spending_category(text):
    df = load_spending_data()
    if not df.empty:
        df.at[df.index[-1], 'category'] = text
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        return "Category updated for the last spending"
    else:
        return "No spending to update"


def get_report(text):
    df = load_spending_data()
    current_date = get_current_date()

    if text == '📊 День':
        today_report = df[(df['date'] == current_date['day']) &
                          (df['month'].str.contains(current_date['month'])) &
                          (df['year'] == int(current_date['year']))]
        return format_report(today_report, CURRENCY)

    elif text == '📊 Неделя':
        df['date'] = pd.to_datetime(df['date'], format="%d.%m.%Y", dayfirst=True)
        start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_report = df[(df['date'] >= start_of_week.strftime("%Y.%m.%d")) &
                         (df['date'] <= end_of_week.strftime("%Y.%m.%d"))]
        return format_report(week_report, CURRENCY)

    elif text == '📊 Месяц':
        category_month_report = df[(df['month'].str.contains(current_date['month'])) &
                                   (df['year'] == int(current_date['year']))]
        df_excluded_sum = category_month_report.drop(columns=['date']).groupby(
            'category').sum().reset_index()
        return format_month_report(df_excluded_sum, CURRENCY)

    elif text == '📊 Год':
        category_year_report = df[df['year'] == int(current_date['year'])]
        df_excluded_sum = category_year_report.drop(columns=['date']).groupby(
            'category').sum().reset_index()
        return format_year_report(df_excluded_sum, CURRENCY)

    else:
        return "Invalid report type"


def format_report(report_df, currency):
    formatted_report = ""
    total_sum = 0

    for _, row in report_df.iterrows():
        day_abbreviation = get_day_abbreviation(pd.to_datetime(row['date']).strftime('%A'))
        formatted_report += f"{day_abbreviation}. {row['category']:<10} {currency}{row['sum']:<4} {row['comment']}\n"
        total_sum += row['sum']

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def format_month_report(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y.%m")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += row['sum']

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def format_year_report(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += row['sum']

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()
