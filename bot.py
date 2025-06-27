
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from gsheets import write_to_sheet

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

user_data = {}

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("🚗 Оставить заявку"))

consent_kb = InlineKeyboardMarkup()
consent_kb.add(InlineKeyboardButton("✅ Согласен", callback_data="consent_yes"))
consent_kb.add(InlineKeyboardButton("❌ Не согласен", callback_data="consent_no"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы оставить заявку.", reply_markup=start_kb)

@dp.message_handler(lambda message: message.text == "🚗 Оставить заявку")
async def ask_brand(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Укажите марку автомобиля (можно на русском или английском):")

@dp.message_handler(lambda message: message.from_user.id in user_data and "brand" not in user_data[message.from_user.id])
async def ask_model(message: types.Message):
    user_data[message.from_user.id]["brand"] = message.text
    await message.answer("Укажите модель автомобиля:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "model" not in user_data[message.from_user.id])
async def ask_city(message: types.Message):
    user_data[message.from_user.id]["model"] = message.text
    await message.answer("Укажите ваш город:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "city" not in user_data[message.from_user.id])
async def ask_name(message: types.Message):
    user_data[message.from_user.id]["city"] = message.text
    await message.answer("Укажите ваше имя:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def ask_phone(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.answer("Укажите ваш номер телефона:")

@dp.message_handler(lambda message: message.from_user.id in user_data and "phone" not in user_data[message.from_user.id])
async def ask_payment(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Лизинг"), KeyboardButton("Кредит"), KeyboardButton("Наличные"))
    await message.answer("Какой способ оплаты вас интересует?", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "payment" not in user_data[message.from_user.id])
async def ask_year(message: types.Message):
    user_data[message.from_user.id]["payment"] = message.text
    await message.answer("Какой год выпуска интересует (можно указать диапазон)?")

@dp.message_handler(lambda message: message.from_user.id in user_data and "year" not in user_data[message.from_user.id])
async def ask_budget(message: types.Message):
    user_data[message.from_user.id]["year"] = message.text
    await message.answer("Ваш примерный бюджет (₽)?")

@dp.message_handler(lambda message: message.from_user.id in user_data and "budget" not in user_data[message.from_user.id])
async def ask_import(message: types.Message):
    user_data[message.from_user.id]["budget"] = message.text
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    await message.answer("Рассматриваете авто под заказ из-за границы?", reply_markup=kb)

@dp.message_handler(lambda message: message.from_user.id in user_data and "import_interest" not in user_data[message.from_user.id])
async def ask_consent(message: types.Message):
    user_data[message.from_user.id]["import_interest"] = message.text
    await message.answer("Вы соглашаетесь с условиями обработки персональных данных?", reply_markup=consent_kb)

@dp.callback_query_handler(lambda call: call.data in ["consent_yes", "consent_no"])
async def process_consent(call: types.CallbackQuery):
    if call.data == "consent_no":
        await call.message.answer("Заявка отменена.")
        user_data.pop(call.from_user.id, None)
    else:
        uid = call.from_user.id
        data = user_data.get(uid, {})
        write_to_sheet([
            data.get("brand"), data.get("model"), data.get("city"),
            data.get("name"), data.get("phone"), data.get("payment"),
            data.get("year"), data.get("budget"), data.get("import_interest")
        ])
        await call.message.answer("Спасибо! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.")
        user_data.pop(uid, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
