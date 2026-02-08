# Telegram Screenshot Bot 📸

Telegram бот для автоматического создания скриншотов веб-сайтов по запросу и расписанию.

## 🌟 Возможности

- 📸 Создание скриншотов полной страницы или выбранной области
- ⏰ Автоматическая отправка скриншотов по расписанию
- 🎯 Поддержка CSS-селекторов для выбора конкретных элементов
- 🔄 Простая настройка через команды Telegram
- 📅 Гибкое планирование времени отправки

## ⚠️ Важно: Совместимость с Python

**Если вы используете Python 3.13+**, используйте упрощенную версию без APScheduler:
```bash
# Используйте эти файлы:
cp main_simple.py main.py
cp requirements_simple.txt requirements.txt
```

**Для Python 3.11 или 3.12** используйте стандартную версию (уже настроена по умолчанию).

## 🚀 Установка

### 1. Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### 2. Клонирование или загрузка проекта

```bash
# Если используете git
git clone <your-repo-url>
cd telegram_screenshot_bot

# Или просто скопируйте все файлы в папку
```

### 3. Установка зависимостей

```bash
# Установка Python пакетов
pip install -r requirements.txt

# Установка браузера Playwright
playwright install chromium
```

### 4. Создание Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен (например: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 5. Настройка конфигурации

```bash
# Скопируйте пример файла конфигурации
cp .env.example .env

# Отредактируйте файл .env и вставьте ваш токен
nano .env  # или любой другой редактор
```

В файле `.env` замените `your_bot_token_here` на ваш реальный токен:

```env
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## 📖 Использование

### Запуск бота

```bash
python main.py
```

### Команды бота

После запуска бота найдите его в Telegram и используйте следующие команды:

#### Основные команды

- `/start` - Начать работу с ботом
- `/help` - Показать справку
- `/settings` - Показать текущие настройки

#### Настройка

1. **Установить URL сайта:**
   ```
   /seturl https://example.com
   ```

2. **Установить CSS-селектор (опционально):**
   ```
   /setselector .main-content
   ```
   
   Примеры селекторов:
   - `.class-name` - элемент с классом
   - `#element-id` - элемент с ID
   - `article.post` - комбинированный селектор
   - `div > p` - вложенные элементы

3. **Сбросить селектор (скриншот всей страницы):**
   ```
   /setselector
   ```

#### Получение скриншотов

- `/screenshot` - Получить скриншот немедленно
- `/schedule` - Настроить автоматическую отправку по расписанию

### Настройка расписания

1. Используйте команду `/schedule`
2. Нажмите "Включить" для активации автоматической отправки
3. Нажмите "Изменить время" и введите время в формате `HH:MM` (UTC)
4. Бот будет автоматически отправлять скриншоты каждый день в указанное время

**Важно:** Время указывается в UTC. Для Москвы (UTC+3) вычтите 3 часа:
- Чтобы получать в 12:00 по Москве, укажите `09:00`
- Чтобы получать в 18:00 по Москве, укажите `15:00`

## 💡 Примеры использования

### Пример 1: Скриншот всего сайта

```
/seturl https://news.ycombinator.com
/screenshot
```

### Пример 2: Скриншот конкретной области

```
/seturl https://github.com
/setselector .dashboard-sidebar
/screenshot
```

### Пример 3: Ежедневный скриншот биржи

```
/seturl https://finance.yahoo.com
/setselector #market-summary
/schedule
→ Включить → Изменить время → 09:00
```

## 🔍 Как найти CSS-селектор

### Способ 1: Через DevTools браузера

1. Откройте сайт в браузере
2. Нажмите F12 (открыть DevTools)
3. Нажмите на иконку "выбрать элемент" (стрелка в углу)
4. Кликните на нужный элемент на странице
5. В DevTools посмотрите на выбранный элемент:
   - Если есть `class="..."` - используйте `.class-name`
   - Если есть `id="..."` - используйте `#element-id`

### Способ 2: Копирование селектора

1. Откройте DevTools (F12)
2. Выберите нужный элемент
3. ПКМ на элементе в DevTools → Copy → Copy selector
4. Вставьте скопированный селектор в команду `/setselector`

