from datetime import datetime, timedelta

from app.services.google_calendar_api import get_calendar_service
from app.utils.data_utils import get_calendar_id_for_master
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_appointment(user_data):
    """
    Создает запись в календаре мастера на основе данных бронирования.
    Args:
        user_data (dict): Данные о бронировании (мастер, дата, время, услуги).
    Returns:
        event или None: Созданное событие или None при ошибке.
    """
    try:
        # Получаем calendar_id мастера
        master_id = user_data.get("master_id")
        if not master_id:
            logger.error("Не указан master_id")
            return None
        calendar_id = get_calendar_id_for_master(master_id)
        if not calendar_id:
            logger.error(f"Не найден calendar_id для мастера {master_id}")
            return None
        # Добавляем мастера, если нужно стандартное уведомление и ему
        # Формируем дату и время
        date_str = user_data.get("date")  # Формат: "2025-03-29"
        time_str = user_data.get("time").replace("time_", "")  # Формат: "14:00"
        start_datetime = f"{date_str}T{time_str}:00+03:00"  # Часовой пояс Москвы

        # Считаем общую длительность услуг
        total_duration = sum(
            int(service.get("duration", 60))  # По умолчанию 60 минут
            for service in user_data.get("services", [])
        )
        end_datetime = (
                datetime.fromisoformat(start_datetime) +
                timedelta(minutes=total_duration)
        ).isoformat()

        # Описание события
        service_names = [
            service.get("full_name_service", "Неизвестная услуга")
            for service in user_data.get("services", [])
        ]
        description = (
            f"Клиент: {user_data.get('name', 'Не указано')}\n"
            f"Телефон: {user_data.get('phone', 'Не указан')}\n"
            # f"Email клиента: {user_data.get('email', 'Не указан')}\n\n"
            f"Мастер: {user_data.get('master_name', 'Не указан')}\n"
            f"Услуги: {'\n, '.join(service_names)}"
        )

        event = {
            "summary": f"Запись: {user_data.get('name')}",
            "description": description,
            "start": {"dateTime": start_datetime, "timeZone": "Europe/Moscow"},
            "end": {"dateTime": end_datetime, "timeZone": "Europe/Moscow"},

            "reminders": {
                "useDefault": True,
            },
        }
        # Отправка запроса к API
        service = get_calendar_service()
        logger.info(f"Создаём событие с данными: {event}")
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendNotifications=True,
            sendUpdates="all"
        ).execute()

        logger.info(f"Событие создано: {created_event.get('htmlLink')}")
        return created_event

    except Exception as e:
        logger.error(f"Ошибка при создании записи: {e}")
        return None


