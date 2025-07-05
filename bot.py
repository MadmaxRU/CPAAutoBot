import os
import asyncio
from aiogram import Bot, Dispatcher, types 
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from gsheets import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🚗 Купить авто"))
    await message.answer("Привет! Нажми на кнопку, чтобы начать.", reply_markup=markup)

@dp.message_handler(lambda message: message.text == "🚗 Купить авто")
async def ask_name(message: types.Message):
    await message.answer("Как тебя зовут?")
    user_data[message.from_user.id] = {}

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("name"))
async def ask_city(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Москва"), KeyboardButton("Санкт-Петербург"))
    await message.answer("Выбери город:", reply_markup=markup)

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("city"))
async def ask_brand(message: types.Message):
    user_data[message.from_user.id]["city"] = message.text
    await message.answer("Напиши марку автомобиля:")

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("car_brand"))
async def ask_payment(message: types.Message):
    user_data[message.from_user.id]["car_brand"] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Кредит"), KeyboardButton("Наличные"))
    await message.answer("Выбери способ оплаты:", reply_markup=markup)

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("payment_method"))
async def ask_region(message: types.Message):
    user_data[message.from_user.id]["payment_method"] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    await message.answer("Ты из другого региона?", reply_markup=markup)

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("from_abroad"))
async def ask_agreement(message: types.Message):
    user_data[message.from_user.id]["from_abroad"] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    await message.answer("Согласен с политикой обработки данных?", reply_markup=markup)

@dp.message_handler(lambda message: message.from_user.id in user_data and not user_data[message.from_user.id].get("agreement"))
async def finish(message: types.Message):
    user_data[message.from_user.id]["agreement"] = message.text
    data = {
        "lead_type": "auto",
        "name": user_data[message.from_user.id]["name"],
        "city": user_data[message.from_user.id]["city"],
        "car_brand": user_data[message.from_user.id]["car_brand"],
        "payment_method": user_data[message.from_user.id]["payment_method"],
        "phone": f"+{message.from_user.id}",
        "from_abroad": user_data[message.from_user.id]["from_abroad"],
        "agreement": user_data[message.from_user.id]["agreement"]
    }
    write_to_gsheet(data)
    await message.answer("Спасибо! Данные отправлены.")
    user_data.pop(message.from_user.id)

async def main():
    await dp.start_polling()

if name == "main":
    asyncio.run(main())
