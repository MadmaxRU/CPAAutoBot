
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка доступа к Google Таблицам
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Открытие таблицы
sheet = client.open("CPAauto Leads").sheet1

def send_to_google_sheet(data):
    row = [
        data.get("name", ""),
        data.get("method", ""),
        data.get("brand", ""),
        data.get("budget", ""),
        data.get("city", ""),
        data.get("phone", "")
    ]
    sheet.append_row(row)



import telebot
from telebot import types

bot = telebot.TeleBot("YOUR_TELEGRAM_BOT_TOKEN")

user_data = {}

def reset_user(chat_id):
    user_data[chat_id] = {
        "state": "ask_name",
        "data": {}
    }

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    reset_user(chat_id)
    bot.send_message(chat_id, "Привет! Как к вам можно обращаться?")

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    user_data[chat_id]["data"]["phone"] = phone

    finish_submission(chat_id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        reset_user(chat_id)

    state = user_data[chat_id]["state"]
    text = message.text.strip()

    if state == "ask_name":
        user_data[chat_id]["data"]["name"] = text
        user_data[chat_id]["state"] = "ask_method"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("Наличные", "Кредит", "Лизинг", "Трейд-ин")
        bot.send_message(chat_id, "Выберите способ покупки:", reply_markup=markup)

    elif state == "ask_method":
        user_data[chat_id]["data"]["method"] = text
        user_data[chat_id]["state"] = "ask_brand"
        bot.send_message(chat_id, "Введите марку автомобиля:", reply_markup=types.ReplyKeyboardRemove())

    elif state == "ask_brand":
        user_data[chat_id]["data"]["brand"] = text
        user_data[chat_id]["state"] = "ask_budget"
        bot.send_message(chat_id, "Укажите бюджет:")

    elif state == "ask_budget":
        user_data[chat_id]["data"]["budget"] = text
        user_data[chat_id]["state"] = "ask_city"
        bot.send_message(chat_id, "Укажите город:")

    elif state == "ask_city":
        user_data[chat_id]["data"]["city"] = text
        user_data[chat_id]["state"] = "ask_phone"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton("📱 Поделиться номером телефона", request_contact=True)
        markup.add(button)
        bot.send_message(chat_id, "Оставьте ваш номер телефона:", reply_markup=markup)

    elif state == "ask_phone":
        user_data[chat_id]["data"]["phone"] = text
        finish_submission(chat_id)

def finish_submission(chat_id):
    data = user_data[chat_id]["data"]

    send_to_google_sheet(data)

    # Отправка финального сообщения
    msg = f"""✅ Спасибо, {data.get('name', '')}! Ваша заявка принята.
📌 Способ покупки: {data.get('method')}
🚗 Марка авто: {data.get('brand')}
💰 Бюджет: {data.get('budget')}
📍 Город: {data.get('city')}
📞 Телефон: {data.get('phone')}"""
    )
    bot.send_message(chat_id, msg, reply_markup=types.ReplyKeyboardRemove())

    # Предложение отправить новую заявку
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔄 Отправить ещё одну заявку")
    bot.send_message(chat_id, "Хотите отправить ещё одну заявку?", reply_markup=markup)

    user_data[chat_id]["state"] = "wait_restart"

@bot.message_handler(func=lambda message: message.text == "🔄 Отправить ещё одну заявку")
def restart(message):
    start(message)

bot.polling(none_stop=True)
