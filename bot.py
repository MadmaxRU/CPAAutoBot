from aiogram import Bot, Dispatcher, types, executor
import os
from gsheets import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Напиши своё имя.")

@dp.message_handler()
async def handle_text(message: types.Message):
    data = {
        "lead_type": "test",
        "city": "Москва",
        "car_brand": "Toyota",
        "payment_method": "Кредит",
        "name": message.text,
        "phone": "+79999999999",
        "from_abroad": "Нет",
        "agreement": "Да"
    }
    write_to_gsheet(data)
    await message.answer("Данные отправлены в таблицу!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
