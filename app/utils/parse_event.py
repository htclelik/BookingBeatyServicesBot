from datetime import datetime
def parse_event_time(event):
    """
    Извлекает время начала и окончания из события.
    Возвращает кортеж (start_dt, end_dt) или None, если данные отсутствуют.
    """
    event_start = event['start'].get('dateTime')
    event_end = event['end'].get('dateTime')
    if event_start and event_end:
        start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
        return start_dt, end_dt
    return None
