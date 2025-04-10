# # app/state_management/state_manager.py
from datetime import datetime, timedelta
from typing import Dict, Callable, Awaitable

from aiogram import types
from aiogram.fsm.context import FSMContext

from app.database.local_mini_db import INFO_LIST_MASTER
# from app.handlers.booking.process_calendar_date_time import validate_booking_data
from app.keyboards.calendar_kb import create_date_confirmation_keyboard, create_time_keyboard, \
    create_time_confirmation_keyboard, create_confirmation_finish_booking_keyboard
from app.keyboards.inline import create_inline_universal_keyboard
from app.keyboards.reply import create_custom_keyboard
from app.states.booking_states import BookingStates
from app.states.state_transitions import STATE_TRANSITIONS
from app.utils.calendar_utils import get_calendar_data, get_time_calendar_data, create_calendar_keyboard
from app.utils.constants import (
    STEP_ENTER_NAME,
    STEP_ENTER_PHONE,
    STEP_SELECT_MASTER,
    STEP_SELECT_SERVICES,
    STEP_SELECT_DATE,
    STEP_SELECT_TIME,
    CONFIRM_ORDER_DETAILS_TEXT,
    CUSTOM_BUTTONS, FINISH_TEXT,
    LAYOUT_CUSTOM_212_BUTTON, STEP_CONFIRM_DATE, STEP_CONFIRM_TIME, BACK_BUTTON, MENU_BUTTON_TEXT, BACK_BUTTON_MENU_CALLBACK
)
from app.utils.data_utils import get_calendar_id_for_master
from app.utils.formmaters import format_date_to_russian, format_duration, format_price
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def validate_booking_data(state: FSMContext):
    """Проверяет, заполнены ли все необходимые данные"""
    user_data = await state.get_data()
    required_fields = ['date', 'time', 'master_id', 'services', 'calendar_id', 'name', 'phone', 'master_name'] # 'name', 'phone',

    if not all(field in user_data for field in required_fields):
        return False, "❌ Ошибка: недостаточно данных. Начните заново."

    return True, user_data


