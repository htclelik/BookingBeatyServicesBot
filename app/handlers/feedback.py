# """ Модуль feedback.py содержит обработчик для команды 'Предоставить обратную связь'. """
# from aiogram import Router
# from aiogram.types import Message
#
# from app.keyboards.reply import create_custom_keyboard
# from app.utils.constants import FEEDBACK_TEXT, CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON, FEEDBACK_THANK_TEXT
#
# # Создаем роутер для обработки команд
# router = Router()
#
#
# async def feedback_command_handler(message: Message):
#     """ Обработчик команды /feedback. """
#     await message.answer(
#         f" {FEEDBACK_TEXT}",
#         parse_mode="HTML",
#         reply_markup=create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON)
#     )
#
# async def feedback_message_handler(message: Message):
#     """ Обработчик текстовых сообщений для обратной связи. """
#     # Здесь можно добавить логику сохранения обратной связи в базу данных или отправки администратору
#     await message.answer(
#         f" {FEEDBACK_THANK_TEXT}",
#         parse_mode="HTML",
#         reply_markup=create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON)
#     )