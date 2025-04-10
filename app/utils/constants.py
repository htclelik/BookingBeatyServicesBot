
from app.utils.formmaters import format_price
from app.database.local_mini_db import WORK_AREA_LIST, INFO_LIST_MASTER, MASTER_SERVICES_FULL, MASTERS_ID

#_________________________________Имя и рабочие области бота
SPECIALIST_NAME = "Ася"

DB = (
    f"{INFO_LIST_MASTER} и/или {WORK_AREA_LIST} и/или {MASTERS_ID} и/или {MASTER_SERVICES_FULL}"
)

#_________________________________ Бонусы и подарки__________________________________________________________

BONUS_FIRST = 100
BONUS_BIRTHDAY = 100

#__________________________________ Шаблоны текста____________________________________________________________

ASSISTANT_START_COMMAND = "assistant"
ASSISTANT_START_BUTTON_TEXT = "💬Общение с ассистентом"
START_TEXT = (
    f" Ваш консультант и администратор <b>{SPECIALIST_NAME}</b>.\n\n "
    f" Вы можете использовать Доступные команды:\n"
    "<b>/start</b> - 🏁Начало работы\n\n"
    f"<b>/assistant</b> - {ASSISTANT_START_BUTTON_TEXT}\n\n"
    "<b>/info</b> - ℹ️Информация о нас:👩‍🦰🧔🏻‍♂️Мастера, 🛠️💅💇‍♂️👨‍💻Услуги\n\n"
    "<b>/book</b> - 📆Записаться на удобное время \n\n\n"
    "<b>/gift</b> - 🎁Акции, Подарки\n\n"
    "<i>/help</i> - 🛟Обратиться в тех.поддержку \n"
)
CANCEL_TEXT = (
    "🚫Отмена! Вы можете начать заново, используя используя доступные команды или кнопки.\n"
)

FEEDBACK_TEXT = (
f"Пожалуйста, напишите ваши пожелания, замечания или опишите проблему:\n"
)

FEEDBACK_THANK_TEXT = (
f"Спасибо за ваш отзыв! Мы учтем ваши пожелания.\n\n"
)

WELCOME_TEXT = (
    f"Привет - я <b>Ася</b> ваш интеллектуальный помощник и администратор\n"
    f"Пожалуйста, введите ваш вопрос 🖍️для начала диалога, и я постараюсь на него ответить.\n"
    f"Вы можете задать вопрос по работе мастеров или записаться на услугу:"
)

# Личный Telegram
support_telegram_url = "https://t.me/@futurestreamtechnicalsupport_bot"
support_telegram_html = f"💬 <a href='{support_telegram_url}'>Написать в поддержку</a>" if support_telegram_url else "Контакт Telegram не указан"

HELP_TEXT = (
    f"🛟Связаться с поддержкой, 💬написать отзыв или ❔задать вопрос:\n"
    f"Пожалуйста, ✒️напишите ваши пожелания, замечания или опишите проблему:\n\n{support_telegram_html}"
)



PROMOTIONS_TEXT = (

    f"👋<b>Мы очень ценим вас 💝 </b>\n"
    f"и рады сообщить 📣, об <b>подарках</b> 🎁 для вас :\n\n"
    f"🟢<i>🚀При первом посещении 🙋‍♀️нашего <b>мастера</b> \n"
    f"мы предоставляем  💰скидку в размере:</i> <b>{format_price(BONUS_FIRST)}</b> \n\n"
    f"🟣<b>🥳День вашего рождения</b> - это 🎊праздник и 🎈для нас ,\n "
    f"мы предоставляем 💰скидку в размере: <b>{format_price(BONUS_BIRTHDAY)}</b> \n\n"

)


STEP_ENTER_NAME = (
    "✏️Введите пожалуйста ваше имя:\n\n"
)

STEP_ENTER_PHONE = (
"📞 Введите номер телефона 10 цифр без 8 и +7 :\n\n"
)

STEP_ENTER_EMAIL = (
    f"📧Введите email: (например, example@domain.com)\n\n"

)

STEP_SELECT_MASTER = (
    f"✔️Выберите <b>мастера:</b>\n\n"
)
STEP_SELECT_SERVICES = (
    f"✔️Выберите <b>услугу:</b>\n\n"
)

