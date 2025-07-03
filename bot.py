import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from gsheets import write_to_gsheet

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Определение состояний
class LeadForm(StatesGroup):
    name = State()
    phone = State()
    city = State()
    car_brand = State()
    payment_method = State()
    from_abroad = State()
    agreement = State()

# Обработка команды /start
@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать!")
    await message.answer("Давайте подберем авто. Как вас зовут?")
    await LeadForm.name.set()

@dp.message_handler(state=LeadForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш номер телефона:")
    await LeadForm.phone.set()

@dp.message_handler(state=LeadForm.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙️ В каком вы городе?")
    await LeadForm.city.set()

@dp.message_handler(state=LeadForm.city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("🚗 Укажите марку интересующего авто:")
    await LeadForm.car_brand.set()

@dp.message_handler(state=LeadForm.car_brand)
async def get_car_brand(message: types.Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("💳 Какой способ оплаты? (кредит / наличные / лизинг)")
    await LeadForm.payment_method.set()

@dp.message_handler(state=LeadForm.payment_method)
async def get_payment_method(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await message.answer("🌍 Интересует авто из-за границы? (да / нет)")
    await LeadForm.from_abroad.set()

@dp.message_handler(state=LeadForm.from_abroad)
async def get_from_abroad(message: types.Message, state: FSMContext):
    await state.update_data(from_abroad=message.text)
    await message.answer("✅ Готовы ли вы к звонку от нашего менеджера? (да / нет)")
    await LeadForm.agreement.set()

@dp.message_handler(state=LeadForm.agreement)
async def get_agreement(message: types.Message, state: FSMContext):
    await state.update_data(agreement=message.text)
    data = await state.get_data()
    data["lead_type"] = message.from_user.id
    write_to_gsheet(data)
    await message.answer("🎉 Спасибо! Мы скоро с вами свяжемся.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
