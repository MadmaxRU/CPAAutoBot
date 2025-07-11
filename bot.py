import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from gsheet import write_to_gsheet

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage(), parse_mode=ParseMode.HTML)

class Form(StatesGroup):
    deal_type = State()
    car_brand = State()
    budget = State()
    contact = State()
    comment = State()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Купить в кредит")],
        [KeyboardButton(text="Купить за наличные")],
        [KeyboardButton(text="Купить в лизинг")],
        [KeyboardButton(text="Купить в трейд-ин")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@dp.message(F.text.lower().in_(["/start", "начать", "подобрать авто"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите способ покупки:", reply_markup=main_kb)
    await state.set_state(Form.deal_type)

@dp.message(Form.deal_type)
async def process_deal_type(message: Message, state: FSMContext):
    await state.update_data(deal_type=message.text)
    await message.answer("Введите марку автомобиля:")
    await state.set_state(Form.car_brand)

@dp.message(Form.car_brand)
async def process_brand(message: Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("Укажите бюджет:")
    await state.set_state(Form.budget)

@dp.message(Form.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить телефон", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Оставьте ваш номер телефона:", reply_markup=contact_kb)
    await state.set_state(Form.contact)

@dp.message(Form.contact)
@dp.message(F.contact)
async def process_contact(message: Message, state: FSMContext):
    contact = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=contact)
    await message.answer("Добавьте комментарий или удобное время для звонка:")
    await state.set_state(Form.comment)

@dp.message(Form.comment)
async def process_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    write_to_gsheet(data)
    await message.answer("Спасибо! Наш специалист скоро с вами свяжется.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
