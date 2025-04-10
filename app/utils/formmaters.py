import re
import json

import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from aiogram import types


from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Словарь русских названий месяцев
russian_name_month = {
    1: "Янв", 2: "Фев", 3: "Мар",
    4: "Апр", 5: "Май", 6: "Июн",
    7: "Июл", 8: "Авг", 9: "Сен",
    10: "Окт", 11: "Ноя", 12: "Дек"
}


def sanitize_callback_data(data: str) -> str:
    """
    Очищает callback_data:
      - Заменяет пробелы на подчёркивания.
      - Усечёт результат до 64 байт в UTF-8, гарантируя корректное декодирование.
    """
    # Заменяем пробелы на подчеркивания
    data = data.replace(" ", "_")
    # Кодируем в UTF-8 и усекаем до 64 байт
    encoded = data.encode("utf-8")[:64]
    # Декодируем, игнорируя обрезанные символы
    return encoded.decode("utf-8", "ignore")


def format_price(price: int) -> str:
    return f" {price} ₽"  # Пример: "1500 ₽"


def format_duration(duration: float) -> str:

    hours_duration = duration / 60
    # Формат без лишних нулей после запятой
    if hours_duration == 1:
        text_hour = "час"
    elif 0 < hours_duration < 1 or hours_duration < 5:
        text_hour = "часа"
    else:
        text_hour = "часов"

    return f"{hours_duration:g} {text_hour}"


def format_duration_minutes(duration: int) -> str:
    # Формат без лишних нулей после запятой
    if 1 < duration < 5:
        text_minutes = "минуты"
    elif duration == 1:
        text_minutes = "минута"
    else:
        text_minutes = "минут"
    return f" или {duration:g} {text_minutes}"



def split_message(response):

    """Разбивает длинный текст на части, чтобы избежать ошибки Telegram."""
    return [response[i:i + 4096] for i in range(0, len(response), 4096)]


async def send_response(message: types.Message, response: str):
    """
    Отправляет пользователю основной ответ и дополнительные данные (если есть).

    :param response:
    :param message: Объект сообщения Telegram

    """
    # Отправляем основной текст, если он есть
    for part in split_message(response or ""):
        await message.answer(part, parse_mode="HTML")

def clear_ai_response(text: str) -> str:
    """
    Cleans the AI response text from system annotations.
    """
    # return re.sub(r"【[^】]+】", "", text).strip()
    return re.sub(r"【.*?】", "", text).strip()


def extract_system_data(text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts system data from the AI response.
    """
    match = re.search(r"【systemTextByAi: (.*?)】", text)
    if match:
        try:
            # Replace %% markers around values
            system_text = match.group(1).replace('%%', '"')
            return json.loads(system_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse system data: {e}")
    return None


def format_phone_number(phone_input: str) -> tuple[bool, str]:
    """
    Форматирует введенный пользователем номер телефона.

    Args:
        phone_input: Строка с номером телефона от пользователя

    Returns:
        Tuple[bool, str]: (признак валидности, отформатированный номер или сообщение об ошибке)
    """
    # Удаляем все нецифровые символы
    digits_only = re.sub(r'\D', '', phone_input)

    # Проверяем, что у нас ровно 10 цифр
    if len(digits_only) != 10:
        return False, f"Неверный формат номера. Пожалуйста, введите 10 цифр номера без '8'  без '+7'. Например: 9221507879"

    # Форматируем номер в формате +7XXXXXXXXXX
    formatted_phone = f"+7{digits_only}"

    return True, formatted_phone


def validate_email(email: str) -> tuple[bool, str]:
    """
    Проверяет и форматирует адрес электронной почты.

    Аргументы:
        email (str): Адрес электронной почты для проверки

    Возвращает:
        tuple[bool, str]:
            - Первый элемент - булево значение, указывающее на корректность email
            - Второй элемент - либо отформатированный email, либо сообщение об ошибке
    """
    # Проверка на пустое значение
    if not email:
        return False, "Email не может быть пустым"

    # Удаление пробелов по краям
    email = email.strip()

    # Основной регулярный паттерн для проверки email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # Проверка соответствия базовому паттерну
    if not re.match(email_pattern, email):
        return False, "Неверный формат email. Используйте корректный адрес (например, example@domain.com)"

    # Дополнительные проверки
    try:
        # Разделение email на локальную часть и домен
        local_part, domain = email.split('@')

        # Проверка длины локальной части
        if len(local_part) > 64:
            return False, "Локальная часть email (перед @) слишком длинная"

        # Проверка длины домена
        if len(domain) > 255:
            return False, "Доменная часть email слишком длинная"

        # Проверка на последовательные точки
        if '..' in local_part or '..' in domain:
            return False, "Email не может содержать последовательные точки"

        # Приведение к нижнему регистру для единообразия
        formatted_email = email.lower()

        return True, formatted_email

    except ValueError:
        # Если разделение не удалось (нет символа @)
        return False, "Неверный формат email. Email должен содержать символ '@'"


def format_date_to_russian(date_str: str) -> str:
    """Форматирует дату в читабельный русский формат (20 марта 2025)."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.day} {russian_name_month[date_obj.month]} {date_obj.year}"


