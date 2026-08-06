echo "--> Запуск миграций базы данных..."
poetry run python manage.py migrate --noinput

echo "--> Сбор статических файлов..."
poetry run python manage.py collectstatic --noinput

echo "--> Запуск веб-сервера Gunicorn..."
exec poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000
