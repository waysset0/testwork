FROM python:3.10-slim

WORKDIR /app

# Устанавливаем supervisord
RUN apt-get update && apt-get install -y supervisor

# Копируем файлы зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . /app/

# Копируем конфигурацию для supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Открываем порт для FastAPI
EXPOSE 8000

# Запускаем supervisor
CMD ["/usr/bin/supervisord"]