FROM python:3.13-slim

# Отключение буферизации для немедленного вывода логов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка зависимостей отдельным слоем (кэширование)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода и артефактов
COPY src/__init__.py src/api.py src/schemas.py ./src/
COPY artifacts/ ./artifacts/
COPY models/ ./models/

EXPOSE 8000

# Запуск ASGI-сервера uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]