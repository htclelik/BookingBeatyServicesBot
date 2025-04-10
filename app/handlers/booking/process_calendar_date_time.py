from datetime import datetime, timedelta

import pytz
from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot_instance import bot
from app.config import BOOKING_CHAT_ID, TIMEZONE
from app.database.local_mini_db import INFO_LIST_MASTER
from app.scheduler_setup import add_job_to_scheduler
from app.states.state_manager import state_manager, validate_booking_data
from app.utils.appointments_utils import create_appointment
from app.utils.calendar_utils import update_calendar_display  # , update_selected_date
from app.utils.data_utils import get_calendar_id_for_master
from app.utils.formmaters import format_date_to_russian, format_duration, format_price
from app.utils.logger import setup_logger
from app.utils.sheets_utils import add_reminder_to_sheet  # Импорт функции добавления в таблицу

logger = setup_logger(__name__)
router = Router()


async def handle_calendar_navigation(callback_query: CallbackQuery, state: FSMContext):
    """Обработка навигации по календарю (вперёд/назад)"""
    logger.info("Навигация по календарю")

    try:
        # 1. Получаем текущие данные из состояния
        user_data = await state.get_data()
        logger.info(f"User data: {user_data}")
        current_year = user_data.get('current_year', datetime.now().year)
        logger.info(f"Current year: {current_year}")
        current_month = user_data.get('current_month', datetime.now().month)
        logger.info(f"Current month: {current_month}")

        # 2. Определяем направление навигации
        if callback_query.data == "prev":
            logger.info("Навигация влево")
            current_month -= 1
            if current_month < 1:
                current_month = 12
                current_year -= 1
        elif callback_query.data == "next":
            logger.info("Навигация вправо")
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        # 3. Сохраняем новые значения в состоянии
        await state.update_data(
            current_year=current_year,
            current_month=current_month
        )
        # 4. Обновляем отображение календаря
        await update_calendar_display(callback_query, state, current_year, current_month)
    except Exception as e:
        logger.error(f"Ошибка навигации: {e}")
        await callback_query.answer("Ошибка при переключении месяца", show_alert=True)


