
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("✅ Оставить заявку"))

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже, чтобы оставить заявку:", reply_markup=start_keyboard)

@dp.message_handler(lambda message: message.text == "✅ Оставить заявку")
async def ask_car_brand(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await message.answer("Укажи марку автомобиля:")

@dp.message_handler(lambda message: "car_brand" not in user_data.get(message.from_user.id, {}))
async def get_car_brand(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]["car_brand"] = message.text
    await message.answer("В каком городе вы находитесь?")

@dp.message_handler(lambda message: "location" not in user_data.get(message.from_user.id, {}) and "car_brand" in user_data.get(message.from_user.id, {}))
async def get_location(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["location"] = message.text
    await message.answer("Введите ваше имя:")

@dp.message_handler(lambda message: "name" not in user_data.get(message.from_user.id, {}) and "location" in user_data.get(message.from_user.id, {}))
async def get_name(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text
    await message.answer("Введите номер телефона:")

@dp.message_handler(lambda message: "phone" not in user_data.get(message.from_user.id, {}) and "name" in user_data.get(message.from_user.id, {}))
async def get_phone(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["phone"] = message.text
    await message.answer("Какой способ оплаты вас интересует? (Лизинг / Кредит / Наличные)")

@dp.message_handler(lambda message: "payment" not in user_data.get(message.from_user.id, {}) and "phone" in user_data.get(message.from_user.id, {}))
async def get_payment(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["payment"] = message.text
    await message.answer("Какой год выпуска интересует (можно указать диапазон)?")

@dp.message_handler(lambda message: "year" not in user_data.get(message.from_user.id, {}) and "payment" in user_data.get(message.from_user.id, {}))
async def get_year(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["year"] = message.text
    await message.answer("Ваш примерный бюджет (₽)?")

@dp.message_handler(lambda message: "budget" not in user_data.get(message.from_user.id, {}) and "year" in user_data.get(message.from_user.id, {}))
async def get_budget(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["budget"] = message.text
    await message.answer("Рассматриваете авто под заказ из-за границы? (Да / Нет)")

@dp.message_handler(lambda message: "import" not in user_data.get(message.from_user.id, {}) and "budget" in user_data.get(message.from_user.id, {}))
async def get_import_option(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["import"] = message.text
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Согласен", callback_data="agree"),
        InlineKeyboardButton("❌ Не согласен", callback_data="disagree")
    )
    await message.answer("Вы соглашаетесь с условиями обработки персональных данных?", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data in ["agree", "disagree"])
async def process_agreement(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_data[user_id]["agreement"] = call.data
    if call.data == "agree":
        await call.message.answer("✅ Заявка принята! Мы с вами свяжемся.")
    else:
        await call.message.answer("❌ Без согласия на обработку данных мы не можем продолжить.")

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
