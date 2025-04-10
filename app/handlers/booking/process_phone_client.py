from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from app.keyboards.inline import create_inline_universal_keyboard
from app.states.state_manager import StateManager
from app.utils.constants import (
    BACK_BUTTON
)
from app.utils.formmaters import format_phone_number
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()
state_manager = StateManager()



async def process_user_phone(message: types.Message, state: FSMContext):
    """Обрабатывает ввод телефона"""
    is_valid, phone_result = format_phone_number(message.text.strip())
    # phone = message.contact.phone_number if message.contact else message.text.strip()

    if not is_valid:
        await message.answer(
            phone_result,
            parse_mode="HTML",
            reply_markup=create_inline_universal_keyboard(BACK_BUTTON, 1)
        )
        return

    await state.update_data(phone=phone_result)
    logger.info(f"User {message.from_user.id} entered phone: {phone_result}")

    await state_manager.handle_transition(message, state, "next")