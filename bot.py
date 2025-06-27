mport os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from gsheets import write_to_sheet

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

# Стартовое меню
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(KeyboardButton("✅ Оставить заявку"))

# Кнопка согласия
agree_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
agree_keyboard.add(KeyboardButton("✅ Согласен с условиями ПД"))

# Временное хранилище заявок
user_data = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже, чтобы оставить заявку:", reply_markup=start_keyboard)

@dp.message_handler(lambda m: m.text == "✅ Оставить заявку")
async def ask_brand(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Укажи марку автомобиля:")

@dp.message_handler(lambda m: message.from_user.id in user_data and 'brand' not in user_data[m.from_user.id])
async def ask_model(message: types.Message):
    user_data[message.from_user.id]['brand'] = message.text
    await message.answer("Теперь укажи модель автомобиля:")

@dp.message_handler(lambda m: 'brand' in user_data.get(m.from_user.id, {}) and 'model' not in user_data[m.from_user.id])
async def ask_color(message: types.Message):
    user_data[message.from_user.id]['model'] = message.text
    await message.answer("Укажи цвет автомобиля:")

@dp.message_handler(lambda m: 'model' in user_data.get(m.from_user.id, {}) and 'color' not in user_data[m.from_user.id])
async def ask_phone(message: types.Message):
    user_data[message.from_user.id]['color'] = message.text
    await message.answer("Оставь номер телефона для связи:")

@dp.message_handler(lambda m: 'color' in user_data.get(m.from_user.id, {}) and 'phone' not in user_data[m.from_user.id])
async def ask_consent(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text
    await message.answer("Согласны ли вы с обработкой персональных данных?", reply_markup=agree_keyboard)

@dp.message_handler(lambda m: m.text == "✅ Согласен с условиями ПД")
async def submit(message: types.Message):
    data = user_data.get(message.from_user.id)
    if data:
        write_to_sheet(message.from_user.full_name, data['brand'], data['model'], data['color'], data['phone'])
        await message.answer("✅ Заявка принята! Мы с вами свяжемся.", reply_markup=types.ReplyKeyboardRemove())
        user_data.pop(message.from_user.id)
    else:
        await message.answer("Произошла ошибка. Пожалуйста, начните заново командой /start.")

if name == "main":
    executor.start_polling(dp, skip_updates=True)
