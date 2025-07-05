
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # Убедись, что токен в переменной окружения

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Простейшее хранилище состояний
user_state = {}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_state[message.from_user.id] = {"step": "contact"}
    await message.answer("Введите ваш контакт (имя, телефон или email):")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    state = user_state.get(user_id, {"step": "contact"})

    if state["step"] == "contact":
        state["contact"] = text
        state["step"] = "budget"

        # Кнопки с бюджетами
        budget_keyboard = InlineKeyboardMarkup(row_width=2)
        budget_keyboard.add(
            InlineKeyboardButton("1-2 млн", callback_data="budget_1_2"),
            InlineKeyboardButton("2-4 млн", callback_data="budget_2_4"),
            InlineKeyboardButton("4-6 млн", callback_data="budget_4_6"),
            InlineKeyboardButton("6-10 млн", callback_data="budget_6_10"),
            InlineKeyboardButton(">10 млн", callback_data="budget_10_plus")
        )

        await message.answer("Укажите бюджет:", reply_markup=budget_keyboard)
        user_state[user_id] = state

    elif state["step"] == "city":
        state["city"] = text
        await message.answer("Спасибо! Мы свяжемся с вами после подбора авто.")
        user_state[user_id] = {"step": "contact"}  # сброс состояния


@dp.callback_query_handler(lambda c: c.data.startswith("budget_"))
async def handle_budget(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    budget = callback_query.data.replace("budget_", "").replace("_", "-") + " млн"

    state = user_state.get(user_id, {})
    state["budget"] = budget
    state["step"] = "city"
    user_state[user_id] = state

    await bot.send_message(user_id, "Укажите город:")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
