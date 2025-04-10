
from app.config import MASTERS_ID

WORK_AREA_LIST = """
    "Маникюр",
    "Педикюр",
    "Обработка стоп",
    "Уход за руками",
    "Гигиена при работе с инструментами при аппаратном маникюре и педикюре",
    "Мужские стрижки",
    "Стрижки мальчиков"
    "Прически и борода",
    "Уход за бородой"
"""

# Информация о мастерах
INFO_LIST_MASTER = {
    MASTERS_ID[0]: {
        # "master_id": MASTERS_ID[0],
        "name_master": "Наташа",
        "photo_url": "https://drive.google.com/uc?export=view&id=16FnOsps0U-PqNGkujKTbi5vEgQcUjFuF",#"static/master_nata.jpg", # 🔥 Ссылка на фото
        "welcome_short_text": "👩‍🦰Здравствуйте, мои дорогие,\n меня зовут ",
        "brief_about_me": "💅мастер по маникюру и педикюру.",
        "what your services mean": f"Ухоженные ногти-👌успех женской красоты 💐.\n\n"
                                   f"💅🏻Маникюр подчеркивает аккуратность и изящность ваших рук, а также выражает имидж 👸🏼\n"
                                   f"💅Я делаю ваши ручки красивыми и неотразимыми 🥰:",
        "work_area": "💅Маникюр, Педикюр, Обработка стоп, Уход за руками",
        "experience": "2 года",
        "city": "Анапа",
        "address": "СОТ Колос ул.Сосновая 102 \nhttps://yandex.ru/maps/-/CDcP740h",
        "my_telegram": "https://t.me/@NataliaDalke",
        "cl_telegram": "https://t.me/+Ml50f9jh2_Y3YWIy",
        "email": "ntldalke@gmail.com",
        "vk_club": "https://vk.com/club226697253",
        "work_start_hour": 9,
        "work_end_hour": 18,
        "work_days": "Вт-Вс",
        "weekend": "Пн"  # "Сб, Вс"
    },
MASTERS_ID[1]: {
        # "master_id": MASTERS_ID[1],
        "name_master": "Виктор",
        "photo_url": "https://drive.google.com/uc?export=view&id=1zB0s990u-v4IzJVrhiY2l3FZPAGgH8vf",#"static/Виктор.jpeg",
        "welcome_short_text": "👋Всем привет, с вами всегда на контакте 📶",
        "brief_about_me": f"💇‍♂️🧔🏻‍♂️- Специалист по мужским прическам и бороде,\n"
                          f"от Классики и Полубокса к конечно современный Фейд,\n"
                          f"создание различных образов и множество переходов с добавлением современного шарма,\n"
                          f"плавный и стильный переход от короткого к длинному, создам придавая четкость и объем\n "
                          f"выполню работу с идеальной точностью для тех, кто ценит комфорт и практичность без ущерба стилю\n"
                          f"кто хочет сохранить длину и подчеркнуть индивидуальность\n"
                          f"Подведение контуров - финальные штрихи для Идеального образа\n",
        "what your services mean": f"Ваша прическа и борода - это лицо вашего стиля,\n"
                                   f"ведь они создают первое впечатление,\n"
                                   f"отражая вашу индивидуальность и характер.\n"
                                   f"Каждый волос может рассказать историю,\n"
                                   f"а каждый штрих - подчеркнуть уверенность в себе.\n"
                                   f"В прическе и бороде кроется сила,\n"
                                   f"открывающая тайны индивидуальности,\n"
                                   f"способная очаровать и вдохновить окружающих.\n"
                                   f"Сделайте эти детали своими союзниками\n"
                                   ,

        "work_area": "Мужские стрижки, стрижки мальчиков, прически и борода, уход за бородой",
        "experience": "1 год",
        "city": "Анапа",
        "address": "СОТ Колос ул.Сосновая 102 \nhttps://yandex.ru/maps/-/CDcP740h",
        "my_telegram": "https://t.me/+79009839979",
        "cl_telegram": "Скоро будет",
        "email": "vikdal110@gmail.com",
        "vk_club": "https://vk.com/club229861805, \n\n "
                   "",
        "work_start_hour": 9,
        "work_end_hour": 19,
        "work_days": "Вт-Вс",
        "weekend": "Пн" #"Сб, Вс"

    },
# MASTERS_ID[2]: {
#         # "master_id": MASTERS_ID[1],
#         "name_master": "Алексей",
#         "photo_url": "/Users/leik.van-23/PycharmProjects/BookingBeatyServicesBot/app/static/photo_bot_01.jpeg",
#         "welcome_short_text": "👋Всем привет, с вами всегда на 🛜связи",
#         "brief_about_me": f"💇‍♂️🧔🏻‍♂️- Специалист по ерунде,\n",
#
#         "what your services mean":
#                                    f"Сделайте эти детали своими союзниками\n"
#                                    ,
#
#         "work_area": "разработка телеграмм бота",
#         "experience": "1 год",
#         "city": "Анапа",
#         "address": "СОТ Колос ул.Сосновая 102 \nhttps://yandex.ru/maps/-/CDcP740h",
#         "my_telegram": "https://t.me/+79222756869",
#         "cl_telegram": "Скоро будет",
#         "email": "htclelik@gmail.com",
#         "vk_club": "https://vk.com/club228274205, \n\n "
#                    "",
#         "work_start_hour": 9,
#         "work_end_hour": 18,
#         "work_days": "Вт-Сб",
#         "weekend": "Пн, Вс"
#
#     },
}


