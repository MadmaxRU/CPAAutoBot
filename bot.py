
import logging
import os
import json

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

from dotenv import load_dotenv
from gsheets import write_to_gsheet

load_dotenv()

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Состояния
class Form:
    waiting_for_payment_method = "waiting_for_payment_method"
    waiting_for_brand = "waiting_for_brand"
    waiting_for_legal_info = "waiting_for_legal_info"
    waiting_for_contact_info = "waiting_for_contact_info"
    waiting_for_comment = "waiting_for_comment"

user_data = {}

start_buttons = ["🚗 Купить авто", "📞 Связаться с менеджером"]
start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [types.KeyboardButton(text=btn)] for btn in start_buttons
])

budget_buttons = ["1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", ">10 млн"]
budget_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [types.KeyboardButton(text=btn)] for btn in budget_buttons
])

payment_buttons = ["Купить в кредит", "Купить за наличные", "Купить в лизинг"]
payment_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [types.KeyboardButton(text=btn)] for btn in payment_buttons
])

@router.message(Command("start"))
@router.message(lambda message: message.text == "🚗 Купить авто")
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Как планируете оплачивать автомобиль?", reply_markup=payment_kb)
    await state.set_state(Form.waiting_for_payment_method)
    user_data[message.from_user.id] = {}

@router.message(lambda msg: msg.text in payment_buttons)
async def payment_method_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["Оплата"] = message.text
    await message.answer("Введите марку автомобиля:")
    await state.set_state(Form.waiting_for_brand)

@router.message(lambda msg: msg.text not in payment_buttons and msg.text not in start_buttons)
async def brand_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["Марка"] = message.text
    if user_data[message.from_user.id]["Оплата"] == "Купить в лизинг":
        await message.answer("Введите ИНН:")
        await state.set_state(Form.waiting_for_legal_info)
    else:
        await message.answer("Введите ваши контактные данные:")
        await state.set_state(Form.waiting_for_contact_info)

@router.message(lambda msg: msg.text and "ИНН" not in user_data.get(msg.from_user.id, {}))
async def inn_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["ИНН"] = message.text
    await message.answer("Выберите бюджет:", reply_markup=budget_kb)
    await state.set_state(Form.waiting_for_contact_info)

@router.message(lambda msg: msg.text in budget_buttons)
async def budget_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["Бюджет"] = message.text
    await message.answer("Введите город:")
    await state.set_state(Form.waiting_for_comment)

@router.message(lambda msg: msg.text and "Город" not in user_data.get(msg.from_user.id, {}))
async def city_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["Город"] = message.text
    await message.answer("Добавьте комментарий или удобное время для звонка (или отправьте - ):")
    await state.set_state(Form.waiting_for_comment)

@router.message()
async def comment_handler(message: Message, state: FSMContext):
    user_data[message.from_user.id]["Комментарий"] = message.text
    await write_to_gsheet(user_data[message.from_user.id])
    await message.answer("Спасибо! Ваши данные записаны.", reply_markup=start_kb)
    await state.clear()

@router.message(lambda msg: msg.text == "📞 Связаться с менеджером")
async def manager_contact(message: Message):
    await message.answer("Менеджер скоро с вами свяжется.", reply_markup=start_kb)

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