## 🛠 Расширенная настройка

### Изменение размера viewport

Отредактируйте файл `.env`:

```env
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
```

### Изменение таймаута загрузки страницы

```env
PAGE_TIMEOUT=30000  # в миллисекундах (30 секунд)
```

## 📁 Структура проекта

```
telegram_screenshot_bot/
├── main.py                    # Основной файл бота (с APScheduler)
├── main_simple.py             # Альтернативная версия (без APScheduler, для Python 3.13+)
├── screenshot_service.py      # Сервис для создания скриншотов
├── config.py                  # Конфигурация
├── requirements.txt           # Зависимости для Python 3.11-3.12
├── requirements_simple.txt    # Зависимости для Python 3.13+
├── runtime.txt               # Версия Python для деплоя (3.12.8)
├── .env.example              # Пример файла конфигурации
├── .env                      # Ваша конфигурация (создается вручную)
├── .gitignore               # Git ignore файл
├── screenshots/             # Папка для временных скриншотов (создается автоматически)
├── README.md               # Этот файл
├── EXAMPLES.md            # Примеры использования
└── TROUBLESHOOTING.md    # Решение проблем
```

## ⚠️ Возможные проблемы

### "Failed building wheel for greenlet" (Python 3.13)

**Проблема:** Пакет `greenlet` (зависимость APScheduler) несовместим с Python 3.13+

**Решение 1 - Использовать упрощенную версию (рекомендуется для Python 3.13+):**
```bash
# Скопируйте упрощенную версию
cp main_simple.py main.py
cp requirements_simple.txt requirements.txt

# Установите зависимости
pip install -r requirements.txt
playwright install chromium

# Запустите бота
python main.py
```

**Решение 2 - Использовать Python 3.12:**
```bash
# Установите Python 3.12 через pyenv или используйте виртуальное окружение
pyenv install 3.12.8
pyenv local 3.12.8

# Или укажите при деплое (файл runtime.txt уже создан)
```

**Решение 3 - Для деплоя на Render/Heroku:**
Файл `runtime.txt` уже настроен на Python 3.12.8

### "TELEGRAM_TOKEN не установлен"

**Решение:** Создайте файл `.env` на основе `.env.example` и добавьте ваш токен.

### "Элемент не найден на странице"

**Решение:** 
- Проверьте правильность CSS-селектора
- Убедитесь, что элемент видим на странице
- Попробуйте увеличить таймаут в `.env`

### Playwright не устанавливается

**Решение:**
```bash
# Установите системные зависимости (Linux)
playwright install-deps

# Затем снова установите браузер
playwright install chromium
```

### Бот не отправляет плановые скриншоты

**Решение:**
- Убедитесь, что бот запущен и не остановлен
- Проверьте правильность времени (используется UTC)
- Проверьте логи на наличие ошибок

## 🔒 Безопасность

- Никогда не публикуйте файл `.env` с вашим токеном
- Добавьте `.env` в `.gitignore` если используете git
- Храните токен бота в секрете

## 📝 Логи

Бот выводит логи в консоль. Для сохранения логов в файл используйте:

```bash
python main.py >> bot.log 2>&1
```

## 🚀 Запуск в фоновом режиме (Linux)

### С использованием screen

```bash
screen -S screenshot_bot
python main.py
# Нажмите Ctrl+A, затем D для выхода

# Вернуться к боту:
screen -r screenshot_bot
```

### С использованием systemd

Создайте файл `/etc/systemd/system/screenshot-bot.service`:

```ini
[Unit]
Description=Telegram Screenshot Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram_screenshot_bot
ExecStart=/usr/bin/python3 /path/to/telegram_screenshot_bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable screenshot-bot
sudo systemctl start screenshot-bot
sudo systemctl status screenshot-bot
```

## 📄 Лицензия

Этот проект создан для образовательных целей. Используйте на свой риск.

## 🤝 Поддержка

Если у вас возникли вопросы или проблемы:

1. Проверьте раздел "Возможные проблемы"
2. Убедитесь, что все зависимости установлены правильно
3. Проверьте логи бота на наличие ошибок

---

**Приятного использования! 🎉**
