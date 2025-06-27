from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = Bot(token="ВАШ_ТОКЕН")
dp = Dispatcher(bot, storage=MemoryStorage())

class LeadForm(StatesGroup):
    brand = State()
    model = State()
    year = State()
    phone = State()

@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Привет! 🚗 Какая марка автомобиля вас интересует?")
    await LeadForm.brand.set()

@dp.message_handler(state=LeadForm.brand)
async def ask_model(message: types.Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Отлично! Какая модель?")
    await LeadForm.model.set()

@dp.message_handler(state=LeadForm.model)
async def ask_year(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Какой год выпуска?")
    await LeadForm.year.set()

@dp.message_handler(state=LeadForm.year)
async def ask_phone(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer("Оставьте номер телефона для связи:")
    await LeadForm.phone.set()

@dp.message_handler(state=LeadForm.phone)
async def finish(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    
    # Тут можно отправить в Google Sheets, CRM и т.д.
    await message.answer("Спасибо! Наш менеджер свяжется с вами.")
    await state.finish()
