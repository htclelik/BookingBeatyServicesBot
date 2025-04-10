# scheduler_setup.py
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from app.bot_instance import bot  # Убедись, что импорт работает
from app.utils.logger import setup_logger
from app.utils.sheets_utils import update_reminder_status_in_sheet, get_pending_reminders_from_sheet

logger = setup_logger(__name__)

# Инициализируем планировщик
scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

async def send_reminder_job(chat_id: int, text: str, sheet_row_index: int):
    """Асинхронная задача для отправки напоминания и обновления статуса в таблице."""
    if not bot:
        logger.error(f"Не могу отправить напоминание в чат {chat_id}: экземпляр бота не найден.")
        await update_reminder_status_in_sheet(sheet_row_index, 'ERROR_BOT_MISSING')
        return

    new_status = 'ERROR_SENDING' # Статус по умолчанию, если отправка не удалась
    try:
        logger.info(f"Отправка запланированного напоминания в чат {chat_id} (строка {sheet_row_index})")
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        logger.info(f"Напоминание успешно отправлено в чат {chat_id}")
        new_status = 'SENT'
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания в чат {chat_id}: {e}")
        new_status = f'ERROR_SENDING: {e}' # Записываем ошибку

    # Обновляем статус в таблице в любом случае
    await update_reminder_status_in_sheet(sheet_row_index, new_status)

async def schedule_reminders_from_sheet():
    """Планирует задачи из Google Таблицы при старте бота."""
    if not scheduler.running:
        logger.warning("Планировщик не запущен. Пропуск планирования из таблицы.")
        return

    logger.info("Загрузка и планирование ожидающих напоминаний из Google Таблицы...")
    pending_reminders = await get_pending_reminders_from_sheet()

    count = 0
    for reminder in pending_reminders:
        try:
            job_id = reminder.get('job_id')
            chat_id = int(reminder.get('client_chat_id'))
            reminder_time_str = reminder.get('reminder_time_iso')
            message_text = reminder.get('message_text', 'Напоминание о записи!') # Текст по умолчанию
            sheet_row = int(reminder.get('sheet_row_index')) # Получаем номер строки

            if not all([job_id, chat_id, reminder_time_str, sheet_row]):
                 logger.warning(f"Пропуск неполной записи при планировании: {reminder}")
                 continue

            # Преобразуем время из ISO строки в datetime объект
            tz = pytz.timezone(config.TIMEZONE)
            run_date = tz.localize(datetime.fromisoformat(reminder_time_str.split('+')[0]))

            # Добавляем задачу в планировщик
            scheduler.add_job(
                send_reminder_job,
                'date',
                run_date=run_date,
                args=[chat_id, message_text, sheet_row], # Передаем номер строки
                id=job_id,
                replace_existing=True, # Заменить, если задача с таким ID уже есть
                misfire_grace_time=3600 # Разрешить запуск в течение часа, если бот был выключен
            )
            count += 1
            logger.debug(f"Задача {job_id} запланирована на {run_date} для строки {sheet_row}")

        except ValueError as e:
            logger.error(f"Ошибка парсинга данных при планировании из таблицы: {e}. Запись: {reminder}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении задачи {reminder.get('job_id')} в планировщик: {e}", exc_info=True)

    logger.info(f"Завершено планирование из таблицы. Добавлено {count} задач.")

def add_job_to_scheduler(job_id: str, run_date: datetime, chat_id: int, text: str, sheet_row_index: int):
    """Добавляет ОДНУ задачу в работающий планировщик."""
    if not scheduler.running:
        logger.warning(f"Планировщик не запущен. Не могу добавить задачу {job_id}.")
        return False
    try:
        scheduler.add_job(
            send_reminder_job,
            'date',
            run_date=run_date,
            args=[chat_id, text, sheet_row_index],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=3600
        )
        logger.info(f"Задача {job_id} добавлена в планировщик на {run_date}")
        return True
    except Exception as e:
        logger.error(f"Ошибка добавления задачи {job_id} в планировщик: {e}", exc_info=True)
        return False