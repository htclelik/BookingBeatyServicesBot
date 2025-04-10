
import asyncio
import logging
import sys # Добавь sys для логирования в stdout

# Используем общий экземпляр бота
from bot_instance import bot # <<<--- Импорт общего экземпляра
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

# Убираем импорт BOT_TOKEN отсюда, берем из bot_instance
# import config # Импорт конфига все еще нужен для других настроек? Если нет, можно убрать.
from app.handlers.dispatcher import setup_dispatcher
# <<<--- Импорты для планировщика ---
from app.scheduler_setup import scheduler, schedule_reminders_from_sheet
# ----------------------------------
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def set_default_commands(bot_instance: Bot): # Принимаем bot как аргумент
    commands = [
        BotCommand(command="start", description="🏁Начало работы"),
        # BotCommand(command="assistant", description="💬Общение с ассистентом"),
        # BotCommand(command="info", description="ℹ️Информация о нас:👩‍🦰🧔🏻‍♂️Мастера, 🛠️💅💇‍♂️👨‍💻Услуги"),
        # BotCommand(command="book", description="📆Записаться на удобное время"),
        # BotCommand(command="gift", description="🎁Акции, Подарки"),
        BotCommand(command="help", description="🛟Помощь по работе ассистента или обратиться в тех.поддержку"),
        # Убери cancel, если он не используется повсеместно или замени на команду отмены FSM
        BotCommand(command="cancel", description="🚫Отменить операцию")
    ]
    await bot_instance.set_my_commands(commands)


async def main():
    # Конфигурируем логирование
    logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Добавим формат
    logger.info("Запуск бота...")

    # Инициализация хранилища FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Настройка обработчиков (передаем bot для единообразия, если другие хендлеры его ожидают)
    setup_dispatcher(dp) # <<<--- Убрал bot из аргументов, т.к. импортируем из bot_instance
    await set_default_commands(bot) # Используем импортированный bot

    # --- Запуск планировщика ---
    try:
        logger.info("Запуск планировщика APScheduler...")
        scheduler.start()
        logger.info("APScheduler запущен.")
        # Планируем задачи из таблицы после небольшого ожидания
        await asyncio.sleep(1)
        await schedule_reminders_from_sheet()
    except Exception as e:
        logger.error(f"Ошибка запуска или планирования задач APScheduler: {e}", exc_info=True)
    # ---------------------------

    logger.info("Запуск polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Остановка бота...")
        if scheduler.running:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    # Используем try-except для корректного завершения
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Выход из бота (KeyboardInterrupt/SystemExit)")
    except Exception as e:
         logger.critical(f"Критическая ошибка в asyncio.run(main): {e}", exc_info=True)