# app/utils/service_utils.py
from aiogram.fsm.context import FSMContext
from app.database.local_mini_db import MASTER_SERVICES_FULL

async def toggle_service_selection(state: FSMContext, master_id: int, service_id: str):
    """Добавляет или убирает услугу из списка выбранных"""
    user_data = await state.get_data()
    selected_services = user_data.get("selected_services", {})

    if service_id in selected_services:
        del selected_services[service_id]  # Убираем услугу
    else:
        service_details = MASTER_SERVICES_FULL[master_id].get(service_id, {})
        if service_details:
            selected_services[service_id] = service_details

    await state.update_data(selected_services=selected_services)
    return selected_services
