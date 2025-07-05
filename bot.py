
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from gsheet import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    name = State()
    city = State()
    brand = State()
    payment = State()
    region = State()
    agreement = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🚗 Купить авто"))
    await message.answer("Привет! Нажми на кнопку, чтобы начать.", reply_markup=markup)

@dp.message(lambda message: message.text == "🚗 Купить авто")
async def start_form(message: types.Message, state: FSMContext):
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Выбери город:")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введи марку автомобиля:")
    await state.set_state(Form.brand)

@dp.message(Form.brand)
async def process_brand(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Наличные"), KeyboardButton("Кредит"))
    await message.answer("Выбери способ оплаты:", reply_markup=markup)
    await state.set_state(Form.payment)

@dp.message(Form.payment)
async def process_payment(message: types.Message, state: FSMContext):
    await state.update_data(payment=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"), KeyboardButton("Нет"))
    await message.answer("Ты из другого региона?", reply_markup=markup)
    await state.set_state(Form.region)

@dp.message(Form.region)
async def process_region(message: types.Message, state: FSMContext):
    await state.update_data(region=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Да"))
    await message.answer("Согласен с политикой обработки данных?", reply_markup=markup)
    await state.set_state(Form.agreement)

@dp.message(Form.agreement)
async def process_agreement(message: types.Message, state: FSMContext):
    await state.update_data(agreement=message.text)
    data = await state.get_data()
    write_to_gsheet(data)
    await message.answer("Спасибо! Данные переданы. 🚗", reply_markup=ReplyKeyboardRemove())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
