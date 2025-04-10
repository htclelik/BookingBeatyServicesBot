# sheets_utils.py
from datetime import datetime

import gspread
import pytz  # Для работы с часовыми поясами

from app.config import TIMEZONE
from app.services.google_sheets_api import get_reminders_worksheet
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


EXPECTED_HEADERS = [
    'job_id', 'client_chat_id', 'appointment_time_iso', 'reminder_time_iso',
    'reminder_type', 'status', 'message_text', 'google_event_id', 'sheet_row_index'
]


def _get_headers_with_retry(worksheet, retries=3):
    for i in range(retries):
        try:
            headers = worksheet.row_values(1)
            if headers and all(h in headers for h in EXPECTED_HEADERS):
                return headers
            else:
                 logger.warning(f"Попытка {i+1}: Заголовки не найдены или неполные: {headers}")
        except gspread.exceptions.APIError as e:
             logger.warning(f"Попытка {i+1}: Ошибка API при чтении заголовков: {e}")
        if i < retries - 1:
            import time
            time.sleep(2**i) # Экспоненциальная задержка
    logger.error(f"Не удалось получить корректные заголовки после {retries} попыток.")
    return None

async def add_reminder_to_sheet(reminder_data: dict):
    """Добавляет строку с данными напоминания в Google Таблицу."""
    try:
        worksheet = get_reminders_worksheet()
        headers = _get_headers_with_retry(worksheet)
        if not headers:
             logger.error("Не удалось добавить напоминание: отсутствуют заголовки в таблице.")
             return None

        # Убедимся, что все нужные ключи есть в reminder_data
        for header in headers:
            if header not in reminder_data and header != 'sheet_row_index': # sheet_row_index не нужен при добавлении
                 logger.warning(f"Отсутствует ключ '{header}' в данных напоминания. Будет пропущен.")
                 # Можно установить значение по умолчанию или вернуть ошибку

        # Формируем строку в правильном порядке столбцов
        row_to_insert = [reminder_data.get(header, '') for header in headers if header != 'sheet_row_index']

        # Вставляем строку и получаем результат (включая номер строки)
        result = worksheet.append_row(row_to_insert, value_input_option='USER_ENTERED', insert_data_option='INSERT_ROWS')
        logger.info(f"Напоминание {reminder_data.get('job_id')} добавлено в таблицу. Результат: {result}")

        # Получаем номер добавленной строки
        # 'updates.updatedRange': "'Reminders'!A6:I6" -> извлекаем 6
        updated_range = result.get('updates', {}).get('updatedRange', '')
        try:
            # Пример парсинга диапазона типа "'Sheet1'!A5:I5"
            range_parts = updated_range.split('!')[-1] # A5:I5
            start_cell = range_parts.split(':')[0] # A5
            row_index_str = ''.join(filter(str.isdigit, start_cell)) # 5
            row_index = int(row_index_str)
            # Обновляем колонку sheet_row_index в только что добавленной строке
            col_index = headers.index('sheet_row_index') + 1 # +1 т.к. индексы колонок gspread начинаются с 1
            worksheet.update_cell(row_index, col_index, row_index)
            logger.info(f"Установлен sheet_row_index={row_index} для job_id={reminder_data.get('job_id')}")
            return row_index
        except Exception as e:
            logger.error(f"Не удалось извлечь или обновить row_index из диапазона '{updated_range}': {e}")
            return None # Не смогли записать индекс строки

    except gspread.exceptions.APIError as e:
        logger.error(f"Ошибка API Google Sheets при добавлении напоминания: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при добавлении напоминания в таблицу: {e}", exc_info=True)
    return None

async def update_reminder_status_in_sheet(row_index: int, new_status: str):
    """Обновляет статус напоминания в Google Таблице по номеру строки."""
    if not row_index:
        logger.error("Невозможно обновить статус: не передан row_index.")
        return False
    try:
        worksheet = get_reminders_worksheet()
        headers = _get_headers_with_retry(worksheet)
        if not headers:
             logger.error("Не удалось обновить статус: отсутствуют заголовки.")
             return False
        if 'status' not in headers:
            logger.error("Не найдена колонка 'status' в таблице.")
            return False

        status_col_index = headers.index('status') + 1 # Индекс колонки статуса (начиная с 1)
        worksheet.update_cell(row_index, status_col_index, new_status)
        logger.info(f"Статус напоминания в строке {row_index} обновлен на '{new_status}'.")
        return True
    except gspread.exceptions.APIError as e:
        logger.error(f"Ошибка API Google Sheets при обновлении статуса в строке {row_index}: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при обновлении статуса в строке {row_index}: {e}", exc_info=True)
    return False

async def get_pending_reminders_from_sheet():
    """Получает все напоминания со статусом PENDING из таблицы."""
    pending_reminders = []
    try:
        worksheet = get_reminders_worksheet()
        # Получаем все записи как список словарей
        all_records = worksheet.get_all_records(expected_headers=EXPECTED_HEADERS)
        if not all_records: # Если таблица пуста или только заголовки
            logger.info("Таблица напоминаний пуста или не содержит данных.")
            return []

        logger.info(f"Найдено {len(all_records)} записей в таблице напоминаний.")
        tz = pytz.timezone(TIMEZONE)
        now_aware = datetime.now(tz)

        for idx, record in enumerate(all_records):
            row_index_in_sheet = idx + 2 # +2 потому что get_all_records пропускает заголовки (1) и нумерация с 1
            # Проверяем наличие всех ключей перед доступом
            if not all(key in record for key in ['status', 'reminder_time_iso', 'job_id']):
                 logger.warning(f"Пропуск строки {row_index_in_sheet}: отсутствуют необходимые поля (status, reminder_time_iso, job_id). Данные: {record}")
                 continue

            if record.get('status') == 'PENDING':
                try:
                    # Преобразуем время напоминания в aware datetime
                    reminder_time_str = record.get('reminder_time_iso')
                    if not reminder_time_str:
                         logger.warning(f"Пропуск строки {row_index_in_sheet}: пустое значение reminder_time_iso.")
                         continue
                    reminder_time = tz.localize(datetime.fromisoformat(reminder_time_str.split('+')[0])) # Убираем TZ если он есть, локализуем сами

                    # Проверяем, что время еще не прошло
                    if reminder_time > now_aware:
                        record['sheet_row_index'] = row_index_in_sheet # Добавляем реальный номер строки
                        pending_reminders.append(record)
                        logger.debug(f"Найдено PENDING напоминание для reschedule: {record.get('job_id')} на {reminder_time}")
                    else:
                         logger.warning(f"Найдено PENDING напоминание {record.get('job_id')}, но время {reminder_time} уже прошло. Статус не обновляется автоматически.")
                         # Можно добавить логику обновления статуса на 'MISSED'
                except ValueError:
                     logger.error(f"Ошибка парсинга времени '{record.get('reminder_time_iso')}' в строке {row_index_in_sheet}. Пропуск.")
                except Exception as e:
                     logger.error(f"Ошибка обработки PENDING записи {record.get('job_id')} в строке {row_index_in_sheet}: {e}")

        logger.info(f"Найдено {len(pending_reminders)} ожидающих напоминаний для планирования.")
        return pending_reminders
    except gspread.exceptions.APIError as e:
        logger.error(f"Ошибка API Google Sheets при получении ожидающих напоминаний: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при получении ожидающих напоминаний: {e}", exc_info=True)
    return [] # Возвращаем пустой список в случае ошибки