async def handle_date_selection(callback_query: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор даты.
    Из callback_query.data извлекается строка даты (например, "2025-03-29") из формата "date_YYYY-MM-DD",
    затем обновляется состояние и вызывается update_selected_date для отображения выбранной даты.
    """
    data = callback_query.data  # ожидаем, что data выглядит как "date_2025-03-29"
    try:
        _, date_str = data.split("_", 1) # разделяем и получаем "2025-03-29"
        logger.info(f"Выбрана дата: {date_str}")
    except ValueError:
        await callback_query.answer("Неверный формат даты.", show_alert=True)
        return False

    await state.update_data(date=date_str)
    await state_manager.handle_transition(callback_query.message, state, "next")
    return True

async def handle_calendar_button(callback_query: CallbackQuery, state: FSMContext):
    """Показывает календарь"""
    logger.info("Показывает календарь")
    logger.info("Нажата кнопка календаря")

    current_state = await state.get_state()
    logger.info(f"Current state: {current_state}")

    await update_calendar_display(callback_query, state)
    await state.update_data()
    await state_manager.handle_transition(callback_query.message, state, "next")
    await callback_query.answer("Подтвердите дату записи")
    return True


async def handle_confirm_date(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатывает подтверждение выбора даты"""
    logger.info("Этап: Подтверждение выбора даты")

    user_data = await state.get_data()
    date_str = user_data.get("date")
    logger.info(f"date_str: {date_str}")

    if not date_str:
        await callback_query.answer("❌Дата не выбрана", show_alert=True)
        return False

    logger.info(f"Выбрана дата: {date_str}")
    await state.update_data(confirmed_date=date_str)

    await state_manager.handle_transition(callback_query.message, state, "next")
    return True


async def handle_time_selection(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора времени и завершение записи"""
    logger.info("Этап: выбора времени записи")
    data = callback_query.data # получаем данные из callback_query
    logger.info(f"data: {data}") # выводим данные "time_18:00"
    try:
        _, time_str = data.split("_", 1)  # разделяем и получаем "2025-03-29"
        logger.info(f"Выбранное время: {time_str}")
        await state.update_data(time=time_str)
    except ValueError:
        await callback_query.answer("Неверный формат времени.", show_alert=True)
        return False

    await state_manager.handle_transition(callback_query.message, state, "next")
    return True


async def handle_confirm_time(callback_query: CallbackQuery, state: FSMContext):
    """Обрабатывает подтверждение времени (после нажатия кнопки confirm_time_...)"""
    logger.info("Этап: Подтверждение выбора времени (handle_confirm_time)")
    try:
        user_data = await state.get_data()
        time_str = user_data.get("time")
        logger.info(f"time_str: {time_str}")

        if not time_str:
            await callback_query.answer("❌Выберите дату и время записи", show_alert=True)
            return False

        logger.info(f"Подтверждено время: {time_str}")
        # Можно добавить флаг подтверждения, если нужно
        await state.update_data(confirmed_time=True)
        await state.update_data(time=time_str)
        await state_manager.handle_transition(callback_query.message, state, "next")
        await callback_query.answer()  # Ответить на колбэк, чтобы часы пропали
        return True

    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        await callback_query.answer(
            "⚠️ Произошла ошибка. Пожалуйста, попробуйте позже.",
            show_alert=True
        )
        return False


async def handle_create_event_calendar(callback_query: CallbackQuery, state: FSMContext):
    """Создает событие в календаре ПОСЛЕ нажатия финальной кнопки подтверждения И ПЛАНИРУЕТ НАПОМИНАНИЯ КЛИЕНТУ"""
    logger.info("Создание события в календаре в handle_create_event_calendar")
    await callback_query.answer("⏳ Создаем запись в календаре...и планируем напоминания...", show_alert=False)
    message_to_edit = callback_query.message  # Сохраняем сообщение
    try:
        # 1. Валидация данных (на всякий случай)
        valid, user_data = await validate_booking_data(state)
        if not valid:
            logger.error(f"Недостаточно данных для создания события: {user_data}")
            await callback_query.message.edit_text(
                f"❌ Ошибка: {user_data} Не удалось создать событие. Попробуйте начать заново /book.")
            await state.clear()
            return False

        # Получаем master_id сразу в начале функции
        master_id = user_data.get("master_id")
        general_chat_id = BOOKING_CHAT_ID
        name_user = callback_query.from_user.username
        id_user = callback_query.from_user.id



        # Убедимся что calendar_id точно есть
        if not user_data.get('calendar_id'):
            logger.error("Отсутствует calendar_id перед созданием события!")

            calendar_id = get_calendar_id_for_master(master_id)
            if not calendar_id:
                await callback_query.message.edit_text(
                    "❌ Ошибка: не удалось определить календарь мастера для создания события. Попробуйте начать заново /book.")
                await state.clear()
                return False
            await state.update_data(calendar_id=calendar_id)
            user_data = await state.get_data()  # Перезагружаем данные с calendar_id

        logger.info(f"Данные для создания события: {user_data}")

        # 2. Создание события в календаре
        calendar_event = create_appointment(user_data)  # create_appointment должна использовать calendar_id из user_data
        if not calendar_event:
            logger.error("Функция create_appointment не вернула событие.")
            await callback_query.message.edit_text(
                "❌ Ошибка: не удалось создать событие в календаре. Возможно, время уже занято или произошла ошибка API.")
            # Не очищаем state, чтобы пользователь мог попробовать снова или отменить
            return False

        # 3. Отправка уведомления мастеру
        event_link = calendar_event.get('htmlLink', 'Нет ссылки')
        google_event_id = calendar_event.get('id')  # ID события Google
        logger.info(f"Событие успешно создано: {event_link}, ID: {google_event_id}")


        if bot:  # Проверяем, что бот доступен
              # Используем ID мастера как Chat ID
            logger.info(f"Подготовка уведомления для мастера ")
            # --- Формируем текст уведомления ---
            try:
                total_duration = sum(int(s.get('duration', 60)) for s in user_data['services'])
                total_price = sum(int(s.get('price', 0)) for s in user_data['services'])
                service_names_list = [s.get('full_name_service', 'Неизвестная услуга') for s in user_data['services']]
                service_names_str = "\n - ".join(service_names_list)
                start_time = user_data.get('time').replace("time_", "")
                start_dt_obj = datetime.strptime(f"{user_data['date']} {start_time}", '%Y-%m-%d %H:%M')
                end_time = (start_dt_obj + timedelta(minutes=total_duration)).strftime('%H:%M')



                notification_body = (
                    f"🎉 <b>Новая запись!</b> 🎉\n\n"
                    f"<b>Мастер: {user_data['master_name']}</b>\n\n"
                    f"👤 <b>Клиент:</b> {user_data.get("name")}\n"
                    f"📞 <b>Телеграмм:</b> https://t.me/{user_data.get("phone")}\n"
                    # f"📧 <b>Email клиента:</b> {user_data.get('email', 'Не указан')}\n\n"
                    f"📅 <b>Дата:</b> {format_date_to_russian(user_data['date'])}\n"
                    f"⏰ <b>Время:</b> {start_time} - {end_time}\n"
                    f"⏱️ <b>Длительность:</b> {format_duration(total_duration)}\n\n"
                    f"💼 <b>Услуги:</b>\n - {service_names_str}\n\n"
                    f"💵 <b>Общая стоимость:</b> {format_price(total_price)}\n\n"
                    f"🔗 Событие в календаре: {event_link}"
                )
            except Exception as e:
                logger.error(f"Ошибка форматирования данных для уведомления: {e}")
                notification_body = f"⚠️ Новая запись создана ({event_link}), но не удалось сформировать детали. Проверьте календарь. Ошибка: {e}"
            # -----------------------------------

            # --- Отправка ---
            logger.info(f"Отправка уведомления мастеру в Telegram (Chat ID: {master_id})...")
            try:
                chat_master_id = master_id
                await bot.send_message(
                    chat_id=int(chat_master_id),  #(чат id -1002644497895)
                    text=notification_body,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                # Отправка уведомления в общий чат
                await bot.send_message(
                    chat_id=general_chat_id,  # chat_id общего чата
                    text=notification_body,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                logger.info(f"Уведомление успешно отправлено мастеру {master_id} и в общий чат{general_chat_id} в Telegram.")
            except TelegramAPIError as e:
                logger.error(f"Ошибка Telegram API при отправке мастеру {master_id} : {e}")
                # Можно добавить сообщение пользователю, что мастер не уведомлен
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при отправке мастеру {master_id} в Telegram: {e}",
                             exc_info=True)
                # Можно добавить сообщение пользователю
        else:
            logger.warning("Экземпляр 'bot' не найден. Не могу отправить уведомление мастеру в Telegram.")
            # Можно добавить сообщение пользователю, что мастер не уведомлен

        # # --- 4. ЛОГИРОВАНИЕ ЗАПИСИ В GOOGLE SHEETS ---
        # logger.info("Попытка логирования записи в Google Sheets...")
        # try:
        #     # Собираем данные для лога
        #     client_chat_id = callback_query.from_user.id
        #     # master_info = INFO_LIST_MASTER.get(int(master_id)) if master_id.isdigit() else None
        #     services_list = user_data.get('services', [])
        #     services_str = "\n".join(
        #         [s.get('full_name_service', '?') for s in services_list])  # Услуги через новую строку
        #     total_duration = sum(int(s.get('duration', 60)) for s in services_list)
        #     total_price = sum(int(s.get('price', 0)) for s in services_list)
        #     start_time_str = user_data.get('time', '').replace('time_', '')
        #     end_time_str = "N/A"  # Рассчитаем, если возможно
        #     appointment_date_str = user_data.get('date', '')
        #     try:  # Рассчет времени окончания
        #         start_dt_obj = datetime.strptime(f"{appointment_date_str} {start_time_str}", '%Y-%m-%d %H:%M')
        #         end_dt_obj = start_dt_obj + timedelta(minutes=total_duration)
        #         end_time_str = end_dt_obj.strftime('%H:%M')
        #     except ValueError as time_err:
        #         logger.error(f"Ошибка расчета времени окончания для логирования: {time_err}")
        #
        #     booking_log_data = {
        #         # BookingTimestamp добавится автоматически в функции
        #         'ClientChatID': client_chat_id,
        #         'ClientName': user_data.get('name', ''),
        #         'ClientPhone': user_data.get('phone', ''),
        #         'ClientEmail': user_data.get('email', ''),
        #         'MasterName': user_data.get('master_name', ''),
        #         'MasterID': master_id,
        #         'AppointmentDate': appointment_date_str,
        #         'StartTime': start_time_str,
        #         'EndTime': end_time_str,
        #         'Services': services_str,
        #         'TotalDurationMinutes': total_duration,
        #         'TotalPrice': total_price,
        #         'GoogleEventID': google_event_id or '',
        #         'GoogleCalendarLink': event_link or '',
        #         'Status': 'Confirmed'  # Начальный статус
        #     }
        #
        # except Exception as log_err:
        #     logger.error(f"Ошибка при подготовке или вызове логирования записи: {log_err}", exc_info=True)
        # # --- Конец Логирования ---

        # --- 5. ПЛАНИРОВАНИЕ НАПОМИНАНИЙ КЛИЕНТУ ---
        logger.info("Начало планирования напоминаний для клиента...")
        try:
            client_chat_id = callback_query.from_user.id
            # Убедимся, что time содержит только время HH:MM
            time_str_clean = user_data.get('time', '').replace('time_', '')
            appointment_dt_str = f"{user_data['date']}T{time_str_clean}:00"

            tz = pytz.timezone(TIMEZONE)
            now_aware = datetime.now(tz)
            # Создаем aware datetime
            appointment_dt = tz.localize(datetime.fromisoformat(appointment_dt_str))
            appointment_dt_iso = appointment_dt.isoformat()

            # Получаем доп. инфо о мастере
            master_info = INFO_LIST_MASTER.get(int(master_id)) if master_id.isdigit() else None
            master_name = user_data.get('master_name', 'Мастер')
            address = master_info.get('address', 'Уточните у мастера') if master_info else 'Адрес неизвестен'
            services_list = user_data.get('services', [])
            services_str = ', '.join(s.get('full_name_service', '?') for s in services_list)

            # --- Напоминание за 24 часа ---
            reminder_time_24h = appointment_dt - timedelta(hours=24)
            if reminder_time_24h > now_aware:  # Планируем, только если время не прошло
                text_24h = f"🔔 Напоминание! Завтра в {appointment_dt.strftime('%H:%M')} у Вас запись к мастеру {master_name}.\nУслуги: {services_str}.\nАдрес: {address}"
                job_id_24h = f"rem_24h_{client_chat_id}_{appointment_dt.strftime('%Y%m%d%H%M')}"
                reminder_data_24h = {
                    'job_id': job_id_24h, 'client_chat_id': client_chat_id,
                    'appointment_time_iso': appointment_dt_iso,
                    'reminder_time_iso': reminder_time_24h.isoformat(),
                    'reminder_type': '24h', 'status': 'PENDING',
                    'message_text': text_24h, 'google_event_id': google_event_id
                }
                sheet_row_24h = await add_reminder_to_sheet(reminder_data_24h)
                if sheet_row_24h:
                    add_job_to_scheduler(job_id_24h, reminder_time_24h, client_chat_id, text_24h, sheet_row_24h)
                else:
                    logger.error(f"Не удалось добавить напоминание 24ч для {job_id_24h} в таблицу.")
            else:
                logger.info(f"Время для напоминания за 24ч ({reminder_time_24h}) уже прошло. Пропуск планирования.")

            # --- Напоминание за 2 часа ---
            reminder_time_2h = appointment_dt - timedelta(hours=2)
            if reminder_time_2h > now_aware:  # Планируем, только если время не прошло
                text_2h = f"🔔 Напоминание! Через 2 часа ({appointment_dt.strftime('%H:%M')}) у Вас запись к мастеру {master_name}."
                job_id_2h = f"rem_2h_{client_chat_id}_{appointment_dt.strftime('%Y%m%d%H%M')}"
                reminder_data_2h = {
                    'job_id': job_id_2h, 'client_chat_id': client_chat_id,
                    'appointment_time_iso': appointment_dt_iso,
                    'reminder_time_iso': reminder_time_2h.isoformat(),
                    'reminder_type': '2h', 'status': 'PENDING',
                    'message_text': text_2h, 'google_event_id': google_event_id
                }
                sheet_row_2h = await add_reminder_to_sheet(reminder_data_2h)
                if sheet_row_2h:
                    add_job_to_scheduler(job_id_2h, reminder_time_2h, client_chat_id, text_2h, sheet_row_2h)
                else:
                    logger.error(f"Не удалось добавить напоминание 2ч для {job_id_2h} в таблицу.")
            else:
                logger.info(f"Время для напоминания за 2ч ({reminder_time_2h}) уже прошло. Пропуск планирования.")

        except Exception as e:
            logger.error(f"Ошибка при планировании напоминаний для chat_id={callback_query.from_user.id}: {e}",
                         exc_info=True)
            # Отправляем пользователю сообщение об ошибке планирования? Или просто логируем?
            # await callback_query.message.answer("Не удалось запланировать напоминания. Пожалуйста, запишите время самостоятельно.")
        # --- Конец планирования ---

        # 6. Редактируем сообщение для ПОЛЬЗОВАТЕЛЯ
        user_confirm_text = callback_query.message.text  # Исходный текст сводки
        await callback_query.message.edit_text(
            text=f"{user_confirm_text}" + "\n\n<b>✅ Запись успешно создана!\n⚠️Мастер уведомлен!\n📆Напоминания запланированы!.</b>",
            parse_mode="HTML",
            reply_markup=None,  # Убираем кнопки
            disable_web_page_preview=True
        )
        # 7. Переходим в финальное состояние
        logger.info("Переход в следующее состояние (finish)")
        await state_manager.handle_transition(callback_query.message, state, "next")

    except Exception as e:
        logger.error(f"Критическая ошибка в handle_create_event_calendar: {e}", exc_info=True)
        try:
            await callback_query.message.edit_text(
                f"❌ Произошла серьезная ошибка при обработке записи: {e}. Попробуйте позже.")
        except Exception as inner_e:
            logger.error(f"Не удалось даже отредактировать сообщение об ошибке: {inner_e}")
        await state.clear()  # Очищаем состояние при серьезной ошибке





