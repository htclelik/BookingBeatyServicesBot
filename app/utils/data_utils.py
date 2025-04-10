from app.config import MASTERS_ID, GOOGLE_CALENDAR_ID
from app.database.local_mini_db import INFO_LIST_MASTER, MASTER_SERVICES_FULL
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def get_master_by_id(master_id: str):
    """Возвращает данные мастера по ID, если ID корректен"""
    logger.info(f"Входной master_id: {master_id} (тип: {type(master_id)})")

    # Если получен список, берем первый элемент
    if isinstance(master_id, list):
        master_id = master_id[0]

    try:
        master_id = int(master_id)
        return INFO_LIST_MASTER.get(master_id)
    except (ValueError, TypeError):
        logger.error(f"Неверный формат master_id: {master_id}")
        return None

def get_master_email(master_id: str):
    """Возвращает email мастера по ID, если ID корректен"""
    master_info = get_master_by_id(master_id)
    if master_info:
        return master_info.get("email")
    return None

# def get_chat_id_for_master()


def get_work_hours(master_info, default_start=9, default_end=18):
    """
    Извлекает рабочие часы из данных мастера.
    Если информации нет, возвращает значения по умолчанию.
    Если значения хранятся в списке, извлекает первое значение.
    """
    if master_info:
        work_start = master_info.get("work_start_hour", default_start)
        work_end = master_info.get("work_end_hour", default_end)
        logger.info(f"Тип work_start_hour: {type(work_start)}, значение: {work_start}")
        logger.info(f"Тип work_end_hour: {type(work_end)}, значение: {work_end}")

        # Если work_start или work_end являются списками, берем первый элемент
        if isinstance(work_start, list):
            work_start = work_start[0]
        if isinstance(work_end, list):
            work_end = work_end[0]
    else:
        work_start, work_end = default_start, default_end

    return int(work_start), int(work_end)  # Преобразуем в int на всякий случай



def get_weekend_days(master_info):
    """
    Извлекает список выходных дней из данных мастера.
    Выходные дни возвращаются в виде списка номеров дней недели (0 - понедельник, 6 - воскресенье).
    Если информации нет, возвращается пустой список.
    """
    weekend_days = []
    if master_info and "weekend" in master_info:
        weekend_str = master_info["weekend"]
        # Маппинг сокращений на номера дней недели
        day_mapping = {
            "Пн": 0, "Вт": 1, "Ср": 2, "Чт": 3, "Пт": 4, "Сб": 5, "Вс": 6
        }
        for day_abbr in weekend_str.split(", "):
            if day_abbr in day_mapping:
                weekend_days.append(day_mapping[day_abbr])
    return weekend_days

def get_calendar_id_for_master(master_id, master_ids=MASTERS_ID, calendar_ids=GOOGLE_CALENDAR_ID):
    """
    Возвращает calendar_id для указанного master_id из списков master_ids и calendar_ids.

    Args:
        master_id: ID мастера
        master_ids: Список ID мастеров
        calendar_ids: Список ID календарей, соответствующих мастерам

    Returns:
        str or None: ID календаря для указанного мастера или None, если мастер не найден
    """
    logger.info(f"Определение calendar_id= {calendar_ids} для master_id={master_id}")
    for i, m in enumerate(master_ids):
        if str(m) == str(master_id):
            return calendar_ids[i]
    logger.error(f"Master ID {master_id} not found in master_ids list")
    return None



