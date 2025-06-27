
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("✅ Оставить заявку"))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже, чтобы оставить заявку:", reply_markup=start_kb)

@dp.message_handler(lambda message: message.text == "✅ Оставить заявку")
async def ask_car_brand(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("🚗 Укажи марку автомобиля:")

@dp.message_handler(lambda message: "car_brand" not in user_data.get(message.from_user.id, {}))
async def get_car_brand(message: types.Message):
    user_data[message.from_user.id]["car_brand"] = message.text
    await message.answer("🏙️ Укажи город:")

@dp.message_handler(lambda message: "city" not in user_data.get(message.from_user.id, {}))
async def get_city(message: types.Message):
    user_data[message.from_user.id]["city"] = message.text
    await message.answer("📞 Укажи номер телефона:")

@dp.message_handler(lambda message: "phone" not in user_data.get(message.from_user.id, {}))
async def get_phone(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    await message.answer("🧑 Укажи своё имя:")

@dp.message_handler(lambda message: "name" not in user_data.get(message.from_user.id, {}))
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await ask_payment_method(message)

async def ask_payment_method(message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Наличные"), KeyboardButton("🏦 Кредит"), KeyboardButton("🔄 Лизинг"))
    kb.add(KeyboardButton("🚛 Заказ из-за границы"))
    await message.answer("💳 Выберите способ приобретения авто:", reply_markup=kb)

@dp.message_handler(lambda message: "acquisition" not in user_data.get(message.from_user.id, {}))
async def get_acquisition(message: types.Message):
    user_data[message.from_user.id]["acquisition"] = message.text
    await message.answer("📅 Какой год выпуска интересует (можно указать диапазон)?")

@dp.message_handler(lambda message: "year" not in user_data.get(message.from_user.id, {}))
async def get_year(message: types.Message):
    user_data[message.from_user.id]["year"] = message.text
    await message.answer("💸 Ваш примерный бюджет (₽)?")

@dp.message_handler(lambda message: "budget" not in user_data.get(message.from_user.id, {}))
async def get_budget(message: types.Message):
    user_data[message.from_user.id]["budget"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("✅ Согласен"), KeyboardButton("❌ Не согласен"))
    await message.answer("🛡️ Вы соглашаетесь с условиями обработки персональных данных?", reply_markup=kb)

@dp.message_handler(lambda message: message.text in ["✅ Согласен", "❌ Не согласен"])
async def final_step(message: types.Message):
    user_data[message.from_user.id]["consent"] = message.text
    if message.text == "✅ Согласен":
        await message.answer("🎉 Спасибо! Ваша заявка принята. Мы скоро свяжемся с вами.")
    else:
        await message.answer("❗ Без согласия с условиями мы не можем принять заявку.")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)
