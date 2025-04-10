from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from app.database.local_mini_db import MASTER_SERVICES_FULL
from app.keyboards.inline import create_inline_universal_keyboard
from app.states.booking_states import BookingStates
from app.utils.constants import BACK_BUTTON, CONFIRM_SERVICES_DETAILS_TEXT, CONFIRM_SERVICES_CALLBACK_PREFIX #CONFIRM_SERVICES_BUTTON
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()

async def get_service_buttons(master_id: int, selected_services: dict) -> dict:
    """
    Генерирует кнопки для списка услуг на основе выбранного мастера.

    Обоснование:
    - Приводим master_id к целому числу, чтобы избежать несоответствия типов ключей.
    - Если для данного мастера услуги отсутствуют, функция возвращает пустой словарь и логирует ошибку.
    - Это помогает избежать KeyError и даёт возможность уведомить пользователя о проблеме.
    """
    try:
        # Приводим master_id к целому числу
        master_key = int(master_id)
    except ValueError:
        logger.error(f"Некорректный master_id: {master_id}")
        return {}

    # Безопасное получение услуг по мастеру
    master_services = MASTER_SERVICES_FULL.get(master_key)
    if master_services is None:
        logger.error(f"Услуги для мастера с ID {master_key} не найдены.")
        return {}

    # Формирование кнопок: ставим галочку, если услуга уже выбрана, и отображаем название и цену
    service_buttons = {
        f"{'✅' if service_id in selected_services else '✔️'} {details.get('full_name_service', 'Услуга')} - {details.get('price', 'цена')}₽":
            f"service||{master_key}||{service_id}"
        for service_id, details in master_services.items()
    }
    return service_buttons

async def show_services(callback_query: CallbackQuery, master_id: int, state: FSMContext):
    """
    Отображает список услуг для выбранного мастера.

    Обоснование:
    - Получает из состояния выбранные услуги пользователя, чтобы отобразить актуальное состояние выбора.
    - Вызывает функцию get_service_buttons для генерации inline-клавиатуры.
    - Если услуги для мастера не найдены, уведомляет пользователя с помощью alert.
    - После успешного формирования клавиатуры обновляет состояние на BookingStates.waiting_for_service.
    """
    current_state = await state.get_state()
    logger.info(f"Current state: {current_state}")
    user_data = await state.get_data()
    selected_services = user_data.get("selected_services", {})

    # Генерация кнопок для услуг
    service_buttons = await get_service_buttons(master_id, selected_services)
    if not service_buttons:
        await callback_query.answer("Услуги для выбранного мастера не найдены.", show_alert=True)
        return

    text = f"Выберите услуги мастера {user_data.get('master_name', '')}:"
    # Объединяем с кнопкой подтверждения выбора услуг
    buttons = {**service_buttons, **{CONFIRM_SERVICES_DETAILS_TEXT: CONFIRM_SERVICES_CALLBACK_PREFIX}, **BACK_BUTTON}

    # Редактируем сообщение с новым текстом и клавиатурой
    await callback_query.message.edit_text(
        text,
        reply_markup=create_inline_universal_keyboard(buttons, 1)
    )
    # Устанавливаем новое состояние ожидания выбора услуг
    await state.set_state(BookingStates.waiting_for_service)
