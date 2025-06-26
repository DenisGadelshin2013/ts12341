import os
import random
import asyncio

from telegram import (
    Bot,
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Не забудь задать переменную окружения


# /start — приветствие и кнопка отправки номера
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📞 Отправить номер", request_contact=True)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Отправь свой номер телефона:", reply_markup=reply_markup)


# обработка контакта (кнопка)
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        await update.message.reply_text(f"Спасибо! Мы сохранили твой номер: {contact.phone_number}")
        # Здесь можно связать Telegram user ID с номером в БД


# отправка кода подтверждения
async def send_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = random.randint(1000, 9999)
    await update.message.reply_text(f"Код подтверждения: {code}")
    # Можно сохранить этот код в БД или временное хранилище


# уведомление пользователю (например, при просрочке возврата)
async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔔 Напоминание: вы не вернули повербанк вовремя.")


# функция, вызываемая Flask при приходе нового update
def handle_update(update_json):
    async def process():
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("sendcode", send_code))
        application.add_handler(CommandHandler("notify", notify))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

        await application.initialize()  # обязательно!
        update_obj = Update.de_json(update_json, application.bot)
        await application.process_update(update_obj)

    asyncio.run(process())
    return "ok"
