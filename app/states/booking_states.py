from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):

    # Основные состояния

    waiting_for_name_client = State()
    waiting_for_phone_client = State()
    # waiting_for_email_client = State()
    waiting_for_master = State()
    waiting_for_service = State()
    waiting_for_date = State()
    waiting_for_time = State()


    # Состояние подтверждения услуг, дат и времени заказа
    waiting_for_service_confirmation = State()
    waiting_confirm_date = State()
    waiting_confirm_time = State()
    waiting_confirm_booking = State()
    waiting_creation_event_in_calendar = State()

    # Состояние завершения заказа
    finish = State()









