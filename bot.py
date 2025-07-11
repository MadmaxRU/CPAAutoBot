
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Contact
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

# FSM состояния
class Form(StatesGroup):
    name = State()
    payment_method = State()
    car_brand = State()
    budget = State()
    contact = State()
    comment = State()

# Бот и диспетчер
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Обработка команды /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Как вас зовут?")

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.payment_method)
    await message.answer("Выберите способ покупки:
1. Кредит
2. Наличные
3. Лизинг
4. Купить в трейд-ин")

@dp.message(Form.payment_method)
async def get_payment_method(message: Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await state.set_state(Form.car_brand)
    await message.answer("Введите марку автомобиля:")

@dp.message(Form.car_brand)
async def get_car_brand(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await state.set_state(Form.budget)
    await message.answer("Укажите бюджет:")

@dp.message(Form.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await state.set_state(Form.contact)
    await message.answer("Оставьте ваш номер телефона:")

@dp.message(Form.contact)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(Form.comment)
    await message.answer("Добавьте комментарий или удобное время для звонка:")

@dp.message(Form.comment)
async def get_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    # Сохраняем в Google Таблицу
    await write_to_gsheet(data)

    await message.answer("Спасибо! Ваша заявка отправлена.")
    await state.clear()

async def write_to_gsheet(data):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = [now, data.get("payment_method"), data.get("car_brand"), "", data.get("contact"),
           data.get("budget"), "", data.get("comment"), data.get("name")]
    sheet.append_row(row)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
