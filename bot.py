
import logging
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from gsheets import write_to_gsheet

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_data = {}

start_kb = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text="Купить в кредит"),
        KeyboardButton(text="Купить за наличные"),
        KeyboardButton(text="Купить в лизинг"),
        KeyboardButton(text="Купить в трейд-ин")
    ]],
    resize_keyboard=True
)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Выберите способ покупки автомобиля:", reply_markup=start_kb)


@router.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_data:
        user_data[user_id] = {"step": "purchase_type"}

    state = user_data[user_id]

    if state["step"] == "purchase_type":
        state["purchase_type"] = text
        state["step"] = "brand"
        await message.answer("Введите марку автомобиля:", reply_markup=ReplyKeyboardRemove())
    elif state["step"] == "brand":
        state["brand"] = text
        if state["purchase_type"] == "Купить в лизинг":
            state["step"] = "entity_type"
            await message.answer("Введите форму юрлица (ИП или ООО):")
        else:
            state["step"] = "contact"
            await message.answer("Введите ваши контактные данные (номер телефона или email):", reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
                resize_keyboard=True
            ))
    elif state["step"] == "entity_type":
        state["entity_type"] = text
        state["step"] = "inn"
        await message.answer("Введите ИНН:")
    elif state["step"] == "inn":
        state["inn"] = text
        state["step"] = "email"
        await message.answer("Введите email:")
    elif state["step"] == "email":
        state["email"] = text
        state["step"] = "budget"
        await message.answer("Укажите бюджет:") 
1–2 млн
2–4 млн
4–6 млн
6–10 млн
>10 млн")
    elif state["step"] == "contact":
        state["contact"] = text
        state["step"] = "budget"
        await message.answer(
"Укажите бюджет:\n"
"1-2 млн\n"
"2-4 млн\n"
"4-6 млн\n"
"6-10 млн\n"
">10 млн"
)
    elif state["step"] == "budget":
        state["budget"] = text
        state["step"] = "city"
        await message.answer("Укажите город:")
    elif state["step"] == "city":
        state["city"] = text
        state["step"] = "comment"
        await message.answer("Можете добавить комментарий или удобное время для звонка:")
    elif state["step"] == "comment":
        state["comment"] = text

        data = user_data.pop(user_id)
        write_to_gsheet(data)

        await message.answer("Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=start_kb)


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
