# app/utils/calendar_utils.py

from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.database.local_mini_db import DEFAULT_SESSION_DURATION
from app.keyboards.calendar_kb import create_calendar_keyboard
from app.states.booking_states import BookingStates
from app.utils.available_dates import get_available_dates
from app.utils.available_times import get_available_times
from app.utils.data_utils import get_calendar_id_for_master, get_master_by_id, get_work_hours
from app.utils.formmaters import russian_name_month
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def get_calendar_data(state: FSMContext):
    """Получает данные календаря с учётом текущего состояния"""

    logger.info("Получаем данные календаря из get_calendar_data...")
    current_state = await state.get_state()
    logger.info(f"Current state: {current_state}")
    user_data = await state.get_data()

    # Используем сохранённые year/month или текущие
    year = user_data.get('current_year', datetime.now().year)
    logger.info(f"Current year: {year}")

    month = user_data.get('current_month', datetime.now().month)
    logger.info(f"Current month: {month}")

    master_id = user_data.get("master_id")
    logger.info(f"Master ID: {master_id}")
    calendar_id = get_calendar_id_for_master(master_id)
    logger.info(f"Calendar ID: {calendar_id}")

    try:
        available_dates, fully_booked_dates = get_available_dates(
            year=year,
            month=month,
            master_id=master_id,
            calendar_id=calendar_id
        )
        return year, month, available_dates, fully_booked_dates
    except Exception as e:
        logger.error(f"Calendar data error: {e}")
        return None

async def get_time_calendar_data(state: FSMContext):
    """Получает данные о времени в календаре с учётом текущего состояния"""
    logger.info("Получаем данные о времени в календаре из get_time_calendar_data...")

    current_state = await state.get_state()
    logger.info(f"Current state: {current_state}")

    user_data = await state.get_data()
    master_id = user_data.get("master_id")
    logger.info(f"Master ID: {master_id}")

    calendar_id = get_calendar_id_for_master(master_id)
    logger.info(f"Calendar ID: {calendar_id}")

    confirm_date = user_data.get("date")
    logger.info(f"Confirm date: {confirm_date}")
    if confirm_date is None:
        logger.error("Дата не подтверждена, значение confirm_date равно None")
        # Можно вернуть None или обработать ошибку другим способом
        return None

    master_info = get_master_by_id(master_id)
    work_start_hour, work_end_hour = get_work_hours(master_info)

    try:
        available_times = get_available_times(
            date_str=confirm_date,
            calendar_id=calendar_id,
            work_start_hour=work_start_hour,
            work_end_hour=work_end_hour,
            service_duration=DEFAULT_SESSION_DURATION
        )
        return available_times
    except Exception as e:
        logger.error(f"Time calendar data error: {e}")
        return None


async def update_calendar_display(callback_query: CallbackQuery, state: FSMContext, year=None, month=None):
    """Обновляет отображение календаря с новыми параметрами"""
    logger.info(f"Обновление отображения календаря: {year}, {month}")
    current_state = await state.get_state()
    logger.info(f"Current state: {current_state}")

    try:
        # Получаем актуальные year и month из состояния, если не переданы
        if year is None or month is None:
            user_data = await state.get_data()
            year = user_data.get('current_year', datetime.now().year)
            month = user_data.get('current_month', datetime.now().month)

        # Получаем данные календаря
        calendar_data = await get_calendar_data(state)
        if not calendar_data:
            await callback_query.answer("Ошибка получения календаря", show_alert=True)
            return False

        year, month, available_dates, fully_booked_dates = calendar_data
        logger.info(f"Доступные даты: {available_dates}, Полностью занятые: {fully_booked_dates}")

        # Создаём клавиатуру с новыми данными
        keyboard = create_calendar_keyboard(year, month, available_dates, fully_booked_dates)
        logger.info(f"Клавиатура: {keyboard}")

        # Редактируем сообщение с новыми данными

        await callback_query.message.edit_text(
            f"📅 {russian_name_month[month]} {year}\nВыберите дату:",
            reply_markup=keyboard
        )

        logger.info("Отображение календаря обновлено")
        await state.set_state(BookingStates.waiting_for_date)
        return True

    except Exception as e:
        logger.error(f"Ошибка обновления календаря: {e}")
        return False
