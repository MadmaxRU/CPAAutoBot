
import telebot
from telebot import types
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gsheets import save_to_sheet

BOT_TOKEN = 'YOUR_TOKEN'
GOOGLE_CREDS_JSON = 'YOUR_CREDENTIALS_JSON'
SHEET_ID = 'YOUR_SHEET_ID'

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

regions = ["Москва", "Санкт-Петербург", "Краснодар", "Екатеринбург", "Новосибирск", "Другой регион"]

@bot.message_handler(commands=['start', 'reset'])
def start_handler(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "🎯 Добро пожаловать! Здесь вы получите скидки до 20% и подарки на новое авто. 🚗\n\n👋 Давайте познакомимся! 🧑‍💼 Как вас зовут?")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "name" not in user_data[m.chat.id])
def name_handler(message):
    user_data[message.chat.id]["name"] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📱 Поделиться номером телефона", request_contact=True)
    keyboard.add(button)
    bot.send_message(message.chat.id, "📱 Поделитесь номером телефона:", reply_markup=keyboard)

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    if message.contact is not None:
        user_data[message.chat.id]["phone"] = message.contact.phone_number
        markup = types.ReplyKeyboardRemove()
        keyboard = types.InlineKeyboardMarkup()
        for region in regions:
            keyboard.add(types.InlineKeyboardButton(region, callback_data=f"region_{region}"))
        bot.send_message(message.chat.id, "🏙 В каком городе вы находитесь?", reply_markup=markup)
        bot.send_message(message.chat.id, "Выберите ваш город:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def region_handler(call):
    region = call.data.replace("region_", "")
    user_data[call.message.chat.id]["region"] = region
    save_to_sheet(user_data[call.message.chat.id])
    bot.send_message(call.message.chat.id, "✅ Спасибо! Ваша заявка принята. Наш специалист скоро свяжется с вами.\n\n🔁 Чтобы оставить новую заявку — введите /start")

bot.polling(none_stop=True)
