import os
from pydoc import doc
from sched import scheduler
from aiogram import Bot,Dispatcher,types,executor
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import Database
from datetime import datetime
from parser import make_document


bot = Bot(token='5446413703:AAEXTpTWUKYUDDxzJQPUSW8qVp2zTgaD76Q', parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot,storage=storage)
database = Database()
scheduler = AsyncIOScheduler()


@dp.message_handler(commands = ['start'],state=None)
async def start(message: types.Message):
    await message.answer('Бот запущен')
    database.create_user(message.from_user.id, message.from_user.username)


async def send_document():
    doc_name = make_document()
    print(doc_name, datetime.now())
    if not doc_name: return
    users = database.get_user_list()
    print(users)
    for id in users:
        try:
            await bot.send_document(id[0], open(doc_name,'rb'))
        except Exception as ex:
            print(ex)
    os.remove(doc_name)     


if __name__ == '__main__':
    scheduler.add_job(send_document,"interval",minutes=5)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)