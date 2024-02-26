from datetime import datetime, timedelta

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from Utils import constants

# Constants
SPREADSHEET_ID = constants.GOOGLE_SHEET_ID
SHEET_NAME = 'Spendings'
RANGE_NAME = f'{SHEET_NAME}!A1'  # Adjust based on where you want to start reading/writing
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'Utils/google_Api.json'

# Authenticate and create the service
credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

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
        'day': current_date.strftime('%Y-%m-%d %H:%M:%S'),  # Modified to desired format
        'year': current_date.strftime('%Y'),
        'month': current_date.strftime('%m %B').lower()
    }


def load_data_from_excel():
    try:
        df = pd.read_excel(FILE_NAME, sheet_name='Sheet1')
        # Ensure the 'date' column is in the correct format if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['year', 'month', 'date', 'sum', 'comment', 'category'])
    return df


def load_data_from_google_sheets():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        # Assuming the first row is the header
        df = pd.DataFrame(values[1:], columns=values[0])
        # Convert the 'date' column to datetime
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df


def load_data_to_excel(df):
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', datetime_format='YYYY-MM-DD HH:MM:SS') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)


def save_spending(text):
    amount, description = text.split(maxsplit=1)
    current_date = get_current_date()

    df = load_data_from_excel()
    new_data = pd.DataFrame({
        'year': [current_date['year']],
        'month': [current_date['month']],
        'date': [current_date['day']],
        'sum': [amount],
        'comment': [description],
        'category': ['']
    })

    df = pd.concat([df, new_data], ignore_index=True)
    load_data_to_excel(df)

    return "Don't forget to choose Category"


def delete_last_spending():
    df = load_data_from_excel()
    if not df.empty:
        df = df.drop(df.index[-1])
        load_data_to_excel(df)
        return "Last spending deleted"
    else:
        return "No spending to delete"


def update_last_spending_category(text):
    df = load_data_from_excel()
    if not df.empty:
        df.at[df.index[-1], 'category'] = text
        load_data_to_excel(df)
        return "Category updated for the last spending"
    else:
        return "No spending to update"


def get_report(text):
    df = load_data_from_google_sheets()
    current_date = get_current_date()

    if text == '📊 День':
        # Assuming the 'day' in current_date already includes time, comparisons should be date-only
        today_report = df[(pd.to_datetime(df['date']).dt.date == pd.to_datetime(current_date['day']).date())]
        return format_report(today_report, CURRENCY)



    elif text == '📊 Неделя':
        df['date'] = pd.to_datetime(df['date']).dt.date
        start_of_week = datetime.now().date() - timedelta(days=6)
        end_of_week = datetime.now().date()
        week_report = df[(df['date'] >= start_of_week) & (df['date'] <= end_of_week)]
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
