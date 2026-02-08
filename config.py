"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


class Config:
    """Класс конфигурации"""
    
    # Telegram Bot Token (получить у @BotFather)
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # Проверка наличия токена
    if not TELEGRAM_TOKEN:
        raise ValueError(
            "TELEGRAM_TOKEN не установлен! "
            "Создайте файл .env и добавьте строку: TELEGRAM_TOKEN=ваш_токен"
        )
    
    # Директория для хранения скриншотов
    SCREENSHOTS_DIR = os.getenv('SCREENSHOTS_DIR', 'screenshots')
    
    # Настройки скриншотов по умолчанию
    DEFAULT_VIEWPORT_WIDTH = int(os.getenv('VIEWPORT_WIDTH', '1920'))
    DEFAULT_VIEWPORT_HEIGHT = int(os.getenv('VIEWPORT_HEIGHT', '1080'))
    DEFAULT_TIMEOUT = int(os.getenv('PAGE_TIMEOUT', '30000'))  # миллисекунды
