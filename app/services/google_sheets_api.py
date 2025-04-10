
import os
import gspread
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from app.config import GOOGLE_CREDENTIALS_PATH, SCOPES_FEED_DRIVE, GOOGLE_SHEET_ID, REMINDERS_WORKSHEET_NAME, \
    GOOGLE_SHEET_NAME, BOOKINGS_LOG_WORKSHEET_NAME
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

_reminders_worksheet = None
_bookings_log_worksheet = None
_google_sheets_client = None

def get_google_sheets_client():

    global _google_sheets_client
    if _google_sheets_client is None:
        try:
            scope = SCOPES_FEED_DRIVE
            creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
            _google_sheets_client = gspread.authorize(creds)

            logger.info("Клиент Google Sheets успешно аутентифицирован.")

        except Exception as e:
            logger.error(f"Ошибка при получении клиента Google Sheets: {e}")
            raise e


    return _google_sheets_client

def get_reminders_worksheet():
    """Возвращает рабочий лист 'Reminders'."""
    global _reminders_worksheet
    if _reminders_worksheet is None:
        try:
            client = get_google_sheets_client()
            spreadsheet = client.open(GOOGLE_SHEET_NAME)
            _reminders_worksheet = spreadsheet.worksheet(REMINDERS_WORKSHEET_NAME)
            logger.info(f"Рабочий лист '{REMINDERS_WORKSHEET_NAME}' успешно получен.")
        except gspread.exceptions.WorksheetNotFound:
             logger.error(f"Лист '{REMINDERS_WORKSHEET_NAME}' не найден в таблице '{GOOGLE_SHEET_NAME}'!")
             raise
        except Exception as e:
            logger.error(f"Ошибка при получении рабочего листа: {e}", exc_info=True)
            raise
    return _reminders_worksheet

def get_bookings_log_worksheet():
    """Возвращает рабочий лист 'BookingsLog'."""
    global _bookings_log_worksheet
    if _bookings_log_worksheet is None:
        try:
            client = get_google_sheets_client()
            spreadsheet = client.open(GOOGLE_SHEET_NAME)
            # Используем имя листа из конфига
            _bookings_log_worksheet = spreadsheet.worksheet(BOOKINGS_LOG_WORKSHEET_NAME)
            logger.info(f"Рабочий лист '{BOOKINGS_LOG_WORKSHEET_NAME}' успешно получен.")
        except gspread.exceptions.WorksheetNotFound:
             logger.error(f"Лист '{BOOKINGS_LOG_WORKSHEET_NAME}' не найден в таблице '{GOOGLE_SHEET_NAME}'!")
             raise
        except Exception as e:
            logger.error(f"Ошибка при получении рабочего листа '{BOOKINGS_LOG_WORKSHEET_NAME}': {e}", exc_info=True)
            raise
    return _bookings_log_worksheet