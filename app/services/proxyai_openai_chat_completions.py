# # services/ai_assistant_handler.py
# import json
# import traceback
# from typing import Dict, Any, List
#
# from aiogram import Router
# from openai import OpenAI
#
# from app.config import OPENAI_API_KEY
# from app.database.local_mini_db import MASTER_SERVICES_FULL
# from app.utils.logger import setup_logger
# from app.utils.system_prompt import SYSTEM_PROMPT
#
# logger = setup_logger(__name__)
#
#
# # Initialize router
# router = Router()
#
# async def get_ai_response(user_message: str, user_state: str, user_data: Dict[str, Any] = None,
#                           message_history: List[Dict] = None) -> str:
#     """
#     Gets response from OpenAI using Chat Completions API.
#     """
#     try:
#         if not user_message or len(user_message) > 4096:
#             raise ValueError("Invalid request: empty message or length exceeds 4096 characters")
#
#         # Initialize OpenAI client
#         client = OpenAI(
#             api_key=OPENAI_API_KEY,
#             base_url="https://api.proxyapi.ru/openai/v1",
#         )
#
#         # Prepare messages
#         messages = [
#             {"role": "system",
#              "content": f"""
#             {SYSTEM_PROMPT}.
#             Ты предлагаешь следующие услуги: {MASTER_SERVICES_FULL}.
#             Текущее состояние диалога: {user_state}.
#             """}
#         ]
#
#         # Add message history if available
#         if message_history:
#             messages.extend(message_history)
#
#         # Add user message context if available
#         if user_data:
#             messages.append({
#                 "role": "system",
#                 "content": f" {SYSTEM_PROMPT}\n Информация о пользователе: {json.dumps(user_data)}"
#             })
#
#         # Add current user message
#         messages.append({
#             "role": "user",
#             "content": user_message
#         })
#
#         # Call the API
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",  # Выберите подходящую модель
#             messages=messages,
#             temperature=0.5,
#             max_tokens=250
#         )
#
#         # Process the response
#         if response.choices and response.choices[0].message:
#             return response.choices[0].message.content
#
#         return "Ответ не найден"
#
#     except Exception as e:
#         logger.error(f"Error when requesting OpenAI: {str(e)}\n{traceback.format_exc()}")
#         return "Произошла внутренняя ошибка. Попробуйте снова."
