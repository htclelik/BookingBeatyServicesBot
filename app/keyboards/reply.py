from typing import List, Optional
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_custom_keyboard(buttons: List, layout: Optional[List[int]] = None,
                           request_phone: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for i, button in enumerate(buttons):
        # Проверяем, является ли button словарем или строкой
        if isinstance(button, dict):
            # Если это словарь, берем первый ключ как текст кнопки
            button_text = list(button.keys())[0]
        else:
            # Иначе используем button как есть (строка)
            button_text = button

        builder.button(text=button_text, request_contact=(request_phone and i == 0))

    # Если layout не передан, автоматически делаем 2 кнопки в ряд
    builder.adjust(*(layout if layout else [2] * (len(buttons) // 2 + len(buttons) % 2)))

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=request_phone)

