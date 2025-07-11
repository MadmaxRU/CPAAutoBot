import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from gsheet import write_to_gsheet
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=Bot.default_parse_mode(ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    method = State()
    company_type = State()
    inn = State()
    email = State()
    brand = State()
    budget = State()
    city = State()
    contact = State()
    comment = State()

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Купить в кредит")],
        [KeyboardButton(text="Купить за наличные")],
        [KeyboardButton(text="Купить в лизинг")],
        [KeyboardButton(text="Купить по трейд-ин")]
    ],
    resize_keyboard=True
)

budget_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1-2 млн"), KeyboardButton(text="2-4 млн")],
        [KeyboardButton(text="4-6 млн"), KeyboardButton(text="6-10 млн")],
        [KeyboardButton(text="Более 10 млн")]
    ],
    resize_keyboard=True
)

@dp.message(F.text.in_(["Купить в кредит", "Купить за наличные", "Купить в лизинг", "Купить по трейд-ин"]))
async def choose_method(message: Message, state: FSMContext):
    await state.set_state(Form.method)
    await state.update_data(method=message.text)

    if message.text == "Купить в лизинг":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="ИП"), KeyboardButton(text="ООО")]
            ],
            resize_keyboard=True
        )
        await message.answer("Выберите форму юр. лица:", reply_markup=kb)
        await state.set_state(Form.company_type)
    else:
        await message.answer("Введите марку автомобиля:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.brand)

@dp.message(Form.company_type)
async def get_company_type(message: Message, state: FSMContext):
    await state.update_data(company_type=message.text)
    await message.answer("Введите ИНН:")
    await state.set_state(Form.inn)

@dp.message(Form.inn)
async def get_inn(message: Message, state: FSMContext):
    await state.update_data(inn=message.text)
    await message.answer("Введите e-mail:")
    await state.set_state(Form.email)

@dp.message(Form.email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите марку автомобиля:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.brand)

@dp.message(Form.brand)
async def get_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Укажите бюджет:", reply_markup=budget_kb)
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def get_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Укажите город:")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить телефон", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Введите ваши контактные данные или отправьте номер:", reply_markup=contact_kb)
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def get_contact(message: Message, state: FSMContext):
    contact = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=contact)
    await message.answer("Добавьте комментарий или удобное время для звонка (или нажмите Пропустить):")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def get_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    write_to_gsheet(data)
    await message.answer("Спасибо! Ваша заявка отправлена.")
    await state.clear()

@dp.message()
async def fallback(message: Message):
    await message.answer("Выберите действие:", reply_markup=start_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
