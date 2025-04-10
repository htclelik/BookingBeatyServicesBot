import os
from aiogram import Bot
from app.config import BOT_TOKEN

# Используем BOT_TOKEN из твоего config.py
if not BOT_TOKEN:
    raise ValueError("Не найден BOT_TOKEN в config.py")

bot = Bot(token=BOT_TOKEN)