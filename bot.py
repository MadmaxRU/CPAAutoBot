
import datetime
import gspread
import telebot
from telebot import types
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_ID = os.getenv("SHEET_ID")

# Авторизация в Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

regions = ["Москва", "Санкт-Петербург", "Краснодар", "Екатеринбург", "Новосибирск", "Другой регион"]
brands = ["Toyota", "BMW", "Hyundai", "Kia", "Lada", "Mercedes", "Volkswagen", "Audi", "Chery", "Haval"]

@bot.message_handler(commands=["start", "reset"])
def start_handler(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "🎯 Добро пожаловать! Здесь вы получите максимальную скидку на новое авто. 🚗")

bot.send_message(message.chat.id, "👋 Давайте познакомимся! 👤 Как вас зовут?")
@bot.message_handler(func=lambda m: m.chat.id in user_data and "name" not in user_data[m.chat.id])
def name_handler(message):
    user_data[message.chat.id]["name"] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📱 Поделиться номером телефона", request_contact=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, "📱 Поделитесь номером телефона:", reply_markup=keyboard)

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_data[message.chat.id]["contact"] = message.contact.phone_number
    keyboard = types.InlineKeyboardMarkup()
    for region in regions:
        keyboard.add(types.InlineKeyboardButton(text=region, callback_data=f"region_{region}"))
    bot.send_message(message.chat.id, "🏙️ В каком городе вы находитесь?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def region_handler(call):
    region = call.data.split("_", 1)[1]
    user_data[call.message.chat.id]["city"] = region
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        ("💵 Наличные", "pay_cash"),
        ("💳 Кредит", "pay_credit"),
        ("📄 Лизинг", "pay_leasing"),
        ("♻️ Трейд-ин", "pay_tradein")
    ]
    for label, cb in buttons:
        keyboard.add(types.InlineKeyboardButton(label, callback_data=cb))
    bot.send_message(call.message.chat.id, "💰 Какой способ покупки вас интересует?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def payment_handler(call):
    pay_type = call.data.split("_", 1)[1]
    user_data[call.message.chat.id]["payment"] = pay_type
    bot.send_message(call.message.chat.id, "🚗 Укажите марку автомобиля:")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "brand" not in user_data[m.chat.id])
def brand_handler(message):
    user_data[message.chat.id]["brand"] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    options = ["1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", "Больше 10 млн"]
    for opt in options:
        keyboard.add(opt)
    bot.send_message(message.chat.id, "💵 Укажите ваш бюджет:", reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.chat.id in user_data and "budget" not in user_data[m.chat.id])
def budget_handler(message):
    user_data[message.chat.id]["budget"] = message.text
    bot.send_message(message.chat.id, "🗓️ Добавьте комментарий или удобное время для звонка (по желанию):")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "comment" not in user_data[m.chat.id])
def comment_handler(message):
    user_data[message.chat.id]["comment"] = message.text
    save_to_sheet(message.chat.id)
    bot.send_message(message.chat.id, "✅ Заявка успешно отправлена!
📞 Наш специалист свяжется с вами в ближайшее время.")
    bot.send_message(message.chat.id, "🔁 Чтобы начать заново, нажмите /start")

def save_to_sheet(chat_id):
    data = user_data.get(chat_id, {})
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data.get("payment", ""),
        data.get("brand", ""),
        "",  # Название юр.лица — необязательное
        "",  # email — необязательное
        f"{data.get('name', '')}, {data.get('contact', '')}",
        data.get("budget", ""),
        data.get("city", ""),
        data.get("comment", "")
    ]
    sheet.append_row(row)

bot.polling(none_stop=True)
