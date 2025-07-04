from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import os
from gsheet import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("🚗 Купить авто"))

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("Привет! Нажми на кнопку, чтобы начать.", reply_markup=start_kb)

@dp.message_handler(lambda message: message.text == "🚗 Купить авто")
async def ask_name(message: types.Message):
    await message.answer("Как тебя зовут?")
    user_data[message.from_user.id] = {}

@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Москва", "Санкт-Петербург", "Казань")
    await message.answer("Выбери город:", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "city" not in user_data[message.from_user.id])
async def get_city(message: types.Message):
    user_data[message.from_user.id]["city"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Toyota", "Lada", "Kia", "Chery")
    await message.answer("Выбери марку автомобиля:", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "car_brand" not in user_data[message.from_user.id])
async def get_car(message: types.Message):
    user_data[message.from_user.id]["car_brand"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Кредит", "Наличные", "Рассрочка")
    await message.answer("Выбери способ оплаты:", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "payment_method" not in user_data[message.from_user.id])
async def get_payment(message: types.Message):
    user_data[message.from_user.id]["payment_method"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет")
    await message.answer("Ты из другого региона?", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "from_abroad" not in user_data[message.from_user.id])
async def get_from_abroad(message: types.Message):
    user_data[message.from_user.id]["from_abroad"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет")
    await message.answer("Согласен с политикой обработки данных?", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "agreement" not in user_data[message.from_user.id])
async def get_agreement(message: types.Message):
    user_data[message.from_user.id]["agreement"] = message.text
    user_data[message.from_user.id]["phone"] = f"+{message.from_user.id}"
    user_data[message.from_user.id]["lead_type"] = "bot"

    write_to_gsheet(user_data[message.from_user.id])
    await message.answer("Спасибо! Данные отправлены ✅")
    del user_data[message.from_user.id]

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