class StateManager:
    """
    Класс для управления переходами между состояниями бронирования.

    Обоснование:
      - Централизованное управление состояниями позволяет легко отслеживать логику переходов.
      - Разделение логики для каждого шага (например, ввод имени, телефона, выбор мастера) упрощает сопровождение и тестирование.
      - Использование единственного метода для обработки переходов снижает вероятность ошибок при добавлении новых состояний.
    """

    def __init__(self):
        # Регистрируем обработчики для состояний, если потребуется расширение функционала.
        self.state_handlers: Dict[str, Dict[str, Callable[[types.Message, FSMContext], Awaitable[None]]]] = {}

    def register_state(self, state_name: str, entry_handler: Callable[[types.Message, FSMContext], Awaitable[None]]):
        """
        Регистрирует обработчик для конкретного состояния.
        Обоснование: Позволяет динамически добавлять новые обработчики без изменения основной логики переходов.
        """
        self.state_handlers[state_name] = {"entry": entry_handler}

    async def handle_transition(self, msg: types.Message, state: FSMContext, action: str = "next"):
        """
        Централизованная обработка переходов между состояниями.

        Обоснование:
          - Позволяет управлять переходами (например, вперед или назад) в одном месте.
          - Облегчает отслеживание и логирование переходов для дальнейшей отладки.
        """
        current_state = await state.get_state()
        if current_state is None:
            logger.error("Текущее состояние не установлено.")
            return  # Если состояние не установлено, выходим

        # Обработка нажатия кнопки "назад"
        if action == "back":
            previous_state = STATE_TRANSITIONS.get(current_state, {}).get("back")
            if previous_state:
                await state.set_state(previous_state)
                logger.info(f"Переход назад: {current_state} -> {previous_state}")
                await self._handle_state_entry(msg, state, previous_state)
                return

        # Переход к следующему состоянию по умолчанию
        next_state = STATE_TRANSITIONS.get(current_state, {}).get(action)
        if not next_state:
            logger.warning(f"Нет перехода для действия '{action}' из состояния '{current_state}'")
            return

        await state.set_state(next_state)
        logger.info(f"Переход: {current_state} -> {next_state} по действию '{action}'")
        await self._handle_state_entry(msg, state, next_state)


    async def _handle_state_entry(self, msg: types.Message, state: FSMContext, next_state: str):
        """
        Вызывает обработчик для нового состояния.

        Обоснование:
          - Разделение логики входа в состояние позволяет легко изменять поведение для каждого шага.
          - Если обработчик для нового состояния не найден, это логируется для дальнейшей диагностики.
        """
        handlers = {
            BookingStates.waiting_for_name_client: self._handle_name_entry,
            BookingStates.waiting_for_phone_client: self._handle_phone_entry,
            # BookingStates.waiting_for_email_client: self._handle_email_entry,
            BookingStates.waiting_for_master: self._handle_master_selection,
            BookingStates.waiting_for_service: self._handle_service_selection,
            # BookingStates.waiting_for_service_confirmation: self._handle_confirm_services,
            BookingStates.waiting_for_date: self._handle_date_selection,
            BookingStates.waiting_confirm_date: self._handle_confirm_date,
            BookingStates.waiting_for_time: self._handle_time_selection,
            BookingStates.waiting_confirm_time: self._handle_confirm_time,
            BookingStates.waiting_confirm_booking: self._handle_confirm_booking,
            BookingStates.waiting_creation_event_in_calendar: self._handle_creation_event_in_calendar,
            BookingStates.finish: self._handle_finish,

        }
        handler = handlers.get(next_state)
        if handler:
            await handler(msg, state)
        else:
            logger.error(f"Обработчик для состояния {next_state} не найден.")

    async def _handle_name_entry(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния ожидания ввода имени.

        Обоснование:
          - Изолированный метод для ввода имени облегчает модификацию или расширение логики данного шага.
        """

        await msg.answer(
            STEP_ENTER_NAME,
            parse_mode="HTML",
            reply_markup=create_inline_universal_keyboard({MENU_BUTTON_TEXT: BACK_BUTTON_MENU_CALLBACK}, 1)

        )

    async def _handle_phone_entry(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния ожидания ввода телефона.

        Обоснование:
          - Выводит сообщение с просьбой ввести телефон и кнопкой "назад", что улучшает навигацию для пользователя.
        """
        user_data = await state.get_data()
        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_ENTER_PHONE}",
            parse_mode="HTML",
            reply_markup=create_inline_universal_keyboard(BACK_BUTTON, 1)
        )

    # async def _handle_email_entry(self, msg: types.Message, state: FSMContext):
    #     """
    #     Обработка состояния ожидания ввода email.
    #
    #     Обоснование:
    #       - Подобно предыдущему шагу, изолированный метод позволяет легко изменять сообщение или клавиатуру.
    #     """
    #     user_data = await state.get_data()
    #     await msg.answer(
    #         f"{user_data.get('name', 'Пользователь')}, {STEP_ENTER_EMAIL}",
    #         reply_markup=create_inline_universal_keyboard(BACK_BUTTON, 1)
    #     )

    async def _handle_master_selection(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния выбора мастера.

        Обоснование:
          - Формирует список кнопок с именами мастеров, что позволяет пользователю выбрать нужного специалиста.
          - Использование inline-клавиатуры обеспечивает интуитивный интерфейс.
        """
        user_data = await state.get_data()

        #________________блок без ввода имени _______________
        # name_user = msg.from_user.username
        # id_user = msg.from_user.id
        # first_name = msg.from_user.first_name
        # logger.info(f"{first_name, name_user, id_user}")
        # await state.update_data(id_user=id_user)
        # await state.update_data(name_user=name_user)


        master_buttons = {
            master["name_master"]: f"booking_master_{master_id}"
            for master_id, master in INFO_LIST_MASTER.items()
        }

        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_SELECT_MASTER}",
            parse_mode="HTML",
            reply_markup=create_inline_universal_keyboard(master_buttons, 2,BACK_BUTTON)
        )

    async def _handle_service_selection(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния выбора услуг.

        Обоснование:
          - Отправляет сообщение с просьбой выбрать услуги, используя inline-клавиатуру.
          - Разделение этой логики позволяет позже расширить функционал выбора услуг (например, добавив динамическое обновление списка).
        """
        user_data = await state.get_data()
        # name_user = msg.from_user.username
        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_SELECT_SERVICES}",
            parse_mode="HTML",
            reply_markup=create_inline_universal_keyboard(BACK_BUTTON, 1)
        )


    async def _handle_date_selection(self, msg: types.Message, state: FSMContext):
            """
            Обработка состояния выбора даты.
            Вместо простого текстового сообщения выводит календарь.
            """

            # Получаем данные календаря для выбранного мастера
            user_data = await state.get_data()
            master_id = user_data.get("master_id")  # Получаем ID мастера
            calendar_id = get_calendar_id_for_master(master_id)
            if not calendar_id:
                logger.error(f"Не удалось получить calendar_id для мастера {master_id}")
                await msg.answer("Ошибка: не удалось определить календарь мастера. Попробуйте позже.")
                await state.clear()  # Пример прерывания
                return
            logger.info(f"Получен calendar_id: {calendar_id} для мастера {master_id}")
            await state.update_data(calendar_id=calendar_id)  # Сохраняем ДО получения данных календаря

            calendar_data = await get_calendar_data(state)
            if calendar_data is None:
                await msg.answer("Ошибка получения данных календаря. Попробуйте позже.")
                return
            year, month, available_dates, fully_booked_dates = calendar_data
            logger.info(f"Получены данные календаря: {calendar_data}")
            # Создаём inline‑клавиатуру календаря
            keyboard = create_calendar_keyboard(year, month, available_dates, fully_booked_dates)
            await msg.answer(
                f"{user_data.get('name', 'Пользователь')}, {STEP_SELECT_DATE}",
                parse_mode="HTML",
                reply_markup=keyboard
            )



    async def _handle_confirm_date(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния подтверждения выбранной даты.

        Обоснование:
          - Изолированный метод для подтверждения даты облегчает модификацию или расширение логики данного шага.
        """
        user_data = await state.get_data()
        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_CONFIRM_DATE} <b>{user_data.get('date')}</b>",
            parse_mode="HTML",
            reply_markup=create_date_confirmation_keyboard(date_str=user_data.get("date")),
        )

    async def _handle_time_selection(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния выбора времени.

        Обоснование:
          - Аналогично выбору даты, выделенный метод позволяет внести изменения в логику выбора времени без влияния на другие этапы.
        """
        user_data = await state.get_data()
        calendar_times = await get_time_calendar_data(state)
        if calendar_times  is None:
            await msg.answer("Ошибка получения данных календаря. Попробуйте позже.")
            return
        keyboard_time_slots = create_time_keyboard(calendar_times)

        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_SELECT_TIME}",
            parse_mode="HTML",
            reply_markup=keyboard_time_slots
        )

    async def _handle_confirm_time(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния подтверждения выбора времени.

        Обоснование:
          - Завершающий шаг процесса бронирования, где выводится сообщение с благодарностью.
          - Изолированный метод упрощает дальнейшую модификацию финального шага.
        """
        logger.info("в _handle_confirm_time Выбранное время: {}".format(msg.text))
        user_data = await state.get_data()
        time = user_data.get("time")
        logger.info(f"Выбранное время: {time}")
        # name_user = msg.from_user.username

        await msg.answer(
            f"{user_data.get('name', 'Пользователь')}, {STEP_CONFIRM_TIME} <b>{user_data.get('time')}</b>",
            parse_mode="HTML",
            reply_markup=create_time_confirmation_keyboard(time_str=user_data.get("time"))
        )

    async def _handle_confirm_booking(self, msg: types.Message, state: FSMContext):
        """
            Показывает финальную сводку перед созданием события.
            Вызывается при переходе в состояние waiting_confirm_booking.
        """
        logger.info("в state_manager _handle_confirm_booking - Показ финальной сводки")
        current_state = await state.get_state()
        logger.info(f"Текущее состояние: {current_state}")

        user_data = await state.get_data()
        # user_name = user_data.get("name_user")

        logger.info(f"Текущие данные: {user_data}")
        # Валидация данных перед показом сводки (можно использовать validate_booking_data)
        valid, data_or_error = await validate_booking_data(state)  # Используем функцию из process_calendar_date_time
        if not valid:
            logger.error(f"Недостаточно данных для показа сводки: {data_or_error}")
            await msg.answer(
                f"❌ Ошибка: {data_or_error} Не удалось собрать данные для подтверждения. Попробуйте начать заново /book.",
                parse_mode="HTML")
            await state.clear()
            return

        # user_data теперь содержит проверенные данные
        user_data = data_or_error

        # Получаем доп.инфо
        master_info = INFO_LIST_MASTER.get(int(user_data['master_id']))
        if not master_info:
            logger.error(f"Мастер с ID {user_data['master_id']} не найден в INFO_LIST_MASTER")
            await msg.answer("❌ Ошибка: информация о мастере не найдена. Попробуйте начать заново /book.",
                             parse_mode="HTML")
            await state.clear()
            return

        total_duration = sum(int(s.get('duration', 60)) for s in user_data['services'])
        total_price = sum(int(s.get('price', 0)) for s in user_data['services'])
        # my_telegram = master_info.get('my_telegram')
        # logger.info(f"Контакт: {my_telegram}")

        service_names = [s.get('full_name_service', 'Неизвестная услуга') for s in user_data['services']]
        start_time = user_data.get('time').replace("time_", "")  # Убираем префикс, если он там есть
        try:
            start_datetime = datetime.strptime(f"{user_data['date']} {start_time}", '%Y-%m-%d %H:%M')
            end_time = (start_datetime + timedelta(minutes=total_duration)).strftime('%H:%M')
        except (ValueError, TypeError) as e:
            logger.error(
                f"Ошибка форматирования времени для сводки: {e}, date={user_data.get('date')}, time={start_time}")
            await msg.answer("❌ Ошибка: неверный формат даты или времени. Попробуйте начать заново /book.",
                             parse_mode="HTML")
            await state.clear()
            return

        # Формируем текст сообщения

        # Адрес

        address_raw = master_info.get('address', 'Адрес не указан')
        address_html = f"<b>{address_raw}</b>"  # По умолчанию просто жирный текст
        if '\n' in address_raw:
            parts = address_raw.split('\n', 1)
            text_part = parts[0].strip()
            url_part = parts[1].strip()
            # Проверяем, что вторая часть похожа на URL
            if url_part.startswith('http'):
                address_html = f"<b>{text_part}</b> <a href='{url_part}'>🗺️ Показать на карте</a>"
            # Если вторая часть не URL, оставляем как было (весь текст жирным)

        # Личный Telegram
        telegram_url = master_info.get('my_telegram')
        telegram_html = f"💬 <a href='{telegram_url}'>Написать в Telegram</a>" if telegram_url else "Контакт Telegram не указан"

        # Email
        email_address = master_info.get('email')
        email_html = f"📩 <a href='mailto:{email_address}'>{email_address}</a>" if email_address else "Email не указан"

        # Канал/Группа Telegram
        channel_url = master_info.get('cl_telegram')
        channel_html = f"📢 <a href='{channel_url}'>Канал/Группа в Telegram</a>" if channel_url else "Канал Telegram не указан"

        # Группа VK
        vk_url = master_info.get('vk_club')
        # Убираем лишние переносы строк и пробелы из URL VK, если они есть
        vk_url_cleaned = vk_url.strip().replace('\n', '').replace(' ', '') if vk_url else None
        vk_html = f"🌍 <a href='{vk_url_cleaned}'>Группа ВКонтакте</a>" if vk_url_cleaned else "Группа VK не указана"


        summary_booking_text = (
            f"<b>📆Запись в календаре</b>\n\n"
            f"<b>Сводная информация о заказе:</b>\n\n"
            f"👤<i>Клиент:</i> <b>{user_data.get('name', 'Пользователь')}</b>\n"
            f"📞<i>Телефон:</i> <b>{user_data.get('phone', 'Телефон отсутствует')}</b>\n\n"
            f"🤩<i>Мастер:</i> <b>{user_data['master_name']}</b>\n"
            f"📍<i>Адрес:</i> <b>{address_html}</b>\n\n"
            f"📶Для связи с мастером используйте \n{telegram_html}\nили{email_html}\n\n"
            f"📅<i>Дата:</i> <b>{format_date_to_russian(user_data['date'])}</b>\n"
            f"⏰<i>Время:</i> <b>{start_time} - {end_time}</b>\n"
            f"⏱️<i>Длительность услуг составит:</i> {format_duration(total_duration)}\n\n"
            f"💼<i>Услуги:</i>\n{'\n'.join(service_names)}\n\n" 
            f"💵<i>Стоимость услуг без скидки составит:</i> <b>{format_price(total_price)}</b>\n\n"
            # Лучше \n для читаемости
        )
        confirm_booking_button = create_confirmation_finish_booking_keyboard()  # Передаем НОВЫЙ callback_data

        # Отправляем сообщение со сводкой и кнопкой "Создать запись"
        await msg.answer(f"<b>{CONFIRM_ORDER_DETAILS_TEXT}</b>\n\n", parse_mode="HTML")
        await msg.answer(
            text=summary_booking_text,
            parse_mode="HTML",
            reply_markup=confirm_booking_button
        )

    async def _handle_creation_event_in_calendar(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния создания события в календаре.

        Обоснование:
          - Завершающий шаг процесса бронирования, где выводится сообщение с благодарностью.
          - Изолированный метод упрощает дальнейшую модификацию финального шага.
        """
        logger.info("в state_manager Создание события в календаре")
        current_state = await state.get_state()
        logger.info(f"Текущее состояние: {current_state}")
        user_data = await state.get_data()
        logger.info(f"Текущие данные: {user_data}")
        await msg.answer(
            FINISH_TEXT,
            parse_mode="HTML",
            reply_markup=create_custom_keyboard(
                CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON)
        )




        await state.set_state(BookingStates.waiting_creation_event_in_calendar)

    async def _handle_finish(self, msg: types.Message, state: FSMContext):
        """
        Обработка состояния завершения процесса бронирования.

        Обоснование:
          - Завершающий шаг процесса бронирования, где выводится сообщение с благодарностью.
          - Изолированный метод упрощает дальнейшую модификацию финального шага.
        """
        logger.info("в state_manager Завершение процесса бронирования")
        await state.get_data()
        await msg.answer(
            f"🙏",
            parse_mode="HTML",
            reply_markup=create_custom_keyboard(
                CUSTOM_BUTTONS, LAYOUT_CUSTOM_212_BUTTON)
            )

        await state.set_state(BookingStates.finish)
        await state.clear()





# Инициализация state_manager для использования в остальной части проекта
state_manager = StateManager()

