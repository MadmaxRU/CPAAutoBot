
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from gsheet import write_to_gsheet
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class LeadForm(StatesGroup):
    method = State()
    car = State()
    budget = State()
    city = State()
    company_type = State()
    inn = State()
    email = State()
    contact = State()
    comment = State()

@dp.message()
async def start_handler(message: Message, state: FSMContext):
    if message.text.lower() in ["/start", "начать", "привет"]:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Купить в кредит")],
                      [KeyboardButton(text="Купить за наличные")],
                      [KeyboardButton(text="Купить в лизинг")],
                      [KeyboardButton(text="Купить по трейд-ин")]],
            resize_keyboard=True
        )
        await message.answer("Привет! Выберите способ покупки:", reply_markup=kb)
        await state.set_state(LeadForm.method)
        return

    current_state = await state.get_state()

    if current_state == LeadForm.method:
        await state.update_data(method=message.text)
        await message.answer("Введите марку автомобиля:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(LeadForm.car)

    elif current_state == LeadForm.car:
        await state.update_data(car=message.text)
        await message.answer("Укажите ваш бюджет (1–2 млн, 2–4 млн, 4–6 млн, 6–10 млн, >10 млн):")
        await state.set_state(LeadForm.budget)

    elif current_state == LeadForm.budget:
        await state.update_data(budget=message.text)
        await message.answer("Укажите ваш город:")
        await state.set_state(LeadForm.city)

    elif current_state == LeadForm.city:
        await state.update_data(city=message.text)
        user_data = await state.get_data()
        if user_data["method"].lower().endswith("лизинг"):
            await message.answer("Вы ИП или ООО?")
            await state.set_state(LeadForm.company_type)
        else:
            kb = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Отправить номер телефона 📱", request_contact=True)]],
                resize_keyboard=True
            )
            await message.answer("Введите ваши контактные данные или нажмите кнопку ниже:", reply_markup=kb)
            await state.set_state(LeadForm.contact)

    elif current_state == LeadForm.company_type:
        await state.update_data(company_type=message.text)
        await message.answer("Введите ИНН:")
        await state.set_state(LeadForm.inn)

    elif current_state == LeadForm.inn:
        await state.update_data(inn=message.text)
        await message.answer("Введите ваш email:")
        await state.set_state(LeadForm.email)

    elif current_state == LeadForm.email:
        await state.update_data(email=message.text)
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отправить номер телефона 📱", request_contact=True)]],
            resize_keyboard=True
        )
        await message.answer("Введите ваши контактные данные или нажмите кнопку ниже:", reply_markup=kb)
        await state.set_state(LeadForm.contact)

    elif current_state == LeadForm.contact:
        contact = message.text
        if message.contact:
            contact = message.contact.phone_number
        await state.update_data(contact=contact)
        await message.answer("Можете добавить комментарий или удобное время для звонка (по желанию):")
        await state.set_state(LeadForm.comment)

    elif current_state == LeadForm.comment:
        await state.update_data(comment=message.text)
        data = await state.get_data()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        values = [
            now,
            data.get("method", ""),
            data.get("car", ""),
            data.get("budget", ""),
            data.get("city", ""),
            data.get("company_type", ""),
            data.get("inn", ""),
            data.get("email", ""),
            data.get("contact", ""),
            data.get("comment", "")
        ]
        await write_to_gsheet(values)
        await message.answer("Спасибо! Ваша заявка принята ✅", reply_markup=ReplyKeyboardRemove())
        await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
