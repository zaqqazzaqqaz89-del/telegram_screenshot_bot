#!/usr/bin/env python3
"""
Telegram бот для создания скриншотов веб-сайтов
Версия: WEBHOOK с улучшенным выбором области
"""
import os
import logging
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
                'selector_type': 'full',  # full, css, text, coords, auto
                'search_text': None,
                'coordinates': None,
                'schedule_enabled': False,
                'schedule_time': '09:00'
            }
        
        await update.message.reply_text(
            "👋 Привет! Я бот для создания скриншотов сайтов.\n\n"
            "Доступные команды:\n"
            "/seturl - Установить URL сайта\n"
            "/area - Выбрать область для скриншота ⭐️\n"
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
            "2️⃣ Выберите область командой /area\n"
            "   📍 Вся страница (по умолчанию)\n"
            "   📍 Главный контент (автоматически)\n"
            "   📍 По тексту (найти элемент)\n"
            "   📍 По координатам\n"
            "   📍 По CSS-селектору (для опытных)\n\n"
            "3️⃣ Получите скриншот командой /screenshot\n\n"
            "4️⃣ Настройте расписание через /schedule\n\n"
            "💡 Новые возможности:\n"
            "- Автопоиск главного контента\n"
            "- Поиск элемента по тексту\n"
            "- Выбор области координатами"
        )
    
    async def set_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка URL сайта"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings:
            user_settings[user_id] = {
                'url': None,
                'selector': None,
                'selector_type': 'full',
                'search_text': None,
                'coordinates': None,
                'schedule_enabled': False,
                'schedule_time': '09:00'
            }
        
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
        
        # Показываем кнопки выбора области
        keyboard = [
            [InlineKeyboardButton("📄 Вся страница", callback_data='area_full')],
            [InlineKeyboardButton("🎯 Главный контент (авто)", callback_data='area_auto')],
            [InlineKeyboardButton("🔍 Найти по тексту", callback_data='area_text')],
            [InlineKeyboardButton("📐 По координатам", callback_data='area_coords')],
            [InlineKeyboardButton("🔧 CSS-селектор", callback_data='area_css')],
        ]
        
        await update.message.reply_text(
            f"✅ URL установлен: {url}\n\n"
            "Выберите область для скриншота:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def area_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Меню выбора области"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings or not user_settings[user_id]['url']:
            await update.message.reply_text(
                "❌ Сначала установите URL командой /seturl"
            )
            return
        
        settings = user_settings[user_id]
        
        # Показываем текущую настройку
        current = self._get_area_description(settings)
        
        keyboard = [
            [InlineKeyboardButton("📄 Вся страница", callback_data='area_full')],
            [InlineKeyboardButton("🎯 Главный контент (авто)", callback_data='area_auto')],
            [InlineKeyboardButton("🔍 Найти по тексту", callback_data='area_text')],
            [InlineKeyboardButton("📐 По координатам", callback_data='area_coords')],
            [InlineKeyboardButton("🔧 CSS-селектор", callback_data='area_css')],
        ]
        
        await update.message.reply_text(
            f"📍 Текущая область: {current}\n\n"
            "Выберите новую область:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def _get_area_description(self, settings):
        """Получить описание текущей области"""
        if settings['selector_type'] == 'full':
            return "Вся страница"
        elif settings['selector_type'] == 'auto':
            return "Главный контент (автоматически)"
        elif settings['selector_type'] == 'text':
            return f"По тексту: '{settings['search_text']}'"
        elif settings['selector_type'] == 'coords':
            coords = settings['coordinates']
            return f"Координаты: ({coords['x']}, {coords['y']}, {coords['width']}x{coords['height']})"
        elif settings['selector_type'] == 'css':
            return f"CSS: {settings['selector']}"
        return "Не установлена"
    
    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Создание скриншота"""
        user_id = update.effective_user.id
        
        if user_id not in user_settings or not user_settings[user_id]['url']:
            await update.message.reply_text(
                "❌ Сначала установите URL командой /seturl"
            )
            return
        
        settings = user_settings[user_id]
        await update.message.reply_text("⏳ Создаю скриншот...")
        
        try:
            # Определяем параметры для скриншота
            screenshot_params = {
                'url': settings['url'],
                'selector_type': settings['selector_type'],
                'selector': settings.get('selector'),
                'search_text': settings.get('search_text'),
                'coordinates': settings.get('coordinates')
            }
            
            screenshot_path = await self.screenshot_service.take_screenshot(**screenshot_params)
            
            caption = f"🖼 Скриншот: {settings['url']}\n"
            caption += f"📍 Область: {self._get_area_description(settings)}"
            
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=caption)
            
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
            f"Область: {self._get_area_description(settings)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        settings = user_settings[user_id]
        
        # Обработка выбора области
        if query.data.startswith('area_'):
            area_type = query.data.replace('area_', '')
            
            if area_type == 'full':
                settings['selector_type'] = 'full'
                settings['selector'] = None
                settings['search_text'] = None
                settings['coordinates'] = None
                await query.edit_message_text(
                    "✅ Выбрано: Вся страница\n\n"
                    "Теперь используйте /screenshot для создания скриншота."
                )
            
            elif area_type == 'auto':
                settings['selector_type'] = 'auto'
                settings['selector'] = None
                settings['search_text'] = None
                settings['coordinates'] = None
                await query.edit_message_text(
                    "✅ Выбрано: Главный контент (автоопределение)\n\n"
                    "Бот попытается найти основной контент страницы автоматически.\n"
                    "Используйте /screenshot для создания скриншота."
                )
            
            elif area_type == 'text':
                await query.edit_message_text(
                    "🔍 Поиск элемента по тексту\n\n"
                    "Введите текст, который содержится в нужном элементе.\n"
                    "Например: 'Главные новости' или 'Цена'\n\n"
                    "Отправьте текст следующим сообщением:"
                )
                context.user_data['waiting_for_search_text'] = True
            
            elif area_type == 'coords':
                await query.edit_message_text(
                    "📐 Координаты области\n\n"
                    "Введите координаты в формате:\n"
                    "x y width height\n\n"
                    "Например: 100 200 800 600\n"
                    "(x=100, y=200, ширина=800, высота=600)\n\n"
                    "Отправьте координаты следующим сообщением:"
                )
                context.user_data['waiting_for_coords'] = True
            
            elif area_type == 'css':
                await query.edit_message_text(
                    "🔧 CSS-селектор\n\n"
                    "Введите CSS-селектор элемента.\n"
                    "Примеры:\n"
                    "  .main-content\n"
                    "  #article-body\n"
                    "  div.container\n\n"
                    "Отправьте селектор следующим сообщением:"
                )
                context.user_data['waiting_for_css'] = True
        
        # Обработка расписания
        elif query.data == 'toggle_schedule':
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
        user_id = update.effective_user.id
        text = update.message.text.strip()
        
        # Обработка ввода текста для поиска
        if context.user_data.get('waiting_for_search_text'):
            user_settings[user_id]['selector_type'] = 'text'
            user_settings[user_id]['search_text'] = text
            user_settings[user_id]['selector'] = None
            user_settings[user_id]['coordinates'] = None
            
            await update.message.reply_text(
                f"✅ Будет искаться элемент с текстом: '{text}'\n\n"
                "Используйте /screenshot для создания скриншота."
            )
            context.user_data['waiting_for_search_text'] = False
        
        # Обработка ввода координат
        elif context.user_data.get('waiting_for_coords'):
            try:
                parts = text.split()
                if len(parts) != 4:
                    raise ValueError("Нужно 4 числа")
                
                x, y, width, height = map(int, parts)
                
                user_settings[user_id]['selector_type'] = 'coords'
                user_settings[user_id]['coordinates'] = {
                    'x': x, 'y': y, 'width': width, 'height': height
                }
                user_settings[user_id]['selector'] = None
                user_settings[user_id]['search_text'] = None
                
                await update.message.reply_text(
                    f"✅ Координаты установлены:\n"
                    f"x={x}, y={y}, ширина={width}, высота={height}\n\n"
                    "Используйте /screenshot для создания скриншота."
                )
            except:
                await update.message.reply_text(
                    "❌ Неверный формат!\n"
                    "Используйте: x y width height\n"
                    "Например: 100 200 800 600"
                )
            
            context.user_data['waiting_for_coords'] = False
        
        # Обработка ввода CSS-селектора
        elif context.user_data.get('waiting_for_css'):
            user_settings[user_id]['selector_type'] = 'css'
            user_settings[user_id]['selector'] = text
            user_settings[user_id]['search_text'] = None
            user_settings[user_id]['coordinates'] = None
            
            await update.message.reply_text(
                f"✅ CSS-селектор установлен: {text}\n\n"
                "Используйте /screenshot для создания скриншота."
            )
            context.user_data['waiting_for_css'] = False
        
        # Обработка ввода времени для расписания
        elif context.user_data.get('waiting_for_time'):
            try:
                hours, minutes = map(int, text.split(':'))
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    user_settings[user_id]['schedule_time'] = text
                    
                    if user_settings[user_id]['schedule_enabled']:
                        self.remove_scheduled_job(user_id)
                        self.schedule_screenshot_for_user(user_id, context.application)
                    
                    await update.message.reply_text(
                        f"✅ Время установлено: {text} (UTC)"
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
            f"📍 Область: {self._get_area_description(settings)}\n"
            f"📅 Расписание: {schedule_status}\n"
            f"⏰ Время: {settings['schedule_time']} (UTC)"
        )
        
        await update.message.reply_text(text)
    
    def schedule_screenshot_for_user(self, user_id: int, application):
        """Добавить задачу в расписание"""
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
            screenshot_params = {
                'url': settings['url'],
                'selector_type': settings['selector_type'],
                'selector': settings.get('selector'),
                'search_text': settings.get('search_text'),
                'coordinates': settings.get('coordinates')
            }
            
            screenshot_path = await self.screenshot_service.take_screenshot(**screenshot_params)
            
            caption = f"📅 Плановый скриншот\n🖼 {settings['url']}\n"
            caption += f"📍 {self._get_area_description(settings)}"
            
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
        """Запуск бота в режиме WEBHOOK для Render Web Service"""
        application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("seturl", self.set_url))
        application.add_handler(CommandHandler("area", self.area_menu))
        application.add_handler(CommandHandler("screenshot", self.take_screenshot))
        application.add_handler(CommandHandler("schedule", self.schedule_menu))
        application.add_handler(CommandHandler("settings", self.show_settings))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запуск планировщика
        async def post_init(app):
            self.scheduler.start()
            logger.info("Планировщик запущен")
        
        application.post_init = post_init
        
        # Настройка WEBHOOK для Render
        render_url = os.getenv("RENDER_EXTERNAL_URL")
        if not render_url:
            raise RuntimeError(
                "RENDER_EXTERNAL_URL не установлена!\n"
                "Render должен установить её автоматически.\n"
                "Проверьте что вы используете Web Service (не Background Worker)."
            )
        
        port = int(os.getenv("PORT", "10000"))
        webhook_path = "/webhook"
        webhook_url = f"{render_url}{webhook_path}"
        
        logger.info("=" * 60)
        logger.info("🚀 Бот запущен в режиме WEBHOOK")
        logger.info(f"📡 Webhook URL: {webhook_url}")
        logger.info(f"🔌 Порт: {port}")
        logger.info("=" * 60)
        
        # ВАЖНО: вызываем run_webhook напрямую, БЕЗ asyncio.run(...)
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )


if __name__ == '__main__':
    bot = ScreenshotBot()
    bot.run()
