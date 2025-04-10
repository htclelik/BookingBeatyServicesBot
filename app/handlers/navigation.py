# app/handlers/navigation.py
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from app.handlers.common import send_message_with_keyboard
from app.keyboards.reply import create_custom_keyboard
from app.states.state_manager import state_manager
from app.utils.constants import CANCEL_TEXT, START_TEXT, LAYOUT_CUSTOM_212_BUTTON, CUSTOM_BUTTONS
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def universal_back_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад'"""
    logger.info("🔙 Возврат к предыдущему шагу")
    await state_manager.handle_transition(callback.message, state, "back")
    await callback.answer()  # Убираем индикатор загрузки


async def universal_cancel_handler(message: types.Message, state: FSMContext):
    """Обработчик отмены — очищает состояние и возвращает в меню"""
    logger.info("❌ Отмена операции")
    current_state = await state.get_state()
    user_id = message.from_user.id
    if current_state is None:
        logger.info(f"Пользователь {user_id} попытался отменить, но состояние уже было пустым.")
        return

    logger.info(f"Пользователь {user_id} отменяет действие из состояния: {current_state}")

    await state.clear()
    await message.answer("❌Действие отменено.\n‼️Диалог с ассистентом завершён",reply_markup=ReplyKeyboardRemove())

    # await message.answer(START_TEXT, parse_mode="HTML", )
    # await send_message_with_keyboard(message, START_TEXT,
    #                                  create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON))


async def universal_menu_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик возвращения в главное меню для inline-кнопок"""
    await callback.answer()  # Важно: подтверждаем callback
    logger.info(f"Возвращение в меню (callback data: {callback.data})")

    await state.clear()
    await callback.message.answer(
        "Действие отменено.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Показываем главное меню
    await send_message_with_keyboard(
        callback.message,
        START_TEXT,
        create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON),
        parse_mode="HTML"
        )


