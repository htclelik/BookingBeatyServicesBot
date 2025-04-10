import logging

import openai
from aiogram import types, Router  # Используем Router для лучшей структуры
from aiogram.fsm.context import FSMContext

from app.config import OPENAI_API_KEY
from app.services.ai_assistant_api import get_ai_response
from app.states.booking_states import BookingStates
# --- Состояния ---
from app.states.conversation_states import ConversationStates
from app.utils.constants import WELCOME_TEXT
from app.utils.formmaters import clear_ai_response

# --- Логгер ---
logger = logging.getLogger(__name__)

# --- Создание Router ---
router = Router()

# --- Константы ---
BOOKING_SIGNAL_TAG = "[START_BOOKING_PROCESS]" # Наш сигнальный маркер

# --- Клиент OpenAI ---
try:
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    logger.critical(f"Failed to initialize OpenAI client: {e}")
    client = None # Обработка случая, если ключ не найден

# --- Обработчики ---
async def start_ai_assistant_session_handler(message: types.Message, state: FSMContext):
    """
    Запуск сессии ассистента по команде /assistant или кнопке.
    Отправляет приветствие и переводит в состояние ожидания вопроса.
    """
    if not client:
        await message.answer("Ошибка конфигурации OpenAI. Свяжитесь с администратором.")
        return

    await state.clear()  # Очищаем предыдущее состояние
    user_id = message.from_user.id
    logger.info(f"User {user_id} starting NEW AI assistant session.")
    try:
        # СОЗДАЕМ НОВЫЙ THREAD ТОЛЬКО ПРИ СТАРТЕ СЕССИИ
        thread = await client.beta.threads.create()
        thread_id = thread.id
        # СОХРАНЯЕМ THREAD_ID В СОСТОЯНИИ FSM
        await state.update_data(thread_id=thread_id)
        logger.info(f"Created new thread {thread_id} for user {user_id} and saved to state.")

        await message.answer(
            f"{WELCOME_TEXT}\nЗадайте мне любой вопрос по нашим услугам!",
            parse_mode="HTML",
        )
        await state.set_state(ConversationStates.waiting_for_question)

    except openai.APIError as e:
        logger.error(f"OpenAI API Error during thread creation for user {user_id}: {e}", exc_info=True)
        await message.answer("Не удалось начать сессию с ассистентом из-за ошибки OpenAI. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Unexpected error during AI session start for user {user_id}: {e}", exc_info=True)
        await message.answer("Произошла непредвиденная ошибка при запуске ассистента.")

async def process_ai_question(message: types.Message, state: FSMContext):
    """
    Обрабатывает сообщение пользователя, когда бот в состоянии ожидания вопроса от ассистента.
    Отправляет запрос AI, анализирует ответ на наличие маркера бронирования.
    """
    if not client:
        await message.answer("Ошибка конфигурации OpenAI. Свяжитесь с администратором.")
        return
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    query = message.text.strip()

    if not query:
        await message.answer("Пожалуйста, введите ваш вопрос.")
        return

    # ПОЛУЧАЕМ THREAD_ID ИЗ СОСТОЯНИЯ
    user_data = await state.get_data()
    thread_id = user_data.get("thread_id")

    if not thread_id:
        logger.error(f"Thread ID not found in state for user {user_id}. Restarting session.")
        await message.answer(
            "Произошла ошибка сессии. Пожалуйста, начните диалог с ассистентом заново (например, командой /assistant).")
        await state.clear()
        return  # Прерываем выполнение

    logger.info(f"Processing query in thread {thread_id} for {username}: '{query[:100]}...'")
    processing_msg = await message.answer("⏳ Думаю над вашим вопросом...")


    try:
        # Вызываем функцию get_ai_response, передавая ей ТЕКУЩИЙ thread_id
        # Убедитесь, что get_ai_response БОЛЬШЕ НЕ СОЗДАЕТ НОВЫЙ ТРЕД!
        # ai_response_text = await get_ai_response(client, thread_id, query) # Передаем client и thread_id
        response_text = await get_ai_response(client, thread_id, query)
        ai_response_text = (clear_ai_response(response_text))

        # Удаляем сообщение "Обрабатываю..."
        await processing_msg.delete()

        # === Улучшенная обработка ответа/ошибок ===
        if ai_response_text is None:  # На всякий случай
            logger.error(f"AI response was None for user {user_id}.")
            await message.answer("К сожалению, не удалось получить ответ. Попробуйте еще раз.")
        elif ai_response_text.startswith("AUTH_ERROR"):
            logger.critical(f"OpenAI Authentication Failed for user {user_id}! Check API Key!")
            await message.answer("Произошла критическая ошибка конфигурации. Пожалуйста, свяжитесь с администратором.")
        elif ai_response_text.startswith("CONFIG_ERROR"):
            logger.error(f"OpenAI Configuration Error (e.g., Assistant ID) for user {user_id}.")
            await message.answer("Произошла ошибка конфигурации ассистента. Свяжитесь с администратором.")
        elif ai_response_text.startswith(("RUN_ERROR", "API_ERROR", "INTERNAL_ERROR")):
            logger.warning(f"Received error from AI service for user {user_id}: {ai_response_text}")
            await message.answer(
                "Возникла временная проблема при обработке вашего запроса OpenAI. Попробуйте спросить еще раз немного позже.")
        # === Конец обработки ошибок ===

        # Если ошибок не было, продолжаем с проверкой маркера
        elif BOOKING_SIGNAL_TAG in ai_response_text:
            logger.info(f"Booking signal '{BOOKING_SIGNAL_TAG}' FOUND for user {user_id} in thread {thread_id}.")
            final_response_to_user = ai_response_text.replace(BOOKING_SIGNAL_TAG, "").strip()

            if final_response_to_user:

                await message.answer(final_response_to_user)


            # 2. Устанавливаем состояние ожидания имени
            logger.info(f"Setting state to BookingStates.waiting_for_name_client for user {user_id}")

            await state.set_state(BookingStates.waiting_for_name_client)
            logger.info(f"Triggering name request for user {user_id}")


        else:
            # Обычный ответ без маркера
            logger.debug(f"No booking signal found. Sending regular AI response to user {user_id} in thread {thread_id}.")
            await message.answer(ai_response_text)
            await state.set_state(ConversationStates.waiting_for_question)  # Остаемся в ожидании

    except Exception as e:
        # Этот блок теперь ловит ошибки самого обработчика, а не get_ai_response (т.к. они обрабатываются выше)
        logger.error(f"Error in process_ai_question handler for user {user_id} in thread {thread_id}: {e}", exc_info=True)
        try:
            await processing_msg.delete()
        except Exception:
            pass
        await message.answer("❌ Произошла непредвиденная ошибка в работе бота. Пожалуйста, попробуйте позже.")
        await state.clear()


