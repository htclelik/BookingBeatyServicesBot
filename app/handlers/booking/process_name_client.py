from aiogram import Router, types
from aiogram.fsm.context import FSMContext

from app.states.state_manager import StateManager
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()
state_manager = StateManager()

async def start_booking(message: types.Message, state: FSMContext):
    """Обрабатывает команду /book и начинает процесс записи"""
    # Устанавливаем начальное состояние "start"
    await state.set_state("start")

    await state_manager.handle_transition(message, state, "next")


async def process_user_name(message: types.Message, state: FSMContext):
    """Обрабатывает ввод имени"""

    name = message.text.strip() if message.text else "Без имени"
    await state.update_data(name=name)
    logger.info(f"User {message.from_user.id} entered name: {name}")
    await state_manager.handle_transition(message, state, "next")