# Используем официальный образ Playwright с предустановленным браузером
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Порт для webhook (Render установит через переменную PORT)
EXPOSE 10000

# Запуск бота
CMD ["python", "main.py"]
