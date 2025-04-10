# # app/keyboards/calendar.py
import calendar

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.inline import create_inline_universal_keyboard
from app.utils.constants import (
    BACK_BUTTON, IGNORE_CALLBACK,
    CONFIRM_TIME_CALLBACK_PREFIX, CONFIRM_DATE_CALLBACK_PREFIX,
    BACK_BUTTON_TEXT,
    BACK_CALLBACK, CONFIRM_ORDER_DETAILS_TEXT, NO_AVAILABLE_TIME_TEXT,
    NO_AVAILABLE_DATE_TEXT,
    CHOICE_TIME_TEXT,
    CHOICE_DATE_TEXT,
    CONFIRM_TIME_TEXT,
    CONFIRM_DATE_TEXT,
    SELECT_TIME_TEXT,
    SELECT_DATE_TEXT,
)
from app.utils.formmaters import russian_name_month
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def generate_calendar_header(year, month):
    """Создает заголовок календаря с кнопками навигации."""
    month_name = russian_name_month[month]
    return [
        InlineKeyboardButton(text="◀️", callback_data="prev"),
        InlineKeyboardButton(text=f"{month_name} {year}", callback_data=f"{IGNORE_CALLBACK}"),
        InlineKeyboardButton(text="▶️", callback_data="next")
    ]
def generate_week_days_header():
    """Создает заголовок календаря с днями недели."""
    russian_name_week_days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]

    return [
        InlineKeyboardButton(text=day, callback_data="ignore") for day in russian_name_week_days
    ]

def generate_calendar_days(year, month, available_dates, fully_booked_dates):
    """
    Создает ряды кнопок календаря.
    Если полная дата (например, "2025-03-29") содержится в available_dates, то отображается как доступная (с ✔️).
    Если дата содержится в fully_booked_dates, то отображается как полностью занятая (⛔).
    Иначе – стандартная кнопка ().
    """
    first_day, days_count = calendar.monthrange(year, month)
    calendar_buttons = []
    current_week = []
    # Заполнение пустыми кнопками перед первым днем месяца
    for _ in range(first_day):
        current_week.append(InlineKeyboardButton(text=" ", callback_data=f"{IGNORE_CALLBACK}"))
    for day in range(1, days_count + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        if available_dates and date_str in available_dates:
            text, callback = f"✔️{day}", f"date_{date_str}"
        elif fully_booked_dates and date_str in fully_booked_dates:
            text, callback = f"⛔{day}", f"{IGNORE_CALLBACK}"
        else:
            text, callback = f"📵{day}", f"{IGNORE_CALLBACK}"
        current_week.append(InlineKeyboardButton(text=text, callback_data=callback))
        if len(current_week) == 7:
            calendar_buttons.append(current_week)
            current_week = []
    while len(current_week) < 7:
        current_week.append(InlineKeyboardButton(text=" ", callback_data=f"{IGNORE_CALLBACK}"))
    if current_week:
        calendar_buttons.append(current_week)
    return calendar_buttons

def generate_time_slots_keyboard(available_times):
    """Создает список кнопок с временными слотами."""
    time_slots_buttons = []
    for time in available_times:
        if isinstance(time, dict):
            # Если available_times это список словарей из get_available_times
            time_slots_buttons.append(
                {"text": time["text"], "callback_data": time["callback_data"]}
            )
        else:
            # Если available_times это просто список строк
            time_slots_buttons.append(
                {"text": time, "callback_data": f"time_{time}"}
            )
    return time_slots_buttons

def create_back_button():
    """Создает кнопку возврата."""
    back_text, back_callback = next(iter(BACK_BUTTON.items()))
    return InlineKeyboardButton(text=back_text, callback_data=back_callback)

def create_calendar_keyboard(year, month, available_dates=None, fully_booked_dates=None):
    """
    Создает финальную клавиатуру календаря, объединяя заголовок, дни, ряд подтверждения и кнопку возврата.
    """
    available_dates = available_dates or {}
    fully_booked_dates = fully_booked_dates or {}
    # back_text, back_callback = next(iter(BACK_BUTTON.items()))
    header = generate_calendar_header(year, month)
    week_days = generate_week_days_header()
    days = generate_calendar_days(year, month, available_dates, fully_booked_dates)
    # back_row = create_back_button()

    if not available_dates:
        confirm = [InlineKeyboardButton(text=f"{NO_AVAILABLE_DATE_TEXT}", callback_data=f"{IGNORE_CALLBACK}")]
    else:
        confirm = [InlineKeyboardButton(text=f"{CHOICE_DATE_TEXT}", callback_data=f"{IGNORE_CALLBACK}")]

    keyboard_rows = [header] + [week_days] + days + [confirm] + [[create_back_button()]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

def create_date_confirmation_keyboard(date_str):
    """Создает финальную клавиатуру для подтверждения выбранной даты."""
    buttons = {
        CONFIRM_DATE_TEXT: f"{CONFIRM_DATE_CALLBACK_PREFIX}{date_str}",
        SELECT_DATE_TEXT: BACK_CALLBACK
    }
    return create_inline_universal_keyboard(buttons,)

def create_time_keyboard(available_times=None, row_width=4, additional_buttons=None):
    """Создает финальную клавиатуру для выбора времени."""
    if available_times is None:
        available_times = []

    # Генерируем кнопки с временными слотами
    keyboard_time_buttons = generate_time_slots_keyboard(available_times)

    # Создаем дополнительные кнопки
    if not available_times:
        confirm = {NO_AVAILABLE_TIME_TEXT: IGNORE_CALLBACK,
                   BACK_BUTTON_TEXT: BACK_CALLBACK
                   }
    else:
        confirm = {CHOICE_TIME_TEXT: IGNORE_CALLBACK,
                   BACK_BUTTON_TEXT: BACK_CALLBACK}

    # Используем универсальную функцию для создания клавиатуры
    return create_inline_universal_keyboard(keyboard_time_buttons, row_width, confirm)


def create_time_confirmation_keyboard(time_str):
    """Создает финальную клавиатуру для подтверждения выбранного времени."""
    buttons = {
        CONFIRM_TIME_TEXT: f"{CONFIRM_TIME_CALLBACK_PREFIX}{time_str}",
        SELECT_TIME_TEXT: BACK_CALLBACK,
    }
    return create_inline_universal_keyboard(buttons, row_width=1)

def create_confirmation_finish_booking_keyboard():
    """Создает финальную клавиатуру для подтверждения заказа."""
    builder = InlineKeyboardBuilder()
    builder.button(text=CONFIRM_ORDER_DETAILS_TEXT, callback_data=f"create_final_appointment")
    builder.button(text="❌Отмена", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()

