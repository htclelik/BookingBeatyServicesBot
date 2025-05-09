# config.py

import base64
import json
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Список ключей
# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOOKING_CHAT_ID = os.getenv("BOOKING_CHAT_ID")

# OpenAI
OPENAI_API_KEY = os.getenv("OPEN_AI_KEY_ORIGINAL")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
URL_OPENAI_TEXT = "https://api.openai.com/v1/completions"
DB_OPENAI_ID = os.getenv("DB_OPENAI_ID")

# Yandex
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
URL_YGPT_TEXT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
MAX_SESSION_AGE_HOURS = 24
MAX_HISTORY_LENGTH = 4095

# Окружение
ENVIRONMENT=os.getenv("ENVIRONMENT")

# Google credentials
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
GOOGLE_CREDENTIALS_B64 = os.getenv("GOOGLE_CREDENTIALS_B64")

# Если есть GOOGLE_CREDENTIALS_B64, создаем временный файл с учетными данными
if GOOGLE_CREDENTIALS_B64:
    try:
        credentials_json = base64.b64decode(GOOGLE_CREDENTIALS_B64).decode('utf-8')
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write(credentials_json)
        temp_file.close()
        # Переопределяем путь к файлу учетных данных
        GOOGLE_CREDENTIALS_PATH = temp_file.name
    except Exception as e:
        print(f"Ошибка при декодировании GOOGLE_CREDENTIALS_B64: {e}")

# Доступ к таблице
SCOPES_SHEETS = ['https://www.googleapis.com/auth/spreadsheets']
SCOPES_FEED_DRIVE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SCOPES_CALENDAR = ['https://www.googleapis.com/auth/calendar']
# GOOGLE_SERVICE_ACCOUNT_JSON=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CACHE_TTL = os.getenv("GOOGLE_CACHE_TTL")
REMINDERS_WORKSHEET_NAME = os.getenv("REMINDERS_WORKSHEET_NAME")
BOOKINGS_LOG_WORKSHEET_NAME = os.getenv('BOOKINGS_LOG_WORKSHEET_NAME')
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_CALENDAR_ID_0 = os.getenv("GOOGLE_CALENDAR_ID_0")
GOOGLE_CALENDAR_ID_1 = os.getenv("GOOGLE_CALENDAR_ID_1")
GOOGLE_CALENDAR_ID_2 = os.getenv("GOOGLE_CALENDAR_ID_2")

# Timezone
TIMEZONE = 'Europe/Moscow' # Укажи свой часовой пояс

# Список участников
ADMIN_ID = list(map(int, os.getenv("ADMIN_ID", "").split(",")))
MASTERS_ID = list(map(int, os.getenv("MASTERS_ID", "").split(",")))
GOOGLE_CALENDAR_ID = [GOOGLE_CALENDAR_ID_0, GOOGLE_CALENDAR_ID_1, GOOGLE_CALENDAR_ID_2]

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "bot.log"

# Безопасность # количество разрешенных запросов в секунду
THROTTLE_RATE=os.getenv("THROTTLE_RATE")

# Проверка наличия файла учетных данных Google
if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
    raise FileNotFoundError(f"Файл {GOOGLE_CREDENTIALS_PATH} не найден! Проверьте путь или наличие GOOGLE_CREDENTIALS_B64.")

# Проверка обязательных переменных окружения
if not BOT_TOKEN or not OPENAI_API_KEY or not OPENAI_ASSISTANT_ID:
    raise EnvironmentError("Не все обязательные переменные окружения установлены!")