# app/handlers/common.py
"""Модуль содержит общие обработчики и функции для работы с ботом."""

from aiogram import types
from aiogram.fsm.context import FSMContext

from app.utils.constants import START_TEXT, HELP_TEXT, CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON
from app.keyboards.reply import create_custom_keyboard

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def send_message_with_keyboard(message: types.Message, text: str, keyboard=None, parse_mode="HTML"):
    """Функция отправки сообщений с проверкой HTML"""
    try:
        if not text:
            logger.warning("Пустой текст сообщения")
            text = "Нет сообщения"

        return await message.answer(text, parse_mode=parse_mode, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return await message.answer("Произошла ошибка. Попробуйте ещё раз.")

# 🔹 Обработчик /start
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await send_message_with_keyboard(message, START_TEXT, create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON))

# 🔹 Обработчик /help
async def help_handler(message: types.Message):
    await send_message_with_keyboard(message, HELP_TEXT,parse_mode="HTML")


