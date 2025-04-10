# app/handlers/promotions.py
from aiogram import types, Router

from app.keyboards.reply import create_custom_keyboard
from app.utils.constants import CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON, PROMOTIONS_TEXT

router = Router()

async def gift_handler(message: types.Message):
    """
    Обработчик команды /gift.
    Отправляет пользователю информацию о скидках и предложениях.
    """
    # message.from_user.first_name


    await message.answer(
        f" {PROMOTIONS_TEXT}",
        parse_mode="HTML",
        reply_markup=create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON)
    )