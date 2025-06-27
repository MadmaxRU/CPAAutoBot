import logging
from aiogram import Bot, Dispatcher, executor, types
from gsheets import write_to_sheet
import os

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь марку автомобиля для заявки.")

@dp.message_handler()
async def handle_message(message: types.Message):
    user_data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "text": message.text
    }
    write_to_sheet(user_data)
    await message.reply("✅ Заявка принята! Мы с вами свяжемся.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
