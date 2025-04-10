# app/utils/validators.py
import re
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
from aiogram.types import CallbackQuery


# Проверка валидности телефона
def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^\+7\d{10}$", phone))  # Проверяет, что номер начинается с +7 и 10 цифр

# Проверка валидности email
def validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))  # Проверяет, что email содержит символ @ и точку

# Проверка выбранных услуг
def validate_selected_services(selected_services: Dict[str, Any]) -> Tuple[bool, str]:
    """Проверка выбранных услуг"""
    if not selected_services:
        return False, "Не выбрано ни одной услуги"

    # Проверка корректности структуры данных
    for service_id, service in selected_services.items():
        if not isinstance(service, dict):
            return False, f"Некорректный формат данных для услуги {service_id}"

        required_fields = ['full_name_service', 'duration']
        missing = [f for f in required_fields if f not in service]
        if missing:
            return False, f"Отсутствуют обязательные поля: {', '.join(missing)}"

    return True, ""

# Проверка выбранного времени
def validate_booking_time(date_str: str, time_str: str,
                          available_times: List[str]) -> Tuple[bool, str]:
    """Проверка выбранного времени"""
    try:
        # Проверка формата даты
        datetime.strptime(date_str, '%Y-%m-%d')

        # Проверка доступности времени
        if time_str not in available_times:
            return False, "Выбранное время недоступно"

        return True, ""
    except ValueError:
        return False, "Некорректный формат даты"

# app/utils/callback_utils.py


async def validate_callback(callback_query: CallbackQuery, expected_length: int = 3) -> list:
    """Проверяет формат callback_data и возвращает список элементов"""
    data = callback_query.data.split("||")
    if len(data) < expected_length:
        await callback_query.answer("Ошибка: некорректный формат данных!", show_alert=True)
        return None
    return data
