
from datetime import datetime, timedelta
from app.utils.events_calendar import get_events_from_calendar
from app.utils.parse_event import parse_event_time
from app.utils.logger import setup_logger


logger = setup_logger(__name__)


def get_available_times(date_str, calendar_id, work_start_hour, work_end_hour, service_duration=60):
    """
    Получает доступное время для записи на указанную дату с учетом длительности услуг.
    Возвращает список слотов, например:
    [{"text": "09:00", "callback_data": "time_09:00"}, ...]
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    next_day = date_obj + timedelta(days=1)
    events = get_events_from_calendar(calendar_id, date_obj, next_day)
    busy_intervals = []
    for event in events:
        parsed = parse_event_time(event)
        if parsed:
            start_dt, end_dt = parsed
            start_minutes = start_dt.hour * 60 + start_dt.minute
            end_minutes = end_dt.hour * 60 + end_dt.minute
            busy_intervals.append((start_minutes, end_minutes))
    busy_intervals.sort()
    # Преобразуем в целые числа, если переданы строки
    work_start_hour = int(work_start_hour)
    work_end_hour = int(work_end_hour)
    logger.info(f"work_start_hour: {work_start_hour}, type: {type(work_start_hour)}")
    logger.info(f"work_end_hour: {work_end_hour}, type: {type(work_end_hour)}")


    work_start_minutes = work_start_hour * 60
    work_end_minutes = work_end_hour * 60
    max_end_minutes = work_end_minutes + 120


    available_times = []
    time_step = 30
    for minutes in range(work_start_minutes, work_end_minutes, time_step):
        slot_end_minutes = minutes + service_duration
        if slot_end_minutes > max_end_minutes:
            continue
        is_available = True
        for busy_start, busy_end in busy_intervals:
            if not (slot_end_minutes <= busy_start or minutes >= busy_end):
                is_available = False
                break
        if is_available:
            hour = minutes // 60
            minute = minutes % 60
            time_str = f"{hour:02d}:{minute:02d}"
            available_times.append({"text": time_str, "callback_data": f"time_{time_str}"})
            logger.info(f"Доступное время: {time_str}")
    return available_times
