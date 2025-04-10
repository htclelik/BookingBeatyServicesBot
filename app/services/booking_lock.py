# app/services/booking_lock.py
from typing import Dict, Set
from datetime import datetime, timedelta
import asyncio


class BookingLockManager:
    """Менеджер для временной блокировки слотов времени при бронировании"""

    def __init__(self, lock_duration: int = 300):  # 5 минут по умолчанию
        self.locked_slots: Dict[str, Dict[str, datetime]] = {}  # master_id -> {slot_key -> expiry}
        self.lock_duration = lock_duration

    async def start_cleanup_task(self):
        """Запускает задачу очистки устаревших блокировок"""
        asyncio.create_task(self._cleanup_expired_locks())

    async def _cleanup_expired_locks(self):
        """Периодически удаляет истекшие блокировки"""
        while True:
            now = datetime.now()
            for master_id in list(self.locked_slots.keys()):
                for slot_key in list(self.locked_slots[master_id].keys()):
                    if self.locked_slots[master_id][slot_key] < now:
                        del self.locked_slots[master_id][slot_key]
                if not self.locked_slots[master_id]:
                    del self.locked_slots[master_id]
            await asyncio.sleep(60)  # Проверка раз в минуту

    def lock_slot(self, master_id: str, date_str: str, time_str: str) -> bool:
        """Блокирует слот для бронирования"""
        slot_key = f"{date_str}_{time_str}"

        if master_id not in self.locked_slots:
            self.locked_slots[master_id] = {}

        # Проверяем, не заблокирован ли слот
        if slot_key in self.locked_slots[master_id]:
            return False

        # Устанавливаем блокировку
        expiry = datetime.now() + timedelta(seconds=self.lock_duration)
        self.locked_slots[master_id][slot_key] = expiry
        return True

    def release_slot(self, master_id: str, date_str: str, time_str: str) -> None:
        """Освобождает заблокированный слот"""
        slot_key = f"{date_str}_{time_str}"

        if master_id in self.locked_slots and slot_key in self.locked_slots[master_id]:
            del self.locked_slots[master_id][slot_key]

    def is_slot_locked(self, master_id: str, date_str: str, time_str: str) -> bool:
        """Проверяет, заблокирован ли слот"""
        slot_key = f"{date_str}_{time_str}"

        if master_id not in self.locked_slots:
            return False

        if slot_key not in self.locked_slots[master_id]:
            return False

        # Проверяем, не истекла ли блокировка
        if self.locked_slots[master_id][slot_key] < datetime.now():
            del self.locked_slots[master_id][slot_key]
            return False

        return True