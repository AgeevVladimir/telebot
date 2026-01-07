import logging
from datetime import datetime, timedelta
import os
import socket
from urllib3.util.timeout import Timeout

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Utils import constants

logger = logging.getLogger(__name__)

# Set socket timeout to prevent hanging
socket.setdefaulttimeout(30)

# Constants
SPREADSHEET_ID = getattr(constants, 'SPREADSHEET_ID', None)
SHEET_NAME = 'Spendings'
RANGE_NAME = f'{SHEET_NAME}!A1:Z'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'Utils/myfinance1514-2-53f670e62850.json'

FILE_NAME = 'spendings.xlsx'
CURRENCY = '€'

# API timeout settings
API_TIMEOUT = 20  # seconds

day_abbreviations = {
    'Monday': 'пн',
    'Tuesday': 'вт',
    'Wednesday': 'ср',
    'Thursday': 'чт',
    'Friday': 'пт',
    'Saturday': 'сб',
    'Sunday': 'вс'
}

# Global service object (lazy initialization)
_service = None


def get_sheet_service():
    """Get or create Google Sheets service with error handling."""
    global _service
    if _service is not None:
        return _service
    
    try:
        if not SPREADSHEET_ID:
            raise ValueError("SPREADSHEET_ID not found in constants")
        
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
        
        logger.info("Initializing Google Sheets service...")
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        # Create service with timeout
        service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        _service = service.spreadsheets()
        logger.info("Google Sheets service initialized successfully")
        return _service
        
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets service: {e}")
        raise


def get_day_abbreviation(day):
    """Get abbreviated day name."""
    return day_abbreviations.get(day, day)


def get_current_date():
    """Get current date information."""
    try:
        current_date = datetime.now()
        return {
            'day': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'year': current_date.strftime('%Y'),
            'month': current_date.strftime('%m %B').lower()
        }
    except Exception as e:
        logger.error(f"Error getting current date: {e}")
        return {
            'day': 'unknown',
            'year': 'unknown',
            'month': 'unknown'
        }


def load_data_from_google_sheets():
    """Load data from Google Sheets and return as DataFrame with error handling and timeout."""
    try:
        logger.debug("Starting load_data_from_google_sheets")
        service = get_sheet_service()
        logger.debug("Got sheet service, executing query...")
        
        # Execute with timeout handling
        result = service.values().get(
            spreadsheetId=SPREADSHEET_ID, 
            range=RANGE_NAME
        ).execute()
        
        values = result.get('values', [])
        logger.info(f"Loaded {len(values)} rows from Google Sheets")
        
        if not values:
            logger.warning("No data found in Google Sheets")
            return pd.DataFrame(columns=['year', 'month', 'date', 'sum', 'comment', 'category'])
        
        logger.debug(f"Creating DataFrame from {len(values)} rows")
        df = pd.DataFrame(values[1:], columns=values[0])
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        logger.info(f"Converted to DataFrame with {len(df)} rows")
        return df
        
    except socket.timeout:
        logger.error("Timeout connecting to Google Sheets API")
        raise Exception("Google Sheets API timeout - unable to load data")
    except HttpError as e:
        logger.error(f"Google Sheets API error: {e}")
        raise Exception("Failed to access Google Sheets. Check permissions and spreadsheet ID.")
    except Exception as e:
        logger.error(f"Error loading data from Google Sheets: {e}", exc_info=True)
        raise


def save_spending(text):
    """Save a spending entry to Google Sheets with error handling."""
    try:
        logger.debug(f"save_spending called with: {text[:50]}")
        
        # Input validation
        if not text or not text.strip():
            return "Please provide amount and description (e.g., '10.50 coffee')"
        
        parts = text.split(maxsplit=1)
        if len(parts) != 2:
            return "Please provide both amount and description separated by space"
        
        amount, description = parts
        amount = amount.strip()
        description = description.strip()
        
        # Validate amount
        try:
            float(amount)
        except ValueError:
            return f"Invalid amount: {amount}. Please enter a valid number."
        
        logger.debug(f"Calling Google Sheets API to save: {amount} {description}")
        current_date = get_current_date()
        values = [[current_date['year'], current_date['month'], current_date['day'], amount, description, '']]
        body = {'values': values}
        
        sheet = get_sheet_service()
        logger.debug("Got sheet service, executing append...")
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        logger.debug("Append completed, extracting row number...")

        # Extract the row number from the updated range
        updated_range = result.get('updates', {}).get('updatedRange', '')
        if updated_range:
            # Parse the range like 'Spendings!A5:F5' to get row 5
            row_number = int(updated_range.split('!')[1].split(':')[0][1:])  # Extract number from A5
        else:
            # Fallback: get the last row
            sheet_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
            row_number = len(sheet_data.get('values', []))
        
        logger.info(f"Spending saved: {amount} {description} (row {row_number})")
        return "Spending saved. Don't forget to choose Category", row_number
        
    except HttpError as e:
        logger.error(f"Google Sheets API error in save_spending: {e}")
        return f"Error saving spending: {e}", None
    except Exception as e:
        logger.error(f"Unexpected error in save_spending: {e}", exc_info=True)
        return f"Unexpected error saving spending: {e}", None


