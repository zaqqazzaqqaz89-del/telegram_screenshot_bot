# 🚀 Исправление для Render.com

## ❌ Текущая проблема

```
RuntimeError: no running event loop
```

**Причина:** APScheduler запускается до создания event loop в Python 3.13.

---

## ✅ БЫСТРОЕ РЕШЕНИЕ (2 минуты)

### Вариант 1: Обновить main.py (рекомендуется)

```bash
# 1. Замените файл
cp main_fixed.py main.py

# 2. Загрузите на GitHub
git add main.py
git commit -m "Fix event loop initialization"
git push origin main
```

Render автоматически передеплоит. Готово! ✅

---

### Вариант 2: Использовать версию без APScheduler

```bash
# 1. Замените файлы
cp main_simple.py main.py
cp requirements_simple.txt requirements.txt

# 2. Загрузите на GitHub
git add main.py requirements.txt
git commit -m "Use asyncio scheduler"
git push origin main
```

---

## 📝 Что исправлено в main_fixed.py

**Проблема:** Планировщик запускался до создания event loop
**Решение:** Планировщик запускается через callback `post_init`

```python
async def post_init(self, application: Application):
    """Запускается ПОСЛЕ создания event loop"""
    self.scheduler.start()  # ✅ Теперь event loop уже создан
    
application.post_init = self.post_init
application.run_polling()  # Создает event loop → вызывает post_init
```

---

## 🔧 Пошаговая инструкция

### Если у вас НЕТ Git локально:

1. Откройте GitHub в браузере: https://github.com/zaqqazzaqqaz89-del/telegram_screenshot_bot
2. Откройте файл `main.py`
3. Нажмите кнопку редактирования (✏️)
4. Откройте в другой вкладке `main_fixed.py` из архива
5. Скопируйте весь код из `main_fixed.py`
6. Вставьте в `main.py`, заменив все содержимое
7. Нажмите "Commit changes"
8. Дождитесь автодеплоя на Render

### Если у вас ЕСТЬ Git:

```bash
# 1. Клонируйте репозиторий (если еще не сделали)
git clone https://github.com/zaqqazzaqqaz89-del/telegram_screenshot_bot.git
cd telegram_screenshot_bot

# 2. Скопируйте исправленные файлы из архива
# (main_fixed.py должен быть в той же папке)

# 3. Замените main.py
cp main_fixed.py main.py

# 4. Проверьте изменения
git diff main.py

# 5. Закоммитьте
git add main.py
git commit -m "Fix: APScheduler event loop initialization"

# 6. Отправьте на GitHub
git push origin main
```

---

## 🎯 Проверка

После деплоя в логах Render вы должны увидеть:

```
✅ Build successful 🎉
✅ Deploying...
✅ Running 'python main.py'
✅ Запуск бота...
✅ Планировщик запущен внутри event loop
✅ Application started
```

Откройте бота в Telegram и отправьте `/start` — должен ответить!

---

## ⚙️ Настройка Render.com

### Переменные окружения:

1. Dashboard → Ваш сервис → Environment
2. Добавьте:
   ```
   TELEGRAM_TOKEN = ваш_токен_от_BotFather
   ```
3. Save Changes

### Build Command (если нужно):

```bash
pip install -r requirements.txt && playwright install chromium
```

### Start Command:

```bash
python main.py
```

---

## 🆘 Если все еще не работает

### Проблема: Playwright не находит браузер

**Build Command:**
```bash
pip install -r requirements.txt && playwright install chromium && playwright install-deps
```

### Проблема: "TELEGRAM_TOKEN не установлен"

Добавьте переменную окружения в Render (см. выше).

### Проблема: Бот не отвечает

1. Проверьте логи в Render
2. Убедитесь, что токен правильный
3. Проверьте, что бот запущен (@BotFather)

---

## 📋 Сравнение версий

| Файл | Планировщик | Совместимость | Когда использовать |
|------|-------------|---------------|-------------------|
| main_fixed.py | APScheduler | Python 3.13+ | Основная версия (рекомендуется) |
| main_simple.py | asyncio | Python 3.11+ | Если проблемы с APScheduler |

---

## 💾 Резервная копия

Перед изменением сохраните старый main.py:
```bash
cp main.py main.py.backup
```

Откатить изменения:
```bash
cp main.py.backup main.py
git add main.py
git commit -m "Rollback"
git push origin main
```

---

**После исправления бот заработает! 🎉**

Вопросы? Проверьте логи в Render Dashboard → Logs
