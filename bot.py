import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from gsheet import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def make_keyboard(options):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        keyboard.add(KeyboardButton(opt))
    return keyboard

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("👋 Привет! Как тебя зовут?")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "name" not in user_data[msg.from_user.id])
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.answer("📱 Введи номер телефона:")

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "phone" not in user_data[msg.from_user.id])
async def get_phone(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    keyboard = make_keyboard(["Toyota", "Kia", "Chery", "Haval", "Geely"])
    await message.answer("🚗 Выбери марку авто:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "car_brand" not in user_data[msg.from_user.id])
async def get_brand(message: types.Message):
    user_data[message.from_user.id]["car_brand"] = message.text
    keyboard = make_keyboard(["2020", "2021", "2022", "2023", "2024"])
    await message.answer("📅 Выбери год выпуска:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "year" not in user_data[msg.from_user.id])
async def get_year(message: types.Message):
    user_data[message.from_user.id]["year"] = message.text
    keyboard = make_keyboard(["Наличные", "Кредит", "Рассрочка"])
    await message.answer("💳 Способ оплаты:", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "payment_method" not in user_data[msg.from_user.id])
async def get_payment(message: types.Message):
    user_data[message.from_user.id]["payment_method"] = message.text
    keyboard = make_keyboard(["Да", "Нет"])
    await message.answer("🌍 Вы находитесь за границей?", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "from_abroad" not in user_data[msg.from_user.id])
async def get_location(message: types.Message):
    user_data[message.from_user.id]["from_abroad"] = message.text
    keyboard = make_keyboard(["Согласен", "Не согласен"])
    await message.answer("✅ Согласны с обработкой данных?", reply_markup=keyboard)

@dp.message_handler(lambda msg: msg.from_user.id in user_data and "agreement" not in user_data[msg.from_user.id])
async def get_agreement(message: types.Message):
    user_data[message.from_user.id]["agreement"] = message.text

    data = user_data.pop(message.from_user.id)
    data["lead_type"] = "bot_lead"
    data["city"] = "Москва"

    write_to_gsheet(data)
    await message.answer("🎉 Спасибо! Мы свяжемся с Вами!.", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
