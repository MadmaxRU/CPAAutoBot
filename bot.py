import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("CPAauto").sheet1

# === FSM States ===
class Form(StatesGroup):
    name = State()
    payment = State()
    car_brand = State()
    budget = State()
    contact = State()
    comment = State()

# === Start ===
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Как вас зовут?")
    await Form.name.set()

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Купить в кредит", "Купить за наличные", "Купить в трейд-ин", "Лизинг")
    await message.answer("Выберите способ покупки:", reply_markup=kb)
    await Form.payment.set()

@dp.message_handler(state=Form.payment)
async def process_payment(message: types.Message, state: FSMContext):
    await state.update_data(payment=message.text)
    await message.answer("Введите марку автомобиля:", reply_markup=types.ReplyKeyboardRemove())
    await Form.car_brand.set()

@dp.message_handler(state=Form.car_brand)
async def process_car_brand(message: types.Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("Укажите бюджет:")
    await Form.budget.set()

@dp.message_handler(state=Form.budget)
async def process_budget(message: types.Message, state: FSMContext):
    await state.update_data(budget=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("Отправить номер телефона", request_contact=True))
    await message.answer("Оставьте ваш номер телефона:", reply_markup=kb)
    await Form.contact.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.contact.phone_number)
    await message.answer("Добавьте комментарий или удобное время для звонка:", reply_markup=types.ReplyKeyboardRemove())
    await Form.comment.set()

@dp.message_handler(state=Form.comment)
async def process_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("payment", ""),
        data.get("car_brand", ""),
        data.get("name", ""),
        data.get("contact", ""),
        data.get("budget", ""),
        message.from_user.city if hasattr(message.from_user, "city") else "",
        data.get("comment", "")
    ]

    try:
        sheet.append_row(row)
        await message.answer("Спасибо! Заявка отправлена ✅")
    except Exception as e:
        logging.error(f"Ошибка при записи в таблицу: {e}")
        await message.answer("Произошла ошибка при сохранении данных. Попробуйте позже.")

    await state.finish()
