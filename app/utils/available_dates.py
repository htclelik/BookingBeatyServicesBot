
from datetime import datetime, timedelta

from app.utils.events_calendar import get_events_from_calendar
from app.utils.data_utils import get_master_by_id, get_work_hours, get_weekend_days
from app.utils.parse_event import parse_event_time
from app.utils.logger import setup_logger


logger = setup_logger(__name__)


def get_available_dates(year, month, master_id, calendar_id):
    """
    Получает доступные даты для записи, исключая полностью занятые дни и выходные дни мастера.
    Рабочее время берется из информации о мастере или по умолчанию с 9 до 18.
    Возвращает словарь доступных дат { 'YYYY-MM-DD': 'date_YYYY-MM-DD' }
    и список полностью занятых дат (список строк).
    """
    now = datetime.now()
    first_day = datetime(year, month, 1)
    last_day = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else (
                datetime(year + 1, 1, 1) - timedelta(days=1))

    # Получаем рабочие часы и выходные дни из информации о мастере
    master_info = get_master_by_id(master_id)
    work_start_hour, work_end_hour = get_work_hours(master_info)
    weekend_days = get_weekend_days(master_info)

    logger.info(f"Getting events for master {master_id} in calendar {calendar_id} from {first_day} to {last_day}")
    logger.info(f"Working hours: {work_start_hour}:00 - {work_end_hour}:00")
    logger.info(f"Weekend days: {weekend_days}")

    events = get_events_from_calendar(calendar_id, first_day, last_day)
    busy_slots_by_date = {}

    for event in events:
        parsed = parse_event_time(event)
        if parsed:
            start_dt, end_dt = parsed
            date_str = start_dt.strftime('%Y-%m-%d')
            busy_slots_by_date.setdefault(date_str, []).append(
                (start_dt.hour * 60 + start_dt.minute, end_dt.hour * 60 + end_dt.minute)
            )

    fully_booked_dates = []
    available_dates = {}
    for day in range(1, last_day.day + 1):
        date_obj = datetime(year, month, day)
        if date_obj.date() < now.date():
            continue

        # Проверка, является ли день выходным для мастера
        weekday = date_obj.weekday()
        if weekday in weekend_days:
            fully_booked_dates.append(date_obj.strftime('%Y-%m-%d'))
            continue

        date_str = date_obj.strftime('%Y-%m-%d')
        busy_slots = busy_slots_by_date.get(date_str, [])
        working_minutes = (work_end_hour - work_start_hour) * 60
        occupied_minutes = sum(end - start for start, end in busy_slots)
        if occupied_minutes > working_minutes * 0.9:
            fully_booked_dates.append(date_str)
            continue
        free_slots_available = False
        busy_slots.sort()
        if not busy_slots or busy_slots[0][0] >= work_start_hour * 60 + 30:
            free_slots_available = True
        for i in range(len(busy_slots) - 1):
            if busy_slots[i + 1][0] - busy_slots[i][1] >= 30:
                free_slots_available = True
                break
        if busy_slots and busy_slots[-1][1] <= work_end_hour * 60 - 30:
            free_slots_available = True
        if free_slots_available:
            available_dates[date_str] = f"date_{date_str}"

    return available_dates, fully_booked_dates
