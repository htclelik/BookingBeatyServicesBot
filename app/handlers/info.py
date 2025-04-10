# app/handlers/info.py
# Команды /info , кнопка "О нас"
from aiogram import Router, types, Bot
from aiogram.types import FSInputFile, URLInputFile

from app.database.local_mini_db import MASTER_SERVICES_FULL, INFO_LIST_MASTER
from app.keyboards.inline import create_inline_universal_keyboard  # get_masters_keyboard, get_services_keyboard,
from app.keyboards.reply import create_custom_keyboard
from app.utils.constants import CUSTOM_BUTTONS, BACK_BUTTON, LAYOUT_CUSTOM_212_BUTTON
from app.utils.formmaters import format_price, format_duration, format_duration_minutes
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = Router()

# 🔹 Обработчик команды /info
async def info_handler(message: types.Message):
    user_name = message.from_user.first_name
    masters = {master["name_master"]: f"master_{master_id}" for master_id, master in INFO_LIST_MASTER.items()}
    # buttons = {**masters,**BACK_BUTTON}

    await message.answer(
        f"<b>{user_name}</b>, \nдля получения информации выберите мастера ниже:\n"
        f"Наши мастера специалисты в своих областях:\n\n\n"
        f"<b>Маникюр и педикюр</b>: мастер <b>Наташа</b>\n\n"
        f"<b>Мужские стрижки</b>(прическа и борода): мастер <b>Виктор</b>\n\n",
        parse_mode="HTML",
        reply_markup=create_inline_universal_keyboard(masters, 1)
    )



# 🔹 Обработчик выбора мастера
async def master_info_handler(callback_query: types.CallbackQuery, bot: Bot):
    master_id = int(callback_query.data.split('_')[1])
    master = INFO_LIST_MASTER.get(master_id)
    services = MASTER_SERVICES_FULL.get(master_id, {})

    if master:
        services_text = ""
        for service_category, service_details in services.items():
            price = service_details["price"]
            duration = service_details["duration"]
            formatted_price = format_price(price)
            formatted_duration = format_duration(duration)
            formatted_duration_minutes = format_duration_minutes(duration)
            services_text += (
                f"\n🔹 <b>{service_details["full_name_service"].capitalize()}</b>:\n"
                f" -💵Цена услуги:- {formatted_price}\n"
                f" - {formatted_duration} {formatted_duration_minutes}\n"
            )

        # Адрес
        address_raw = master.get('address', 'Адрес не указан')
        address_html = f"<b>{address_raw}</b>"  # По умолчанию просто жирный текст
        if '\n' in address_raw:
            parts = address_raw.split('\n', 1)
            text_part = parts[0].strip()
            url_part = parts[1].strip()
            # Проверяем, что вторая часть похожа на URL
            if url_part.startswith('http'):
                address_html = f"<b>{text_part}</b> <a href='{url_part}'>🗺️ Показать на карте 🏠</a>"
            # Если вторая часть не URL, оставляем как было (весь текст жирным)

        # Личный Telegram
        telegram_url = master.get('my_telegram')
        telegram_html = f"💬 <a href='{telegram_url}'>Написать в Telegram</a>" if telegram_url else "Контакт Telegram не указан"

        # Email
        email_address = master.get('email')
        email_html = f"📩 <a href='mailto:{email_address}'>{email_address}</a>" if email_address else "Email не указан"

        # Канал/Группа Telegram
        channel_url = master.get('cl_telegram')
        channel_html = f"📢 <a href='{channel_url}'>Канал/Группа в Telegram</a>" if channel_url else "Канал Telegram не указан"

        # Группа VK
        vk_url = master.get('vk_club')
        # Убираем лишние переносы строк и пробелы из URL VK, если они есть
        vk_url_cleaned = vk_url.strip().replace('\n', '').replace(' ', '') if vk_url else None
        vk_html = f"🌍 <a href='{vk_url_cleaned}'>Группа ВКонтакте</a>" if vk_url_cleaned else "Группа VK не указана"


        about_me_text = (
            f"{master['what your services mean']}.\n\n"
            f"🪩 Моя область работы: {master['work_area']}\n"
            f"📍 Мой опыт работы: {master['experience']}\n"
            f"📍 Мой любимый город: <b>{master['city']}</b>\n\n"
            f"📅 Мой график работы: с <b>{master['work_start_hour']}</b> до <b>{master['work_end_hour']}</b>\n"
            f"   Выходные: <b>{master.get('weekend', 'По запросу')}</b>\n\n"  # Добавим .get для выходных
            # Используем отформатированный адрес
            f"🏡 Вы можете увидеть меня на рабочем месте в уютном месте по адресу:\n{address_html}\n\n\n"
            # Используем отформатированные контакты
            f"📲 Я на связи с вами:\n{telegram_html}\n\n"
            f"📍Можете написать мне на почту:\n{email_html}\n\n"
            f"\n{channel_html}\n\n" #📢 Канал в Telegram:
            f"🌠 Вы можете ознакомиться с <b>моими работами</b>:\n{vk_html}\n\n"
        )

        services_list_text = (
            f"Я предлагаю вам <b>📍следующие услуги:👇</b>\n{services_text}"
        )

        # Используем FSInputFile для отправки локального файла
        # photo = FSInputFile(master["photo_url"])
        # photo_url = f"https://drive.google.com/uc?export=view&id={file_id}"
        photo = URLInputFile(master["photo_url"])

        try:
            short_caption = f"{master['welcome_short_text']} <b>{master['name_master']}</b>\n{master['brief_about_me']}"
            await bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo, caption=short_caption,
                                 parse_mode="HTML")
            await bot.send_message(chat_id=callback_query.message.chat.id, text=about_me_text, parse_mode="HTML", disable_web_page_preview=True)
            await bot.send_message(chat_id=callback_query.message.chat.id, text=services_list_text, parse_mode="HTML",
                                   reply_markup=create_custom_keyboard(CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON), disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Ошибка при отправке информации о мастере: {e}")
            await callback_query.answer("Ошибка отправки информации о мастере!", show_alert=True)

        # Удаляем старое сообщение (опционально)
        await callback_query.message.delete()
    else:
        await callback_query.answer("Мастер не найден.", show_alert=True)


