# dispatcher.py
# from functools import partial
from aiogram import Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

from app.handlers.ai_assistant.ai_response_handler import process_ai_question, start_ai_assistant_session_handler
from app.handlers.booking.process_calendar_date_time import handle_date_selection, \
    handle_time_selection, handle_confirm_date, handle_calendar_navigation, handle_calendar_button, handle_confirm_time, \
    handle_create_event_calendar
# from app.handlers.booking.process_email_client import process_user_email
from app.handlers.booking.process_name_client import start_booking, process_user_name  # , process_user_name
from app.handlers.booking.process_phone_client import process_user_phone
# from app.handlers.booking.process_phone_client import process_user_phone
from app.handlers.booking.process_selected_master_services import handle_master_selection, \
    handle_service_selection, handle_confirm_services
from app.handlers.common import start_handler, help_handler
from app.handlers.gift import gift_handler
from app.handlers.info import info_handler, master_info_handler
from app.handlers.navigation import universal_back_handler, universal_cancel_handler, universal_menu_callback
from app.states.booking_states import BookingStates
from app.states.conversation_states import ConversationStates
from app.utils.constants import ASSISTANT_START_COMMAND, BACK_BUTTON_MENU_CALLBACK, MENU_BUTTON_TEXT, ASSISTANT_START_BUTTON_TEXT, CANCEL_TEXT, CANCEL_CALLBACK, HELP_BUTTON_TEXT, START_CALLBACK, \
    HELP_CALLBACK
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router()



def setup_dispatcher(dp: Dispatcher): #bot: Bot
    """Регистрируем все обработчики команд и состояний"""

    # 📌 Общие команды
    router.message.register(start_handler, Command(START_CALLBACK))
    router.message.register(help_handler, Command(HELP_CALLBACK))
    router.message.register(help_handler, F.text == HELP_BUTTON_TEXT)

    router.message.register(universal_cancel_handler, F.text.casefold() == CANCEL_TEXT.casefold(), StateFilter(ConversationStates.waiting_for_question))
    router.message.register(universal_cancel_handler, Command(CANCEL_CALLBACK), StateFilter(ConversationStates.waiting_for_question))
    logger.info(
        f"AI Assistant: Зарегистрирован текст '{CANCEL_TEXT}' для отмены в состоянии {ConversationStates.waiting_for_question.state}.")
    router.callback_query.register(universal_back_handler, F.data == "back", StateFilter("*"))
    router.callback_query.register(universal_back_handler, F.text == "🔙Назад", StateFilter("*"))

    # 💬🤖 Общение с ИИ-ассистентом
    # router.message.register(universal_cancel_handler, F.data == "cancel", StateFilter("*"))
    router.message.register(start_ai_assistant_session_handler, StateFilter(default_state), Command(ASSISTANT_START_COMMAND))
    router.message.register(start_ai_assistant_session_handler, StateFilter(default_state), F.text == ASSISTANT_START_BUTTON_TEXT)
    router.message.register(start_ai_assistant_session_handler, StateFilter(default_state), F.text == ASSISTANT_START_BUTTON_TEXT, ~F.text.startswith('/'),)
    router.message.register(process_ai_question, StateFilter(ConversationStates.waiting_for_question),F.text, ~Command("cancel"), ~(F.text.casefold() == CANCEL_TEXT.casefold())
                            )
    logger.info(
        f"AI Assistant: Зарегистрирован обработчик вопросов в состоянии {ConversationStates.waiting_for_question.state}.")


    # ℹ️ Информация
    router.message.register(info_handler, Command("info"))
    router.message.register(info_handler, F.text == "ℹ️Информация о нас:👩‍🦰🧔🏻‍♂️Мастера, 🛠️💅💇‍♂️👨‍💻Услуги")
    router.callback_query.register(master_info_handler, F.data.startswith("master_"))

    # 📆 Запись (Начало процесса)
    router.message.register(start_booking, Command("book"))
    router.message.register(start_booking, F.text == "📆Записаться на удобное время")


    router.callback_query.register(universal_menu_callback, F.data == BACK_BUTTON_MENU_CALLBACK)
    router.message.register(process_user_name, StateFilter(BookingStates.waiting_for_name_client))
    router.message.register(process_user_phone, StateFilter(BookingStates.waiting_for_phone_client))
    # router.message.register(process_user_email, StateFilter(BookingStates.waiting_for_email_client))

    # 🔘 Обработка inline-кнопок процесса бронирования
    router.callback_query.register(handle_master_selection, F.data.startswith("booking_master_"))
    router.callback_query.register(handle_service_selection, F.data.startswith("service||"))
    router.callback_query.register(handle_confirm_services, F.data == "confirm_services")

    router.callback_query.register(handle_date_selection, F.data.startswith("date_"))
    router.callback_query.register(handle_calendar_navigation, F.data.in_(["prev", "next"]))
    router.callback_query.register(handle_calendar_button, Command("calendar"))

    router.callback_query.register(handle_confirm_date, F.data.startswith("confirm_date_"))
    router.callback_query.register(handle_time_selection, F.data.startswith("time_"))
    router.callback_query.register(handle_confirm_time, F.data.startswith("confirm_time_"))
    router.callback_query.register(
        handle_create_event_calendar,  # Просто имя функции
        F.data == "create_final_appointment"
    )

    # 🎁 Акции
    router.message.register(gift_handler, Command("gift"))
    router.message.register(gift_handler, F.text == "🎁Акции, Подарки")

    logger.info("Все обработчики бота успешно зарегистрированы")
    dp.include_router(router)
