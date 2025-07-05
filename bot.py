import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
from gsheets import write_to_gsheet
import asyncio

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

user_data = {}

@dp.message(commands=["start"])
async def start(message: Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="Купить в кредит")
    kb.button(text="Купить за наличные")
    kb.button(text="Купить в лизинг")
    await message.answer("Привет! Выберите способ покупки:", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message()
async def handle_step(message: Message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        user_data[chat_id] = {}

    if text in ["Купить в кредит", "Купить за наличные", "Купить в лизинг"]:
        user_data[chat_id]["method"] = text

        if text == "Купить в лизинг":
            await message.answer("Укажите форму юр. лица (ИП или ООО):")
        else:
            await message.answer("Введите марку автомобиля:")

    elif "method" in user_data[chat_id] and user_data[chat_id]["method"] == "Купить в лизинг":
        if "entity" not in user_data[chat_id]:
            user_data[chat_id]["entity"] = text
            await message.answer("Введите ИНН:")
        elif "inn" not in user_data[chat_id]:
            user_data[chat_id]["inn"] = text
            await message.answer("Введите email:")
        elif "email" not in user_data[chat_id]:
            user_data[chat_id]["email"] = text
            await message.answer("Введите бюджет (например, 1-2 млн, 2-4 млн и т.д.):")
        elif "budget" not in user_data[chat_id]:
            user_data[chat_id]["budget"] = text
            await message.answer("Укажите город:")
        elif "city" not in user_data[chat_id]:
            user_data[chat_id]["city"] = text
            await message.answer("Добавьте комментарий или удобное время для звонка:")
        elif "comment" not in user_data[chat_id]:
            user_data[chat_id]["comment"] = text
            await finalize(message)

    else:
        if "brand" not in user_data[chat_id]:
            user_data[chat_id]["brand"] = text
            await message.answer("Укажите бюджет (например, 1-2 млн, 2-4 млн и т.д.):")
        elif "budget" not in user_data[chat_id]:
            user_data[chat_id]["budget"] = text
            await message.answer("Укажите город:")
        elif "city" not in user_data[chat_id]:
            user_data[chat_id]["city"] = text
            await message.answer("Оставьте номер телефона или контакт:")
        elif "contact" not in user_data[chat_id]:
            user_data[chat_id]["contact"] = text
            await message.answer("Добавьте комментарий или удобное время для звонка:")
        elif "comment" not in user_data[chat_id]:
            user_data[chat_id]["comment"] = text
            await finalize(message)

async def finalize(message: Message):
    chat_id = message.chat.id
    data = user_data.get(chat_id, {})
    await write_to_gsheet(data)
    await message.answer("Спасибо! Данные записаны. Менеджер скоро с вами свяжется.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
