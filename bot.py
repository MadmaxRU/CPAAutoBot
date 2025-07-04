import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from gsheets import write_to_gsheet

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_data = {}

car_brands = ["Toyota", "Hyundai", "BMW", "LADA", "Kia", "Volkswagen"]
years = list(range(2015, 2025))

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for brand in car_brands:
        markup.insert(KeyboardButton(brand))
    await message.answer("Выберите марку автомобиля:", reply_markup=markup)

@dp.message_handler(lambda msg: msg.text in car_brands)
async def get_brand(msg: types.Message):
    user_data[msg.from_user.id]["car_brand"] = msg.text
    markup = InlineKeyboardMarkup(row_width=4)
    for year in years:
        markup.insert(InlineKeyboardButton(str(year), callback_data=f"year_{year}"))
    await msg.answer("Выберите год выпуска:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("year_"))
async def get_year(callback: types.CallbackQuery):
    year = callback.data.split("_")[1]
    user_data[callback.from_user.id]["year"] = year
    await callback.message.answer("Введите ваш город:")
    await callback.answer()

@dp.message_handler(lambda msg: "car_brand" in user_data.get(msg.from_user.id, {}))
async def get_city(msg: types.Message):
    user_data[msg.from_user.id]["city"] = msg.text
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Кредит", callback_data="payment_credit"),
        InlineKeyboardButton("Лизинг", callback_data="payment_leasing"),
        InlineKeyboardButton("Наличные", callback_data="payment_cash")
    )
    await msg.answer("Выберите способ оплаты:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("payment_"))
async def get_payment(callback: types.CallbackQuery):
    payment = callback.data.split("_")[1]
    user_data[callback.from_user.id]["payment_method"] = payment
    await callback.message.answer("Введите ваше имя:")
    await callback.answer()

@dp.message_handler(lambda msg: "payment_method" in user_data.get(msg.from_user.id, {}))
async def get_name(msg: types.Message):
    user_data[msg.from_user.id]["name"] = msg.text
    await msg.answer("Введите ваш номер телефона:")

@dp.message_handler(lambda msg: "name" in user_data.get(msg.from_user.id, {}))
async def get_phone(msg: types.Message):
    user_data[msg.from_user.id]["phone"] = msg.text
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Да", callback_data="abroad_yes"),
        InlineKeyboardButton("Нет", callback_data="abroad_no")
    )
    await msg.answer("Рассматриваете авто из-за границы?", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("abroad_"))
async def get_abroad(callback: types.CallbackQuery):
    abroad = "Да" if callback.data.split("_")[1] == "yes" else "Нет"
    user_data[callback.from_user.id]["from_abroad"] = abroad
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Согласен", callback_data="agree_yes"))
    await callback.message.answer("Согласны ли вы на обработку персональных данных?", reply_markup=markup)
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "agree_yes")
async def final(callback: types.CallbackQuery):
    user_data[callback.from_user.id]["agreement"] = "Да"
    write_to_gsheet(user_data[callback.from_user.id])
    await callback.message.answer("Спасибо! Ваша заявка принята. Мы свяжемся с вами!")
    await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
