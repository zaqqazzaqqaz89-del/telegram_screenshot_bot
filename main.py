#!/usr/bin/env python3
"""
Telegram бот для создания скриншотов веб-сайтов
"""
import os
import logging
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from screenshot_service import ScreenshotService
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище настроек пользователей
user_settings = {}

class ScreenshotBot:
    def __init__(self):
        self.screenshot_service = ScreenshotService()
        self.scheduler = AsyncIOScheduler()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        if user_id not in user_settings:
            user_settings[user_id] = {
                'url': None,
                'selector': None,
                'schedule_enabled': False,
                'schedule_time': '09:00'
            }
        
        await update.message.reply_text(
            "👋 Привет! Я бот для создания скриншотов сайтов.\n\n"
            "Доступные команды:\n"
            "/seturl - Установить URL сайта\n"
            "/setselector - Установить CSS-селектор области\n"
            "/screenshot - Сделать скриншот сейчас\n"
            "/schedule - Настроить расписание\n"
            "/settings - Показать текущие настройки\n"
            "/help - Помощь"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📖 Инструкция:\n\n"
            "1️⃣ Установите URL командой /seturl\n"
            "   Пример: /seturl https://example.com\n\n"
            "2️⃣ (Опционально) Установите CSS-селектор для конкретной области:\n"
            "   /setselector .main-content\n"
            "   Если не указан, будет скриншот всей страницы\n\n"
            "3️⃣ Получите скриншот командой /screenshot\n\n"
            "4️⃣ Настройте автоматическую отправку через /schedule\n\n"
            "💡 CSS-селекторы:\n"
            "- По классу: .class-name\n"
            "- По ID: #element-id\n"
            "- По тегу: div, article, main\n"
            "- Комбинированные: div.container, #main article"
        )
    
    async def set_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка URL сайта"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите URL после команды.\n"
                "Пример: /seturl https://example.com"
            )
            return
        
        url = context.args[0]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        user_settings[user_id]['url'] = url
        await update.message.reply_text(f"✅ URL установлен: {url}")
    
    async def set_selector(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка CSS-селектора"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings or not user_settings[user_id]['url']:
            await update.message.reply_text(
                "❌ Сначала установите URL командой /seturl"
            )
            return
        
        if not context.args:
            # Сброс селектора
            user_settings[user_id]['selector'] = None
            await update.message.reply_text(
                "✅ Селектор сброшен. Будет делаться скриншот всей страницы."
            )
            return
        
        selector = ' '.join(context.args)
        user_settings[user_id]['selector'] = selector
        await update.message.reply_text(
            f"✅ Селектор установлен: {selector}\n"
            "Будет делаться скриншот выбранной области."
        )
    
    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание скриншота по запросу"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings or not user_settings[user_id]['url']:
            await update.message.reply_text(
                "❌ Сначала установите URL командой /seturl"
            )
            return
        
        settings = user_settings[user_id]
        await update.message.reply_text("⏳ Создаю скриншот...")
        
        try:
            screenshot_path = await self.screenshot_service.take_screenshot(
                url=settings['url'],
                selector=settings['selector']
            )
            
            caption = f"🖼 Скриншот: {settings['url']}"
            if settings['selector']:
                caption += f"\n📍 Область: {settings['selector']}"
            
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=caption)
            
            # Удаляем временный файл
            os.remove(screenshot_path)
            
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота: {e}")
            await update.message.reply_text(
                f"❌ Ошибка при создании скриншота:\n{str(e)}"
            )
    
    async def schedule_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню настройки расписания"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings or not user_settings[user_id]['url']:
            await update.message.reply_text(
                "❌ Сначала установите URL командой /seturl"
            )
            return
        
        settings = user_settings[user_id]
        status = "✅ Включено" if settings['schedule_enabled'] else "❌ Выключено"
        
        keyboard = [
            [InlineKeyboardButton(
                "🔔 Включить" if not settings['schedule_enabled'] else "🔕 Выключить",
                callback_data='toggle_schedule'
            )],
            [InlineKeyboardButton("⏰ Изменить время", callback_data='change_time')],
        ]
        
        await update.message.reply_text(
            f"📅 Расписание скриншотов\n\n"
            f"Статус: {status}\n"
            f"Время: {settings['schedule_time']} (UTC)\n\n"
            f"URL: {settings['url']}\n"
            f"Область: {settings['selector'] or 'Вся страница'}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        settings = user_settings[user_id]
        
        if query.data == 'toggle_schedule':
            settings['schedule_enabled'] = not settings['schedule_enabled']
            
            if settings['schedule_enabled']:
                self.schedule_screenshot_for_user(user_id, context.application)
                await query.edit_message_text(
                    f"✅ Расписание включено!\n"
                    f"Скриншоты будут отправляться каждый день в {settings['schedule_time']} (UTC)"
                )
            else:
                self.remove_scheduled_job(user_id)
                await query.edit_message_text("❌ Расписание выключено")
        
        elif query.data == 'change_time':
            await query.edit_message_text(
                "⏰ Введите время в формате HH:MM (UTC)\n"
                "Например: 09:00 или 14:30\n\n"
                "Отправьте время следующим сообщением:"
            )
            context.user_data['waiting_for_time'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        if context.user_data.get('waiting_for_time'):
            user_id = update.effective_user.id
            time_str = update.message.text.strip()
            
            try:
                # Проверяем формат времени
                hours, minutes = map(int, time_str.split(':'))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    user_settings[user_id]['schedule_time'] = time_str
                    
                    # Перезапускаем расписание, если оно включено
                    if user_settings[user_id]['schedule_enabled']:
                        self.remove_scheduled_job(user_id)
                        self.schedule_screenshot_for_user(user_id, context.application)
                    
                    await update.message.reply_text(
                        f"✅ Время установлено: {time_str} (UTC)"
                    )
                else:
                    raise ValueError("Неверный диапазон")
            except:
                await update.message.reply_text(
                    "❌ Неверный формат времени. Используйте HH:MM (например: 09:00)"
                )
            
            context.user_data['waiting_for_time'] = False
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать текущие настройки"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings:
            await update.message.reply_text("❌ Настройки не найдены. Используйте /start")
            return
        
        settings = user_settings[user_id]
        schedule_status = "✅ Включено" if settings['schedule_enabled'] else "❌ Выключено"
        
        text = (
            "⚙️ Ваши настройки:\n\n"
            f"🌐 URL: {settings['url'] or 'Не установлен'}\n"
            f"📍 Область: {settings['selector'] or 'Вся страница'}\n"
            f"📅 Расписание: {schedule_status}\n"
            f"⏰ Время: {settings['schedule_time']} (UTC)"
        )
        
        await update.message.reply_text(text)
    
    def schedule_screenshot_for_user(self, user_id: int, application):
        """Добавить задачу в расписание для пользователя"""
        settings = user_settings[user_id]
        hours, minutes = map(int, settings['schedule_time'].split(':'))
        
        self.scheduler.add_job(
            self.send_scheduled_screenshot,
            trigger=CronTrigger(hour=hours, minute=minutes),
            args=[user_id, application],
            id=f'user_{user_id}',
            replace_existing=True
        )
        logger.info(f"Расписание создано для пользователя {user_id} на {settings['schedule_time']}")
    
    def remove_scheduled_job(self, user_id: int):
        """Удалить задачу из расписания"""
        job_id = f'user_{user_id}'
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Расписание удалено для пользователя {user_id}")
    
    async def send_scheduled_screenshot(self, user_id: int, application):
        """Отправить скриншот по расписанию"""
        settings = user_settings.get(user_id)
        if not settings or not settings['url']:
            return
        
        try:
            screenshot_path = await self.screenshot_service.take_screenshot(
                url=settings['url'],
                selector=settings['selector']
            )
            
            caption = f"📅 Плановый скриншот\n🖼 {settings['url']}"
            if settings['selector']:
                caption += f"\n📍 {settings['selector']}"
            
            with open(screenshot_path, 'rb') as photo:
                await application.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=caption
                )
            
            os.remove(screenshot_path)
            logger.info(f"Плановый скриншот отправлен пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке планового скриншота: {e}")
            await application.bot.send_message(
                chat_id=user_id,
                text=f"❌ Ошибка при создании планового скриншота:\n{str(e)}"
            )
    
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


if __name__ == '__main__':
    bot = ScreenshotBot()
    bot.run()
