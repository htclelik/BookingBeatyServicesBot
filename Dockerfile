# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY ./requirements.txt /app/requirements.txt

# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем всю структуру проекта в рабочую директорию
COPY . .

# Команда запуска вашего приложения (измените путь к main.py на актуальный)
CMD ["python", "app/main.py"]
