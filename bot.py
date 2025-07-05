
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import Router
from gsheets import write_to_gsheet

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚗 Купить авто")],
            [KeyboardButton(text="📞 Связаться с менеджером")]
        ],
        resize_keyboard=True
    )
    await message.answer("Привет! Что тебя интересует?", reply_markup=keyboard)

@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    # Пример простой логики
    if text == "🚗 Купить авто":
        await message.answer("Пожалуйста, введите марку автомобиля:")
    elif text == "📞 Связаться с менеджером":
        await message.answer("Менеджер скоро с вами свяжется.")
    else:
        await message.answer("Спасибо! Ваши данные записаны.")
        write_to_gsheet([user_id, text])

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
