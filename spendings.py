from datetime import datetime, timedelta

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from Utils import constants

# Constants
SPREADSHEET_ID = constants.GOOGLE_SHEET_ID
SHEET_NAME = 'Spendings'
RANGE_NAME = f'{SHEET_NAME}!A1:Z'  # Adjust based on where you want to start reading/writing
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


def load_data_from_google_sheets():
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        df = pd.DataFrame(values[1:], columns=values[0])
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        return df


def save_spending(text):
    amount, description = text.split(maxsplit=1)
    current_date = get_current_date()
    values = [[current_date['year'], current_date['month'], current_date['day'], amount, description, '']]
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return "Spending saved. Don't forget to choose Category"


def delete_last_spending():
    # Fetch the last row number with data
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    if values:
        last_row = len(values)
        request_body = {
            'requests': [
                {
                    'deleteDimension': {
                        'range': {
                            'sheetId': 0,  # Assuming it's the first sheet, adjust if necessary
                            'dimension': 'ROWS',
                            'startIndex': last_row - 1,  # Zero-based indexing
                            'endIndex': last_row
                        }
                    }
                }
            ]
        }
        sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request_body).execute()
        return "Last spending deleted"
    else:
        return "No spending to delete"


def update_last_spending_category(text):
    # Fetch the last row number with data to find where to update the category
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    if values:
        last_row = len(values)  # This gives us the row index in 1-based indexing
        # Assuming category is in the 6th column ('F')
        range_to_update = f'{SHEET_NAME}!F{last_row}'
        values = [[text]]  # The new category text
        body = {'values': values}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_update,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return "Category updated for the last spending"
    else:
        return "No spending to update"


def get_total_amount():
    # Retrieve the value from the spreadsheet
    value_response = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Pivot!D2:D2').execute()
    # Extract the string value
    value_str = value_response['values'][0][0]
    # Clean up the string and convert it to a float
    cleaned_value = float(value_str.replace('\xa0', '').replace(',', '.'))
    # Print the value with the Euro symbol
    result = f'{CURRENCY} {cleaned_value}'
    return result


def get_report(text):
    df = load_data_from_google_sheets()
    current_date = get_current_date()

    if text == '📊 День':
        today_report = df[(pd.to_datetime(df['date']).dt.date == pd.to_datetime(current_date['day']).date())]
        return format_report(today_report, CURRENCY)



    elif text == '📊 Неделя':
        df['date'] = pd.to_datetime(df['date']).dt.date
        start_of_week = datetime.now().date() - timedelta(days=6)
        end_of_week = datetime.now().date()
        week_report = df[(df['date'] >= start_of_week) & (df['date'] <= end_of_week)]
        return format_report(week_report, CURRENCY)


    elif text == '📊 Месяц':
        df['sum'] = df['sum'].astype(float)
        category_month_report = df[(df['month'].str.contains(current_date['month'])) &
                                   (df['year'].astype(int) == int(current_date['year']))]
        df_excluded_sum = category_month_report.groupby('category')['sum'].sum().reset_index()
        return format_month_report(df_excluded_sum, CURRENCY)

    elif text == '📊 Год':
        df['sum'] = df['sum'].astype(float)
        category_year_report = df[df['year'].astype(int) == int(current_date['year'])]
        df_excluded_sum = category_year_report.groupby('category')['sum'].sum().reset_index()
        return format_year_report(df_excluded_sum, CURRENCY)

    else:
        return "Invalid report type"


def format_report(report_df, currency):
    formatted_report = ""
    total_sum = 0

    for _, row in report_df.iterrows():
        day_abbreviation = get_day_abbreviation(pd.to_datetime(row['date']).strftime('%A'))
        formatted_report += f"{day_abbreviation}. {row['category']:<10} {currency}{row['sum']:<4} {row['comment']}\n"
        total_sum += float(row['sum'])

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def format_month_report(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y.%m")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += float(row['sum'])

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()


def format_year_report(report_df, currency):
    formatted_report = f'{datetime.now().strftime("%Y")}\n'
    total_sum = 0

    for _, row in report_df.iterrows():
        formatted_report += f"{row['category']} {currency}{row['sum']}\n"
        total_sum += float(row['sum'])

    formatted_report += f'Total: {total_sum} {currency}\n'
    return formatted_report.strip()