def delete_last_spending():
    """Delete the last spending entry from Google Sheets with error handling."""
    try:
        sheet = get_sheet_service()
        
        # First, get all values to find the last row
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
        values = result.get('values', [])
        
        if not values or len(values) <= 1:  # Only header or empty
            return "No spending entries to delete"
        
        # Find the last non-empty row (excluding header)
        last_row_index = len(values)
        
        # Clear the last row
        range_to_clear = f'{SHEET_NAME}!A{last_row_index}:F{last_row_index}'
        body = {'values': [['', '', '', '', '', '']]}  # Clear all columns
        
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_clear,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        logger.info(f"Deleted last spending entry (row {last_row_index})")
        return "Last spending entry deleted successfully"
        
    except HttpError as e:
        logger.error(f"Google Sheets API error in delete_last_spending: {e}")
        return f"Error deleting spending: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in delete_last_spending: {e}")
        return f"Unexpected error deleting spending: {e}"


def update_spending_category(text, row_number=None):
    try:
        sheet = get_sheet_service()
        
        if row_number is None:
            # Fetch the last row number with data to find where to update the category
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
            values = result.get('values', [])
            if values:
                row_number = len(values)  # This gives us the row index in 1-based indexing
            else:
                return "No spending to update"

        # Assuming category is in the 6th column ('F')
        range_to_update = f'{SHEET_NAME}!F{row_number}'
        values = [[text]]  # The new category text
        body = {'values': values}
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_update,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        return "Category updated for the spending"
    except HttpError as e:
        logger.error(f"Google Sheets API error in update_spending_category: {e}")
        return f"Error updating category: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in update_spending_category: {e}")
        return f"Unexpected error updating category: {e}"


def update_last_spending_category(text):
    """Update the category for the last spending entry with error handling."""
    try:
        if not text or not text.strip():
            return "Please provide a valid category"
        
        return update_spending_category(text)
        
    except Exception as e:
        logger.error(f"Unexpected error in update_last_spending_category: {e}")
        return f"Unexpected error updating category: {e}"


def get_total_amount():
    """Retrieve the total amount from the spreadsheet."""
    try:
        sheet = get_sheet_service()
        value_response = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Pivot!D2:D2').execute()
        if not value_response.get('values'):
            logging.warning("No values found in Pivot!D2:D2")
            return f"{CURRENCY} 0.00"
        
        value_str = value_response['values'][0][0]
        # Clean up the string and convert it to a float
        cleaned_value = float(value_str.replace('\xa0', '').replace(',', '.'))
        result = f'{CURRENCY} {cleaned_value:.2f}'
        logging.info(f"Retrieved total amount: {result}")
        return result
    except HttpError as e:
        logging.error(f"Google Sheets API error in get_total_amount: {e}")
        return f"Error retrieving total amount: {e}"
    except ValueError as e:
        logging.error(f"Value conversion error in get_total_amount: {e}")
        return f"Error processing total amount: {e}"
    except Exception as e:
        logging.error(f"Unexpected error in get_total_amount: {e}")
        return f"Unexpected error retrieving total amount: {e}"