DEFAULT_SESSION_DURATION = 60

# Соответствие мастеров и услуг, которые они предоставляют, включая стоимость


MASTER_SERVICES_FULL = {
    MASTERS_ID[0]: {
        "mncr01":{"full_name_service":"1️⃣🫳Маникюр без покрытия", "price": 500, "duration": 90,"select": False},
        "mncr02":{"full_name_service":"2️⃣💅Маникюр c покрытием", "price": 800, "duration": 150,  "select": False},
        "pdcr01":{"full_name_service":"3️⃣📍Педикюр без покрытия", "price": 600, "duration": 90, "select": False},
        "pdcr02":{"full_name_service":"4️⃣📍💅Педикюр с покрытием", "price": 900, "duration": 150, "select": False},
        "pdcr11":{"full_name_service":"5️⃣📍🦶Педикюр без покрытия с обработкой стопы", "price": 900, "duration": 150,"select": False},
        "pdcr12":{"full_name_service":"6️⃣📍💅🦶Педикюр с покрытием с обработкой стопы", "price": 1200, "duration": 180, "select": False},
        "mtng00":{"full_name_service":"7️⃣🙋‍♀️Знакомство с мастером", "price": 0, "duration": 30, "select": False},

    },
MASTERS_ID[1]: {
        "hrct01":{"full_name_service":"1️⃣📍💇‍♂️Стрижка классическая", "price": 700, "duration": 45,"select": False},
        "hrct02":{"full_name_service":"2️⃣📍Фейд", "price": 700, "duration": 60,  "select": False},
        "hrct03":{"full_name_service":"3️⃣📍Полубокс", "price": 900, "duration": 30, "select": False},
        "hrct04":{"full_name_service":"4️⃣📍Удлиненная стрижка", "price": 1000, "duration": 60, "select": False},
        "brd01":{"full_name_service":"5️⃣📍🧔🏻‍♂️Стрижка бороды", "price": 300, "duration": 30,"select": False},
        "brd11":{"full_name_service":"6️⃣📍🧔🏻Подведение контуров шаветкой", "price": 200, "duration": 15, "select": False},
        "brd02":{"full_name_service":"7️⃣📍👨🏻‍🦲Бритье шаветкой", "price": 500, "duration": 30, "select": False},
        "mtng01":{"full_name_service":"8️⃣👨️Знакомство с мастером", "price": 0, "duration": 30, "select": False}
    },
# MASTERS_ID[2]: {
# "tg01":{"full_name_service":"1️⃣Разработка TG с ИИ", "price": 70000, "duration": 60, "select": False},
# "tg02":{"full_name_service":"2️⃣Разработка TG low_code", "price": 30000, "duration": 120, "select": False},
# "webf01":{"full_name_service":"3️⃣Web приложение Flask", "price": 350000, "duration": 90, "select": False},
# "site01":{"full_name_service":"4️⃣Разработка сайта no_code", "price": 900, "duration": 180, "select": False},
# "cnsltnt01":{"full_name_service":"5️⃣Консультация first", "price": 0, "duration": 30, "select": False},
# "cnsltnt02":{"full_name_service":"6️⃣Консультация", "price": 1800, "duration": 60, "select": False}
#
# }
}


