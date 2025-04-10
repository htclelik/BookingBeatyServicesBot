
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.handlers.booking.show_services import show_services
from app.states.state_manager import state_manager
from app.utils.data_utils import get_master_by_id
from app.utils.logger import setup_logger
from app.utils.service_utils import toggle_service_selection
from app.utils.validators import validate_callback

logger = setup_logger(__name__)
router = Router()

async def handle_master_selection(callback_query: CallbackQuery, state: FSMContext) -> Optional[bool]:
    """Обработка выбора мастера, master_id извлекается из callback_query.data"""
    parts = callback_query.data.split("_")
    if len(parts) < 3:
        await callback_query.answer("Ошибка: некорректный формат данных!", show_alert=True)
        return None

    # Извлекаем master_id из последней части строки
    master_id = parts[-1]
    logger.info(f"Получаем данные мастера по ID: {master_id}")
    master = get_master_by_id(master_id)
    if not master:
        await callback_query.answer("Ошибка! Мастер не найден.", show_alert=True)
        return None

    await state.update_data(
        master_id=master_id,
        master_name=master["name_master"],
        selected_services={}
    )
    logger.info(f"Выбран мастер: {master_id}")


    await show_services(callback_query, master_id, state)
    logger.info(f"Выбран мастер: {master_id} и {state}")
    return True

async def handle_service_selection(callback_query: CallbackQuery, state: FSMContext) -> bool:
    """Обработка выбора услуги"""
    logger.info("Выбор услуги")
    parts = await validate_callback(callback_query, 3)
    if not parts:
        return False

    try:
        master_id = int(parts[1])
    except ValueError:
        await callback_query.answer("Ошибка! Некорректный ID мастера.", show_alert=True)
        return False

    service_id = parts[2]
    logger.info(f"Selected master: {master_id}, Selected service: {service_id}")

    await toggle_service_selection(state, master_id, service_id)
    logger.info("Обновлённые выбранные услуги обновлены")

    await state.update_data()  # Обновление данных, если необходимо
    logger.info("Данные обновлены")

    await show_services(callback_query, master_id, state)
    logger.info("Показана новая страница услуг")
    return True

async def handle_confirm_services(callback_query: CallbackQuery, state: FSMContext) -> bool:
    """Обработка подтверждения выбора услуг с переходом к выбору даты"""
    logger.info("Этап: Подтверждение выбора услуг")
    user_data = await state.get_data()
    logger.info(f"User data: {user_data}")
    selected_services = user_data.get("selected_services", {})
    logger.info(f"Selected services: {selected_services}")

    if not selected_services:
        await callback_query.answer("Выберите хотя бы одну услугу!", show_alert=True)
        logger.warning("Нет выбранных услуг при подтверждении")
        return False

    logger.info(f"Saving selected services: {list(selected_services.values())}")
    await state.update_data(services=list(selected_services.values()))

    total_duration = sum(int(service.get('duration', 60)) for service in selected_services.values())
    logger.info(f"Total duration: {total_duration}")
    await state.update_data(total_duration=total_duration)

    await state_manager.handle_transition(callback_query.message, state, "next")
    logger.info("Переход к выбору даты выполнен")
    await callback_query.answer("Выберите дату и время записи")
    return True

