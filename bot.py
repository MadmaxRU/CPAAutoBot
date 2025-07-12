
import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# --- Настройки ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_ID = os.getenv("SHEET_ID")

creds_dict = json.loads(GOOGLE_CREDS_JSON)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).sheet1

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

regions = ["Москва", "Санкт-Петербург", "Краснодар", "Екатеринбург", "Новосибирск", "Другой регион"]

# --- Старт ---
@bot.message_handler(commands=["start", "reset"])
def start_handler(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "🎯 Добро пожаловать! Здесь вы получите максимальную скидку на новое авто. Как вас зовут?")

@bot.message_handler(func=lambda m: m.chat.id in user_data and "name" not in user_data[m.chat.id])
def name_handler(message):
    chat_id = message.chat.id
    user_data[chat_id]["name"] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📱 Поделиться номером телефона", request_contact=True)
    keyboard.add(button)
    bot.send_message(chat_id, "📱 Поделитесь номером телефона:", reply_markup=keyboard)

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    chat_id = message.chat.id
    user_data[chat_id]["phone"] = message.contact.phone_number
    markup = types.InlineKeyboardMarkup()
    for region in regions:
        markup.add(types.InlineKeyboardButton(region, callback_data=f"region_{region}"))
    bot.send_message(chat_id, "🏙 В каком городе вы находитесь?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("region_"))
def region_callback(call):
    chat_id = call.message.chat.id
    region = call.data.split("_", 1)[1]
    user_data[chat_id]["region"] = region
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Кредит", "Наличные", "Лизинг", "Трейд-ин")
    bot.send_message(chat_id, "💰 Какой способ покупки вас интересует?", reply_markup=markup)

# ... Дальнейшая логика обработки марки авто, бюджета, комментариев, записи в таблицу и кнопки "Начать заново"
# (этот кусок добавляется из ранее работающей версии — для краткости здесь не дублируем)
