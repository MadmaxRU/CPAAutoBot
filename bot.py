
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

@bot.message_handler(commands=["start", "reset"])
def start_handler(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "👤 Как вас зовут?")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "name" not in user_data[message.chat.id])
def name_handler(message):
    user_data[message.chat.id]["name"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_btn = types.KeyboardButton("📞 Отправить номер", request_contact=True)
    markup.add(phone_btn)
    bot.send_message(message.chat.id, "📱 Поделитесь номером телефона:", reply_markup=markup)

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    user_data[message.chat.id]["phone"] = message.contact.phone_number
    bot.send_message(message.chat.id, "🏙 В каком городе вы находитесь?", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: message.chat.id in user_data and "phone" in user_data[message.chat.id] and "city" not in user_data[message.chat.id])
def city_handler(message):
    user_data[message.chat.id]["city"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    methods = ["Наличные", "Кредит", "Лизинг", "Трейд-ин"]
    for method in methods:
        markup.add(types.KeyboardButton(method))
    bot.send_message(message.chat.id, "💰 Какой способ покупки вас интересует?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_data and "payment_method" not in user_data[message.chat.id])
def payment_method_handler(message):
    user_data[message.chat.id]["payment_method"] = message.text
    if message.text == "Лизинг":
        bot.send_message(message.chat.id, "🏢 Укажите название юр. лица (ИП или ООО):")
    else:
        bot.send_message(message.chat.id, "🚗 Укажите марку автомобиля:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get("payment_method") == "Лизинг" and "company" not in user_data[message.chat.id])
def company_handler(message):
    user_data[message.chat.id]["company"] = message.text
    bot.send_message(message.chat.id, "📧 Укажите ваш email:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get("payment_method") == "Лизинг" and "email" not in user_data[message.chat.id])
def email_handler(message):
    user_data[message.chat.id]["email"] = message.text
    bot.send_message(message.chat.id, "🚗 Укажите марку автомобиля:")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "car_brand" not in user_data[message.chat.id])
def car_handler(message):
    user_data[message.chat.id]["car_brand"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    budget_options = ["1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", "Больше 10 млн"]
    for b in budget_options:
        markup.add(types.KeyboardButton(b))
    bot.send_message(message.chat.id, "💵 Укажите ваш бюджет:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.chat.id in user_data and "budget" not in user_data[message.chat.id])
def budget_handler(message):
    user_data[message.chat.id]["budget"] = message.text
    bot.send_message(message.chat.id, "🗓 Добавьте комментарий или удобное время для звонка (по желанию):")

@bot.message_handler(func=lambda message: message.chat.id in user_data and "comment" not in user_data[message.chat.id])
def comment_handler(message):
    user_data[message.chat.id]["comment"] = message.text

    # Отправка в таблицу
    data = user_data[message.chat.id]
    sheet.append_row([
        data.get("name", ""),
        data.get("phone", ""),
        data.get("city", ""),
        data.get("payment_method", ""),
        data.get("company", ""),
        data.get("email", ""),
        data.get("car_brand", ""),
        data.get("budget", ""),
        data.get("comment", ""),
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
    bot.send_message(message.chat.id, "✅ Заявка принята! Спасибо, мы свяжемся с вами.")

bot.infinity_polling()
