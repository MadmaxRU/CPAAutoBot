
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать!")
    await message.answer("Давайте подберем авто. Как вас зовут?")
    await LeadForm.name.set()

# Обработка имени
@dp.message_handler(state=LeadForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📱 Введите ваш номер телефона:")
    await LeadForm.phone.set()

# Обработка телефона
@dp.message_handler(state=LeadForm.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("🏙️ Укажите ваш город:")
    await LeadForm.city.set()

# Обработка города
@dp.message_handler(state=LeadForm.city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("🚗 Какая марка автомобиля вас интересует?")
    await LeadForm.car_brand.set()

# Обработка марки авто
@dp.message_handler(state=LeadForm.car_brand)
async def get_car_brand(message: types.Message, state: FSMContext):
    await state.update_data(car_brand=message.text)
    await message.answer("💳 Какой способ оплаты вас интересует? (наличные, кредит, лизинг)")
    await LeadForm.payment_method.set()

# Обработка способа оплаты
@dp.message_handler(state=LeadForm.payment_method)
async def get_payment_method(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await message.answer("🌍 Рассматриваете авто под заказ из-за границы? (да/нет)")
    await LeadForm.from_abroad.set()

# Обработка из-за границы
@dp.message_handler(state=LeadForm.from_abroad)
async def get_from_abroad(message: types.Message, state: FSMContext):
    await state.update_data(from_abroad=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("✅ Согласен", "❌ Не согласен")
    await message.answer("Вы соглашаетесь с условиями обработки персональных данных?", reply_markup=keyboard)
    await LeadForm.agreement.set()

# Обработка согласия
@dp.message_handler(state=LeadForm.agreement)
async def get_agreement(message: types.Message, state: FSMContext):
    if message.text == "✅ Согласен":
        data = await state.get_data()
        # Здесь должна быть логика сохранения в Google Sheets или БД
        await message.answer("🎉 Спасибо! Мы свяжемся с вами в ближайшее время.", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("❗ Без согласия мы не можем продолжить.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

# Запуск бота
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
