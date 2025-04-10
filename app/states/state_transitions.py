# app/state_management/state_transitions.py
from app.states.booking_states import BookingStates

STATE_TRANSITIONS = {
    "start": {"next": BookingStates.waiting_for_name_client.state},

    BookingStates.waiting_for_name_client.state: {
        "next": BookingStates.waiting_for_phone_client.state,
        "back": "start"
    },

    BookingStates.waiting_for_phone_client.state: {
        "next": BookingStates.waiting_for_master.state,  #waiting_for_email_client
        "back": BookingStates.waiting_for_name_client.state
    },
    #
    # BookingStates.waiting_for_email_client.state: {
    #     "next": BookingStates.waiting_for_master.state,
    #     "back": BookingStates.waiting_for_phone_client.state
    # },

    BookingStates.waiting_for_master.state: {
        "next": BookingStates.waiting_for_service.state,
        "back": BookingStates.waiting_for_phone_client.state  #waiting_for_email_client
    },
#__________________version2____transitions without waiting_for_service_confirmation_________
    # # Здесь переход с "waiting_for_service" сразу в "waiting_for_date"
    BookingStates.waiting_for_service.state: {
        "next": BookingStates.waiting_for_date.state,
        "back": BookingStates.waiting_for_master.state
    },

    BookingStates.waiting_for_date.state: {
        "next": BookingStates.waiting_confirm_date.state,
        "back": BookingStates.waiting_for_service.state  # или, если хотите, back из даты вернет в предыдущее состояние
    },
    BookingStates.waiting_confirm_date.state: {
        "next": BookingStates.waiting_for_time.state,
        "back": BookingStates.waiting_for_date.state  # или, если хотите, back из даты вернет в предыдущее состояние
    },

    BookingStates.waiting_for_time.state: {
        "next": BookingStates.waiting_confirm_time.state,
        "back": BookingStates.waiting_for_date.state
    },
    BookingStates.waiting_confirm_time.state: {
        "next": BookingStates.waiting_confirm_booking.state,
        "back": BookingStates.waiting_for_time.state
    },
    BookingStates.waiting_confirm_booking.state: {
        "next": BookingStates.waiting_creation_event_in_calendar.state,
        "back": BookingStates.waiting_for_time.state
    },
    BookingStates.waiting_creation_event_in_calendar.state: {
        "next": BookingStates.finish.state,
        "back": BookingStates.waiting_confirm_booking.state,
        "cancel": "start"
    },
    BookingStates.finish: {
    }
}
