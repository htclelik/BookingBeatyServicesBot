# test_calendar.py
import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.keyboards.calendar import create_calendar_keyboard
from app.config import BOT_TOKEN


# Список доступных дат для теста
def get_test_available_dates():
    """Получаем тестовый набор доступных дат"""
    now = datetime.now()
    # Форматируем даты в формате YYYY-MM-DD
    available_dates = [
        (now.replace(day=5)).strftime('%Y-%m-%d'),
        (now.replace(day=10)).strftime('%Y-%m-%d'),
        (now.replace(day=15)).strftime('%Y-%m-%d'),
        (now.replace(day=20)).strftime('%Y-%m-%d'),
        (now.replace(day=25)).strftime('%Y-%m-%d')
    ]
    return available_dates


async def start_handler(message: Message):
    """Обработчик команды /start для тестирования календаря"""
    now = datetime.now()

    # Для теста используем фиктивный список доступных дат
    available_dates = get_test_available_dates()

    # Создаем календарную клавиатуру с текущим месяцем и доступными датами
    calendar_kb = create_calendar_keyboard(now.year, now.month, available_dates)

    await message.answer("Выберите дату для записи:", reply_markup=calendar_kb)


async def calendar_callback_handler(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик callback-запросов от календаря (для тестирования)"""
    callback_data = CalendarCallback.parse(callback_query.data)

    if callback_data.action == "DAY":
        # Выбран день
        selected_date = datetime(callback_data.year, callback_data.month, callback_data.day)
        formatted_date = selected_date.strftime('%d.%m.%Y')
        await callback_query.message.edit_text(f"Вы выбрали дату: {formatted_date}")
        return

    if callback_data.action in ["PREV-MONTH", "NEXT-MONTH"]:
        # Изменение месяца
        available_dates = get_test_available_dates()
        await callback_query.message.edit_text(
            "Выберите дату:",
            reply_markup=create_calendar_keyboard(callback_data.year, callback_data.month, available_dates)
        )
        return

    if callback_data.action == "IGNORE":
        await callback_query.answer()
        return

    if callback_data.action == "CANCEL":
        await callback_query.message.edit_text("Выбор даты отменен")
        return


# Тестовые функции
@pytest.mark.asyncio
async def test_start_handler():
    """Тест обработчика start_handler"""
    # Создаем mock объекты
    message = MagicMock()
    message.answer = MagicMock(return_value=asyncio.Future())
    message.answer.return_value.set_result(None)

    # Вызываем обработчик
    await start_handler(message)

    # Проверяем, что message.answer был вызван
    message.answer.assert_called_once()
    # Проверяем, что в вызове есть текст и reply_markup
    args, kwargs = message.answer.call_args
    assert "Выберите дату для записи:" in args
    assert "reply_markup" in kwargs


@pytest.mark.asyncio
@patch('app.keyboards.calendar.CalendarCallback.parse')
async def test_calendar_callback_day_selected(mock_parse):
    """Тест выбора дня в календаре"""
    # Настраиваем мок для CalendarCallback.parse
    mock_callback_data = MagicMock()
    mock_callback_data.action = "DAY"
    mock_callback_data.year = 2025
    mock_callback_data.month = 3
    mock_callback_data.day = 15
    mock_parse.return_value = mock_callback_data

    # Создаем mock объекты
    callback_query = MagicMock()
    callback_query.data = f"{CALENDAR_CALLBACK}:DAY:2025:3:15"

    # Добавляем атрибут message вручную
    callback_query.message = MagicMock()
    callback_query.message.edit_text = MagicMock(return_value=asyncio.Future())
    callback_query.message.edit_text.return_value.set_result(None)

    state = MagicMock(spec=FSMContext)

    # Вызываем обработчик
    await calendar_callback_handler(callback_query, state)

    # Проверяем, что message.edit_text был вызван с ожидаемым сообщением
    callback_query.message.edit_text.assert_called_once()
    args, _ = callback_query.message.edit_text.call_args
    assert "Вы выбрали дату: 15.03.2025" in args


@pytest.mark.asyncio
@patch('app.keyboards.calendar.CalendarCallback.parse')
async def test_calendar_callback_change_month(mock_parse):
    """Тест смены месяца в календаре"""
    # Настраиваем мок для CalendarCallback.parse
    mock_callback_data = MagicMock()
    mock_callback_data.action = "NEXT-MONTH"
    mock_callback_data.year = 2025
    mock_callback_data.month = 4
    mock_callback_data.day = 0
    mock_parse.return_value = mock_callback_data

    # Создаем mock объекты
    callback_query = MagicMock()
    callback_query.data = f"{CALENDAR_CALLBACK}:NEXT-MONTH:2025:4:0"

    # Добавляем атрибут message вручную
    callback_query.message = MagicMock()
    callback_query.message.edit_text = MagicMock(return_value=asyncio.Future())
    callback_query.message.edit_text.return_value.set_result(None)

    state = MagicMock(spec=FSMContext)

    # Вызываем обработчик
    await calendar_callback_handler(callback_query, state)

    # Проверяем, что message.edit_text был вызван
    callback_query.message.edit_text.assert_called_once()
    args, kwargs = callback_query.message.edit_text.call_args
    assert "Выберите дату:" in args
    assert "reply_markup" in kwargs


@pytest.mark.asyncio
@patch('app.keyboards.calendar.CalendarCallback.parse')
async def test_calendar_callback_ignore(mock_parse):
    """Тест игнорирования callback"""
    # Настраиваем мок для CalendarCallback.parse
    mock_callback_data = MagicMock()
    mock_callback_data.action = "IGNORE"
    mock_parse.return_value = mock_callback_data

    # Создаем mock объекты
    callback_query = MagicMock()
    callback_query.data = f"{CALENDAR_CALLBACK}:IGNORE:0:0:0"
    callback_query.answer = MagicMock(return_value=asyncio.Future())
    callback_query.answer.return_value.set_result(None)

    state = MagicMock(spec=FSMContext)

    # Вызываем обработчик
    await calendar_callback_handler(callback_query, state)

    # Проверяем, что callback_query.answer был вызван
    callback_query.answer.assert_called_once()


@pytest.mark.asyncio
@patch('app.keyboards.calendar.CalendarCallback.parse')
async def test_calendar_callback_cancel(mock_parse):
    """Тест отмены выбора даты"""
    # Настраиваем мок для CalendarCallback.parse
    mock_callback_data = MagicMock()
    mock_callback_data.action = "CANCEL"
    mock_parse.return_value = mock_callback_data

    # Создаем mock объекты
    callback_query = MagicMock()
    callback_query.data = f"{CALENDAR_CALLBACK}:CANCEL:0:0:0"

    # Добавляем атрибут message вручную
    callback_query.message = MagicMock()
    callback_query.message.edit_text = MagicMock(return_value=asyncio.Future())
    callback_query.message.edit_text.return_value.set_result(None)

    state = MagicMock(spec=FSMContext)

    # Вызываем обработчик
    await calendar_callback_handler(callback_query, state)

    # Проверяем, что message.edit_text был вызван с ожидаемым сообщением
    callback_query.message.edit_text.assert_called_once()
    args, _ = callback_query.message.edit_text.call_args
    assert "Выбор даты отменен" in args


if __name__ == "__main__":
    # Этот код выполняется только при прямом запуске файла, не при запуске тестов
    asyncio.run(main())


async def main():
    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем обработчики
    dp.message.register(start_handler, Command("start"))
    dp.callback_query.register(calendar_callback_handler, lambda c: c.data.startswith(CALENDAR_CALLBACK))

    # Запускаем бота
    await dp.start_polling(bot)