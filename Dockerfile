# Dockerfile для FastAPI приложения

# Базовый образ с Python
FROM python:3.10-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов приложения в контейнер
COPY . /app

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Установка переменной окружения для python-dotenv
ENV PYTHONPATH=/app

# Запуск сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
