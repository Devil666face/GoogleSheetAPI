
from pathlib import Path
from aiogram import Bot,Dispatcher,types,executor
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from database import Database


bot = Bot(token='', parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)
database = Database()

@dp.message_handler(commands = ['start'],state=None)
async def start(message: types.Message):
    await message.answer('Бот запущен')
    database.create_user(message.from_user.id, message.from_user.username)

