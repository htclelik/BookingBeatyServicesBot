from app.services.google_calendar_api import get_calendar_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_events_from_calendar(calendar_id, start_date, end_date):
    """
    Получает список событий из Google Calendar для указанного календаря.

    Args:
        calendar_id: ID календаря
        start_date: Начальная дата (datetime)
        end_date: Конечная дата (datetime)

    Returns:
        list: Список событий из календаря
    """
    logger.info(f"Получение событий из календаря {calendar_id} с {start_date} по {end_date}")
    service = get_calendar_service()
    try:
        start_date_iso = start_date.isoformat() + 'Z'
        end_date_iso = end_date.isoformat() + 'Z'
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date_iso,
            timeMax=end_date_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        logger.info(f"Получено {len(events_result.get('items', []))} событий из календаря {calendar_id}")
        return events_result.get('items', [])


    except Exception as error:
        logger.error(f"Ошибка при получении событий из календаря {calendar_id}: {error}")
        return []
