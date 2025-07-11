import datetime
import gspread
import telebot
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# Получаем данные из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_ID = os.getenv("SHEET_ID")

# Авторизация в Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")

# Создаем бота
bot = telebot.TeleBot(BOT_TOKEN)

# Временное хранилище состояний
user_data = {}

# Старт
@bot.message_handler(commands=["start"])
def start_handler(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "Как вас зовут?")

# Имя
@bot.message_handler(func=lambda message: message.chat.id in user_data and "name" not in user_data[message.chat.id])
def handle_name(message):
    user_data[message.chat.id]["name"] = message.text
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Наличные", "Кредит", "Лизинг", "Трейд-ин")
    bot.send_message(message.chat.id, "Выберите способ покупки:", reply_markup=markup)

# Способ оплаты
@bot.message_handler(func=lambda message: message.chat.id in user_data and "payment" not in user_data[message.chat.id])
def handle_payment(message):
    user_data[message.chat.id]["payment"] = message.text
    bot.send_message(message.chat.id, "Введите марку автомобиля:")

# Марка авто
@bot.message_handler(func=lambda message: message.chat.id in user_data and "brand" not in user_data[message.chat.id])
def handle_brand(message):
    user_data[message.chat.id]["brand"] = message.text
    bot.send_message(message.chat.id, "Укажите бюджет:")

# Бюджет
@bot.message_handler(func=lambda message: message.chat.id in user_data and "budget" not in user_data[message.chat.id])
def handle_budget(message):
    user_data[message.chat.id]["budget"] = message.text
    bot.send_message(message.chat.id, "Укажите город:")

# Город
@bot.message_handler(func=lambda message: message.chat.id in user_data and "city" not in user_data[message.chat.id])
def handle_city(message):
    user_data[message.chat.id]["city"] = message.text
    bot.send_message(message.chat.id, "Оставьте ваш номер телефона:")

# Телефон
@bot.message_handler(func=lambda message: message.chat.id in user_data and "phone" not in user_data[message.chat.id])
def handle_phone(message):
    user_data[message.chat.id]["phone"] = message.text
    bot.send_message(message.chat.id, "Добавьте комментарий или удобное время для звонка:")

# Комментарий и финал
@bot.message_handler(func=lambda message: message.chat.id in user_data and "comment" not in user_data[message.chat.id])
def handle_comment(message):
    user_data[message.chat.id]["comment"] = message.text
    save_to_sheet(message.chat.id)
    bot.send_message(message.chat.id, "✅ Заявка принята. Мы свяжемся с вами в ближайшее время!")
    user_data.pop(message.chat.id)

# Сохраняем в Google Таблицу
def save_to_sheet(chat_id):
    data = user_data[chat_id]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data.get("payment", ""),
        data.get("brand", ""),
        "",  # Название юр лица
        "",  # Email
        f"{data.get('name', '')} | {data.get('phone', '')}",
        data.get("budget", ""),
        data.get("city", ""),
        data.get("comment", "")
    ]
    sheet.append_row(row)

bot.polling(none_stop=True)
