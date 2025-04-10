# app/services/google_calendar_api.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import GOOGLE_CREDENTIALS_PATH, SCOPES_CALENDAR
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def safe_calendar_request(func, *args, **kwargs):
    """Обёртка для обработки ошибок при запросах в Google Calendar."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Ошибка при запросе в календарь: {e}")
        return None

def get_calendar_service(credentials_path=None):
    """Создание аутентифицированного сервиса Calendar API с обработкой ошибок."""
    try:
        credentials_path = credentials_path or GOOGLE_CREDENTIALS_PATH
        scopes = SCOPES_CALENDAR
        logger.info(f"Initializing Google Calendar service with credentials from {credentials_path}")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes
        )
        service = build('calendar', 'v3', credentials=credentials)
        logger.info("Google Calendar service successfully initialized")
        return service
    except FileNotFoundError as e:
        logger.error(f"Credentials file not found: {e}")
        raise
    except HttpError as e:
        logger.error(f"Google API HTTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing Google Calendar service: {e}")
        raise


