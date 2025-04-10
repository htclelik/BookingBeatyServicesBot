# services/ai_assistant_api.py
import logging
import openai
from typing import Optional
from app.config import OPENAI_ASSISTANT_ID # Только ID ассистента нужен здесь

logger = logging.getLogger(__name__)

# ИЗМЕНЕНА СИГНАТУРА: принимает client и thread_id
async def get_ai_response(client: openai.AsyncOpenAI, thread_id: str, user_message: str) -> Optional[str]:
    """
    Gets a response from the configured OpenAI Assistant using an EXISTING thread.
    """
    try:
        # Валидация сообщения остается
        if not user_message or len(user_message.strip()) == 0:
            logger.warning(f"Received empty message for thread {thread_id}.")
            return "Пожалуйста, введите ваш вопрос." # Или вернуть None/спец. маркер
        if len(user_message) > 4096: # Ограничение на длину сообщения все еще актуально
             logger.warning(f"User message exceeds 4096 chars for thread {thread_id}.")
             return "Ваше сообщение слишком длинное."

        assistant_id = OPENAI_ASSISTANT_ID
        if not assistant_id:
            # Эта проверка дублируется, но оставим на всякий случай
            logger.error("OPENAI_ASSISTANT_ID is not configured.")
            return "CONFIG_ERROR: Assistant ID not found."

        # === OpenAI API Calls ===
        # 1. Добавляем сообщение пользователя в СУЩЕСТВУЮЩИЙ Thread
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        logger.debug(f"Added user message to existing thread {thread_id}")

        # 2. Запускаем Run в СУЩЕСТВУЮЩЕМ треде.
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        logger.debug(f"Run status for thread {thread_id}: {run.status}")

        # === Обработка результата (как и раньше) ===
        if run.status == "completed":
            # ... (код получения сообщения из треда остается тем же) ...
            messages = await client.beta.threads.messages.list(
                thread_id=thread_id,
                order="asc"
            )
            assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
            if assistant_messages:
                # Берем последнее сообщение от ассистента после последнего run
                # Внимание: если были tool calls, сообщений может быть больше
                last_message = assistant_messages[-1]
                if last_message.run_id == run.id and last_message.content and last_message.content[0].type == "text":
                     response_text = last_message.content[0].text.value
                     logger.debug(f"Raw response from assistant in thread {thread_id}: {response_text[:200]}...")
                     return response_text
                else:
                    # Ищем предпоследнее, если последнее - это результат tool call?
                    # Либо проверяем run_id у сообщения
                    logger.warning(f"Last assistant message in thread {thread_id} (run {run.id}) is not text or missing.")
                    # Попытка найти предыдущее сообщение от этого run_id (упрощенно)
                    for msg in reversed(assistant_messages):
                        if msg.run_id == run.id and msg.content and msg.content[0].type == "text":
                           response_text = msg.content[0].text.value
                           logger.debug(f"Found earlier response from run {run.id}: {response_text[:200]}...")
                           return response_text
                    return "Ассистент не предоставил текстовый ответ для этого запроса."

            else:
                logger.warning(f"No assistant messages found in completed run for thread {thread_id}.")
                return "Не удалось получить ответ от ассистента."
        else:
            # ... (обработка ошибок run остается той же) ...
             logger.error(f"Run for thread {thread_id} did not complete successfully. Status: {run.status}. Last Error: {run.last_error}")
             error_message = f"RUN_ERROR: Status {run.status}."
             return error_message

    # Обработка исключений остается той же (APIError, AuthenticationError и т.д.)
    # AuthenticationError теперь менее вероятна, т.к. клиент инициализируется один раз
    except openai.APIError as e:
        logger.error(f"OpenAI API Error for thread {thread_id}: {e.status_code} - {e.message}", exc_info=True)
        return f"API_ERROR: {e.status_code}"
    except Exception as e:
        logger.error(f"Unexpected error in get_ai_response for thread {thread_id}: {str(e)}", exc_info=True)
        return "INTERNAL_ERROR: Unexpected issue."