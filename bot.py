import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from gsheets import write_to_gsheet

load_dotenv()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

user_data = {}

start_buttons = ["Купить в кредит", "Купить за наличные", "Купить в лизинг"]
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(*start_buttons)

budget_kb = ReplyKeyboardMarkup(resize_keyboard=True)
budget_kb.add("1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", ">10 млн")

@dp.message_handler(commands="start")
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет! Выберите способ покупки авто:", reply_markup=start_kb)

@dp.message_handler(lambda message: message.text in start_buttons)
async def handle_lead_type(message: types.Message):
    user_data[message.from_user.id]["lead_type"] = message.text
    if message.text == "Купить в лизинг":
        await message.answer("Введите название юр. лица (ИП или ООО):")
    else:
        await message.answer("Введите вашу марку авто:")

@dp.message_handler(lambda message: "юр. лица" in message.text)
async def handle_legal(message: types.Message):
    user_data[message.from_user.id]["legal_type"] = message.text
    await message.answer("Введите ИНН:")

@dp.message_handler(lambda message: message.text.isdigit() and len(message.text) == 10)
async def handle_inn(message: types.Message):
    user_data[message.from_user.id]["inn"] = message.text
    await message.answer("Введите email:")

@dp.message_handler(lambda message: "@" in message.text)
async def handle_email(message: types.Message):
    user_data[message.from_user.id]["email"] = message.text
    await message.answer("Введите вашу марку авто:")

@dp.message_handler(lambda message: "авто" in message.text.lower() or message.text in user_data)
async def handle_brand(message: types.Message):
    user_data[message.from_user.id]["car_brand"] = message.text
    await message.answer("Выберите бюджет:", reply_markup=budget_kb)

@dp.message_handler(lambda message: message.text in ["1–2 млн", "2–4 млн", "4–6 млн", "6–10 млн", ">10 млн"])
async def handle_budget(message: types.Message):
    user_data[message.from_user.id]["budget"] = message.text
    await message.answer("Укажите ваш город:")

@dp.message_handler(lambda message: "город" in message.text.lower() or len(message.text) > 3)
async def handle_city(message: types.Message):
    user_data[message.from_user.id]["city"] = message.text
    await message.answer("Введите ваше имя:")

@dp.message_handler(lambda message: len(message.text.split()) == 1)
async def handle_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    await message.answer("Введите номер телефона:")

@dp.message_handler(lambda message: "+" in message.text or message.text.isdigit())
async def handle_phone(message: types.Message):
    user_data[message.from_user.id]["phone"] = message.text
    await message.answer("Хотите добавить комментарий или удобное время для звонка? Напишите или введите '-' для пропуска:")

@dp.message_handler()
async def handle_comment(message: types.Message):
    user_data[message.from_user.id]["comment"] = message.text
    write_to_gsheet(user_data[message.from_user.id])
    await message.answer("Спасибо! Ваша заявка принята. Мы свяжемся с вами.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