STEP_SELECT_DATE = (
f"✔️Выберите <b>📅дату:</b>\n"
)
STEP_CONFIRM_DATE = (
f"✅Подтвердите выбранную <b>📅дату:</b>\n"
)

STEP_SELECT_TIME = (
f"✔️Выберите <b>⏰время:</b>\n\n"
)
STEP_CONFIRM_TIME = (
f"✅Подтвердите выбранное <b>⏰время:</b>\n\n"
)


HELLO = (
    "👋Здравствуйте"
)
THANKS = (
    "✅Спасибо за предоставление данных"
)
CHOICE_CONFIRM_TEXT = (
    "✅Вы выбрали"
)
BOOK_CONFIRM_TEXT = (
    "✅Запись подтверждена!\n"
)
STEP_BACK = (
"вернуться назад /back\n"
)

# Кнопка подтверждения заказа
CONFIRM_ORDER_DETAILS_TEXT = "✅Подтвердить данные заказа\n "
FINISH_TEXT = (
f"🙏 Спасибо за запись!\n"f"✅ Мы уведомили мастера о вашем визите.\n"f"💬По всем вопросам используйте /help"
)

# Кнопка подтверждения выбора услуг мастера
CONFIRM_SERVICES_DETAILS_TEXT= "✅Подтвердить выбор услуг"

# Тексты кнопок
NO_AVAILABLE_TIME_TEXT = "🔴Нет доступного времени"
NO_AVAILABLE_DATE_TEXT = "🔴Нет доступных дат"
CHOICE_TIME_TEXT = "Выберите время"
CHOICE_DATE_TEXT = "Выберите дату"
CONFIRM_TIME_TEXT = "✅Подтвердить время"
CONFIRM_DATE_TEXT = "✅Подтвердить дату"
SELECT_TIME_TEXT = "⏰Выбрать время"
SELECT_DATE_TEXT = "📆Выбрать дату"
BACK_BUTTON_TEXT = "🔙Назад"
HELP_BUTTON_TEXT = "🛟Связаться с поддержкой"
CANCEL_TEXT = "❌Отмена"
MENU_BUTTON_TEXT = "🏚️Главное меню"


#______________________________________ Список кнопок______________________________________________________
CUSTOM_BUTTONS = [
        "ℹ️Информация о нас:👩‍🦰🧔🏻‍♂️Мастера, 🛠️💅💇‍♂️👨‍💻Услуги",
        "💬Общение с ассистентом",

        "📆Записаться на удобное время",
        "🎁Акции, Подарки", "🛟Связаться с поддержкой"
    ]


BACK_BUTTON = {"🔙Назад": "back"}


# Остальные кнопки
CALENDAR_BUTTON = {"📆Календарь": "calendar"}
CONFIRM_DATE_BUTTON = {"✅Подтвердить дату": "confirm_date"}
CONFIRM_TIME_BUTTON = {"✅Подтвердить время": "confirm_time"}


# callback_data for button
CONFIRM_TIME_CALLBACK_PREFIX = "confirm_time_"
CONFIRM_DATE_CALLBACK_PREFIX = "confirm_date_"
CONFIRM_BOOKING_CALLBACK_PREFIX = "confirm_booking"
CONFIRM_SERVICES_CALLBACK_PREFIX = "confirm_services"
IGNORE_CALLBACK = "ignore"
BACK_CALLBACK = "back"
CALENDAR_CALLBACK = "calendar"
START_CALLBACK = "start"
HELP_CALLBACK = "help"
CANCEL_CALLBACK = "cancel"
BACK_BUTTON_MENU_CALLBACK = "back_menu"




#________________________________________Определяем схему расположения кнопок__________________________________
LAYOUT_CUSTOM_212_BUTTON = [2, 1, 2]
LAYOUT_CUSTOM_112_BUTTON = [1, 1, 2]  # 2 кнопки в первой строке, 1 во второй, 2 в третьей
LAYOUT_CUSTOM_12_BUTTON = [1, 2]  # 1 кнопка в первой строке, 2 во второй, 1 в третьей
LAYOUT_1_BUTTON = [1]  # 1 кнопки в первой строке


