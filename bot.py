
import os
import json
import random
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[KeyboardButton("📞 Отправить номер", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(kb, one_time_keyboard=True)
    await update.message.reply_text("Привет! Отправь свой номер телефона:", reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user_id = str(update.message.from_user.id)
    db = load_db()
    db[user_id] = {
        "phone_number": contact.phone_number,
        "chat_id": user_id
    }
    save_db(db)
    await update.message.reply_text("Спасибо! Номер сохранён.")

async def send_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    db = load_db()
    if user_id in db:
        code = str(random.randint(1000, 9999))
        db[user_id]["code"] = code
        save_db(db)
        await update.message.reply_text(f"Ваш код подтверждения: {code}")
    else:
        await update.message.reply_text("Сначала отправьте свой номер.")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Использование: /notify chat_id сообщение")
        return
    chat_id = args[0]
    text = " ".join(args[1:])
    await context.bot.send_message(chat_id=chat_id, text=text)
    await update.message.reply_text("Уведомление отправлено.")

def handle_update(update_json):
    from telegram import Update
    from telegram.ext import Application

    async def process():
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("sendcode", send_code))
        application.add_handler(CommandHandler("notify", notify))
        application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
        update = Update.de_json(update_json, application.bot)
        await application.process_update(update)

    import asyncio
    asyncio.run(process())
    return "OK"