def get_report(text):
    """Generate financial reports with error handling."""
    try:
        df = load_data_from_google_sheets()
        current_date = get_current_date()
        
        if df.empty:
            return "No spending data available"

        if text == '📊 День':
            try:
                today_report = df[(pd.to_datetime(df['date']).dt.date == pd.to_datetime(current_date['day']).date())]
                return format_report(today_report, CURRENCY)
            except Exception as e:
                logger.error(f"Error generating daily report: {e}")
                return "Error generating daily report"

        elif text == '📊 Неделя':
            try:
                df['date'] = pd.to_datetime(df['date']).dt.date
                start_of_week = datetime.now().date() - timedelta(days=6)
                end_of_week = datetime.now().date()
                week_report = df[(df['date'] >= start_of_week) & (df['date'] <= end_of_week)]
                return format_report(week_report, CURRENCY)
            except Exception as e:
                logger.error(f"Error generating weekly report: {e}")
                return "Error generating weekly report"

        elif text == '📊 Месяц':
            try:
                df['sum'] = df['sum'].astype(float)
                category_month_report = df[(df['month'].str.contains(current_date['month'])) &
                                           (df['year'].astype(int) == int(current_date['year']))]
                df_excluded_sum = category_month_report.groupby('category')['sum'].sum().reset_index()
                return format_month_report(df_excluded_sum, CURRENCY)
            except Exception as e:
                logger.error(f"Error generating monthly report: {e}")
                return "Error generating monthly report"

        elif text == '📊 Год':
            try:
                df['sum'] = df['sum'].astype(float)
                category_year_report = df[df['year'].astype(int) == int(current_date['year'])]
                df_excluded_sum = category_year_report.groupby('category')['sum'].sum().reset_index()
                return format_year_report(df_excluded_sum, CURRENCY)
            except Exception as e:
                logger.error(f"Error generating yearly report: {e}")
                return "Error generating yearly report"

        else:
            return "Invalid report type"
            
    except Exception as e:
        logger.error(f"Error in get_report: {e}")
        return f"Error generating report: {e}"


def format_report(report_df, currency):
    """Format spending report with error handling."""
    try:
        if report_df.empty:
            return "No data to display"
            
        formatted_report = ""
        total_sum = 0

        for _, row in report_df.iterrows():
            try:
                day_abbreviation = get_day_abbreviation(pd.to_datetime(row['date']).strftime('%A'))
                # Handle None values to prevent format string errors
                category = str(row['category']) if row['category'] is not None else ''
                amount = str(row['sum']) if row['sum'] is not None else '0'
                comment = str(row['comment']) if row['comment'] is not None else ''
                
                formatted_report += f"{day_abbreviation}. {category:<10} {currency}{amount:<4} {comment}\n"
                total_sum += float(amount) if amount else 0
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error formatting row: {e}, skipping")
                continue

        formatted_report += f'Total: {total_sum} {currency}\n'
        return formatted_report.strip()
    except Exception as e:
        logger.error(f"Error in format_report: {e}", exc_info=True)
        return "Error formatting report"


def format_month_report(report_df, currency):
    """Format monthly spending report with error handling."""
    try:
        if report_df.empty:
            return f'{datetime.now().strftime("%Y.%m")}\nNo data to display'
            
        formatted_report = f'{datetime.now().strftime("%Y.%m")}\n'
        total_sum = 0

        for _, row in report_df.iterrows():
            try:
                # Handle None values
                category = str(row['category']) if row['category'] is not None else ''
                amount = float(row['sum']) if row['sum'] is not None else 0
                formatted_report += f"{category} {currency}{amount}\n"
                total_sum += amount
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error formatting row: {e}, skipping")
                continue

        formatted_report += f'Total: {total_sum} {currency}\n'
        return formatted_report.strip()
    except Exception as e:
        logger.error(f"Error in format_month_report: {e}", exc_info=True)
        return "Error formatting monthly report"


def format_year_report(report_df, currency):
    """Format yearly spending report with error handling."""
    try:
        if report_df.empty:
            return f'{datetime.now().strftime("%Y")}\nNo data to display'
            
        formatted_report = f'{datetime.now().strftime("%Y")}\n'
        total_sum = 0

        for _, row in report_df.iterrows():
            try:
                # Handle None values
                category = str(row['category']) if row['category'] is not None else ''
                amount = float(row['sum']) if row['sum'] is not None else 0
                formatted_report += f"{category} {currency}{amount}\n"
                total_sum += amount
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error formatting row: {e}, skipping")
                continue

        formatted_report += f'Total: {total_sum} {currency}\n'
        return formatted_report.strip()
    except Exception as e:
        logger.error(f"Error in format_year_report: {e}")
        return "Error formatting yearly report"


def delete_last_spending():
    """Delete the last spending entry from Google Sheets with error handling."""
    try:
        sheet = get_sheet_service()
        
        # First, get all values to find the last row
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
        values = result.get('values', [])
        
        if not values or len(values) <= 1:  # Only header or empty
            return "No spending entries to delete"
        
        # Find the last non-empty row (excluding header)
        last_row_index = len(values)
        
        # Clear the last row
        range_to_clear = f'{SHEET_NAME}!A{last_row_index}:F{last_row_index}'
        body = {'values': [['', '', '', '', '', '']]}  # Clear all columns
        
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_clear,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        logger.info(f"Deleted last spending entry (row {last_row_index})")
        return "Last spending entry deleted successfully"
        
    except HttpError as e:
        logger.error(f"Google Sheets API error in delete_last_spending: {e}")
        return f"Error deleting spending: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in delete_last_spending: {e}")
        return f"Unexpected error deleting spending: {e}"
