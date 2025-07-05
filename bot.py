
import asyncio
import logging
import os
import json

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from gsheet import write_to_gsheet

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=Bot.default_parse_mode.parse_mode = ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    method = State()
    brand = State()
    contacts = State()
    inn = State()
    entity = State()
    email = State()
    city = State()
    budget = State()
    comment = State()

start_buttons = ["Купить в кредит", "Купить за наличные", "Купить в лизинг", "Купить по трейд-ин"]
kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=b)] for b in start_buttons], resize_keyboard=True)

@dp.message(F.text.in_(start_buttons))
async def start_form(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(method=message.text)
    if message.text == "Купить в лизинг":
        await message.answer("Введите форму юрлица (ИП или ООО):")
        await state.set_state(Form.entity)
    else:
        await message.answer("Введите марку автомобиля:")
        await state.set_state(Form.brand)

@dp.message(Form.entity)
async def get_entity(message: Message, state: FSMContext):
    await state.update_data(entity=message.text)
    await message.answer("Введите ИНН:")
    await state.set_state(Form.inn)

@dp.message(Form.inn)
async def get_inn(message: Message, state: FSMContext):
    await state.update_data(inn=message.text)
    await message.answer("Введите email:")
    await state.set_state(Form.email)

@dp.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите город:")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Выберите бюджет:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in ["1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", ">10 млн"]],
        resize_keyboard=True
    ))
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Добавьте комментарий или удобное время для звонка:")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def get_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    await write_to_gsheet(data)
    await message.answer("Спасибо! Ваша заявка принята.")
    await state.clear()

@dp.message(Form.brand)
async def get_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Введите ваши контактные данные или нажмите кнопку ниже:",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
                             resize_keyboard=True))
    await state.set_state(Form.contacts)

@dp.message(Form.contacts)
async def get_contacts(message: Message, state: FSMContext):
    contact_text = message.contact.phone_number if message.contact else message.text
    await state.update_data(contacts=contact_text)
    await message.answer("Введите город:")
    await state.set_state(Form.city)

@dp.message()
async def fallback(message: Message):
    await message.answer("Пожалуйста, выберите способ покупки:", reply_markup=kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
