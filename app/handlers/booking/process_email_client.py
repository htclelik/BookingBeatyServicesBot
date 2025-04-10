# from aiogram import Router, types
# from aiogram.fsm.context import FSMContext
#
# from app.states.state_manager import StateManager
# from app.keyboards.inline import create_inline_universal_keyboard
# from app.utils.constants import BACK_BUTTON
# from app.utils.formmaters import validate_email
# from app.utils.logger import setup_logger
#
# logger = setup_logger(__name__)
# router = Router()
# state_manager = StateManager()
#
# async def process_user_email(message: types.Message, state: FSMContext):
#     """Обрабатывает ввод email"""
#     is_valid, email_or_error = validate_email(message.text.strip())
#
#     if not is_valid:
#         await message.answer(
#             f"❌ {email_or_error}",
#             # reply_markup=create_inline_keyboard({"🔙Назад": "back"}, 1)
#             reply_markup=create_inline_universal_keyboard(BACK_BUTTON, 1)
#         )
#         return
#
#     await state.update_data(email=email_or_error)
#     logger.info(f"User {message.from_user.id} entered email: {email_or_error}")
#
#     # ✅ После успешного ввода email вызываем переход к следующему шагу
#     await state_manager.handle_transition(message, state, "next")
#
