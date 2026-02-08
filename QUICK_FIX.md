# 🚨 СРОЧНОЕ ИСПРАВЛЕНИЕ - RuntimeError на Render

Если ваш бот на Render показывает ошибку `RuntimeError: no running event loop`, вот быстрое решение:

## 📥 Шаг 1: Обновите main.py в GitHub

Скачайте исправленный `main.py` из этого репозитория и замените ваш файл.

**Или исправьте вручную:**

Найдите метод `run()` в вашем `main.py` (строка ~328) и замените его на:

```python
def run(self):
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", self.start))
    application.add_handler(CommandHandler("help", self.help_command))
    application.add_handler(CommandHandler("seturl", self.set_url))
    application.add_handler(CommandHandler("setselector", self.set_selector))
    application.add_handler(CommandHandler("screenshot", self.take_screenshot))
    application.add_handler(CommandHandler("schedule", self.schedule_menu))
    application.add_handler(CommandHandler("settings", self.show_settings))
    
    # Обработчики кнопок и сообщений
    application.add_handler(CallbackQueryHandler(self.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    # Инициализируем планировщик после запуска приложения
    async def post_init(application):
        """Запуск планировщика после инициализации бота"""
        self.scheduler.start()
        logger.info("Планировщик запущен")
    
    application.post_init = post_init
    
    # Запускаем бота
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
```

**Ключевое изменение:** `self.scheduler.start()` теперь вызывается внутри `post_init`, после создания event loop.

## 📤 Шаг 2: Загрузите в GitHub

```bash
git add main.py
git commit -m "Fix RuntimeError: no running event loop"
git push origin main
```

## 🔄 Шаг 3: Перезапустите на Render

Render автоматически задеплоит новую версию если включен Auto-Deploy.

**Или вручную:**
1. Зайдите на [dashboard.render.com](https://dashboard.render.com)
2. Откройте ваш сервис
3. Нажмите **"Manual Deploy"** → **"Deploy latest commit"**

## ✅ Шаг 4: Проверьте логи

Через 2-3 минуты проверьте логи. Вы должны увидеть:

```
INFO - Бот запущен
INFO - Планировщик запущен
```

Если видите эти строки - бот работает! 🎉

---

## 🔀 Альтернативное решение (быстрое)

Если не хотите редактировать код, используйте упрощенную версию:

### На Render:

1. Откройте **Settings** вашего сервиса
2. Найдите **Start Command**
3. Измените на: `python main_simple.py`
4. Нажмите **"Save Changes"**
5. Сервис автоматически перезапустится

### В GitHub:

Добавьте файл `main_simple.py` в ваш репозиторий (скачайте из этого архива).

---

## 🧪 Тест после исправления

Отправьте боту в Telegram:
```
/start
```

Если бот отвечает - всё работает! 🚀

---

## 💡 Что было исправлено?

**Проблема:** APScheduler требует running event loop, но `scheduler.start()` вызывался до `application.run_polling()`, который создаёт loop.

**Решение:** Переместили `scheduler.start()` в `post_init` callback, который выполняется после создания event loop.

---

**Время исправления: ~5 минут** ⏱️
