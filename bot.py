
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from gspread import service_account
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SHEET_ID = os.getenv("SHEET_ID")

# FSM состояние
class Form(StatesGroup):
    name = State()
    payment_method = State()
    car_brand = State()
    budget = State()
    city = State()
    phone = State()
    comment = State()

# Инициализация бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Наличные")],
            [KeyboardButton(text="Кредит")],
            [KeyboardButton(text="Лизинг")],
            [KeyboardButton(text="Трейд-ин")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Выберите способ покупки:", reply_markup=keyboard)
    await state.set_state(Form.payment_method)

@dp.message(Form.payment_method)
async def payment_handler(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await message.answer("Введите марку автомобиля:")
    await state.set_state(Form.car_brand)

@dp.message(Form.car_brand)
async def car_handler(message: types.Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("Укажите бюджет:")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def budget_handler(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Укажите город:")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def city_handler(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Оставьте ваш номер телефона:")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def phone_handler(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Добавьте комментарий или удобное время для звонка:")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def comment_handler(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    # Запись в Google Sheets
    write_to_gsheet([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("name"),
        data.get("payment_method"),
        data.get("car_brand"),
        data.get("budget"),
        data.get("city"),
        data.get("phone"),
        data.get("comment")
    ])

    await message.answer("Спасибо! Ваша заявка отправлена. Мы свяжемся с вами в ближайшее время.")
    await state.clear()

def write_to_gsheet(row):
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_JSON, [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    gc = service_account(filename=GOOGLE_CREDS_JSON)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1
    worksheet.append_row(row)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
