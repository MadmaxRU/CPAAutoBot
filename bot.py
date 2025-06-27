import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
from gsheets import write_to_sheet

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class LeadForm(StatesGroup):
    name = State()
    phone = State()
    city = State()
    car_brand = State()
    payment_method = State()
    from_abroad = State()
    agreement = State()

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать!

Давайте подберем авто. Как вас зовут?")
    await LeadForm.name.set()

@dp.message_handler(state=LeadForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш номер телефона:")
    await LeadForm.phone.set()

@dp.message_handler(state=LeadForm.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙 В каком городе вы находитесь?")
    await LeadForm.city.set()

@dp.message_handler(state=LeadForm.city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("🚗 Какая марка авто вас интересует?")
    await LeadForm.car_brand.set()

@dp.message_handler(state=LeadForm.car_brand)
async def get_brand(message: types.Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💳 Кредит", "💼 Лизинг", "💰 Наличные")
    await message.answer("💸 Какой способ оплаты вас интересует?", reply_markup=keyboard)
    await LeadForm.payment_method.set()

@dp.message_handler(state=LeadForm.payment_method)
async def get_payment(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🇷🇺 Только РФ", "🌍 Хочу авто из-за границы")
    await message.answer("🚚 Нужно ли привезти авто из-за границы?", reply_markup=keyboard)
    await LeadForm.from_abroad.set()

@dp.message_handler(state=LeadForm.from_abroad)
async def get_from_abroad(message: types.Message, state: FSMContext):
    await state.update_data(from_abroad=message.text)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Согласен", callback_data="agree"))
    await message.answer("🛡 Подтвердите согласие на обработку персональных данных", reply_markup=kb)
    await LeadForm.agreement.set()

@dp.callback_query_handler(lambda c: c.data == "agree", state=LeadForm.agreement)
async def agreement_done(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Согласие получено!")
    data = await state.get_data()
    write_to_sheet(data)
    await bot.send_message(callback_query.from_user.id, "✅ Заявка отправлена! Мы скоро свяжемся с вами.")
    await state.finish()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
