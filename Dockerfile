# 1. Берем официальный тонкий образ с Python 3.13
FROM python:3.13-slim

# 2. Задаем системные переменные, чтобы Python не буферизировал логи
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# 3. Создаем и переходим в рабочую папку внутри контейнера
WORKDIR /code

# 4. Устанавливаем Poetry внутрь контейнера Linux
RUN pip install --no-cache-dir poetry

# 5. Копируем файлы зависимостей Poetry с Макбука
COPY pyproject.toml poetry.lock ./

# 6. Устанавливаем все библиотеки проекта без venv (напрямую в систему контейнера)
RUN poetry install --no-root --no-interaction --no-ansi

# 7. Копируем весь остальной код Django-проекта
COPY . .

# 8. Команда для запуска сервера разработки
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
