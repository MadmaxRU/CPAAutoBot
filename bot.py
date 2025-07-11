
import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# FSM состояния
class Form(StatesGroup):
    name = State()
    payment_method = State()
    car_brand = State()
    budget = State()
    city = State()
    contact = State()
    company_info = State()
    inn = State()
    email = State()
    comment = State()

# Настройки логирования
logging.basicConfig(level=logging.INFO)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# Настройка Google Sheets
def write_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    sheet.append_row(data)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Как вас зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
    "Выберите способ покупки:\n"
    "1. Наличные\n"
    "2. Кредит\n"
    "3. Лизинг\n"
    "4. Трейд-ин"
)
    await state.set_state(Form.payment_method)

@dp.message(Form.payment_method)
async def payment_handler(message: Message, state: FSMContext):
    method = message.text.strip().lower()
    await state.update_data(payment_method=method)
    await message.answer("Введите марку автомобиля:")
    await state.set_state(Form.car_brand)

@dp.message(Form.car_brand)
async def brand_handler(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("Укажите бюджет:")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def budget_handler(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Укажите город:")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def city_handler(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Оставьте ваш номер телефона:")
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def contact_handler(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    if "лизинг" in data.get("payment_method", "").lower():
        await message.answer("Введите форму юр. лица (ИП или ООО):")
        await state.set_state(Form.company_info)
    else:
        await message.answer("Добавьте комментарий или удобное время для звонка:")
        await state.set_state(Form.comment)

@dp.message(Form.company_info)
async def company_info_handler(message: Message, state: FSMContext):
    await state.update_data(company_info=message.text)
    await message.answer("Введите ИНН:")
    await state.set_state(Form.inn)

@dp.message(Form.inn)
async def inn_handler(message: Message, state: FSMContext):
    await state.update_data(inn=message.text)
    await message.answer("Укажите email:")
    await state.set_state(Form.email)

@dp.message(Form.email)
async def email_handler(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Добавьте комментарий или удобное время для звонка:")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def comment_handler(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("payment_method", ""),
        data.get("car_brand", ""),
        f'{data.get("company_info", "")} {data.get("email", "")}' if "лизинг" in data.get("payment_method", "").lower() else "",
        data.get("contact", ""),
        data.get("budget", ""),
        data.get("city", ""),
        data.get("comment", ""),
        data.get("name", ""),
        data.get("inn", "") if "лизинг" in data.get("payment_method", "").lower() else ""
    ]
    write_to_gsheet(row)
    await message.answer("Спасибо! Ваша заявка отправлена. Наш специалист скоро с вами свяжется.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
