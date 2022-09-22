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
from parser import make_document, get_last_twenty, make_document_for_line
from markup import Keyboard
from dataclasses import dataclass

@dataclass
class Values:
    last_twenty_values:list
    max_len:int

bot = Bot(token='5446413703:AAEXTpTWUKYUDDxzJQPUSW8qVp2zTgaD76Q', parse_mode="HTML")
dp = Dispatcher(bot,storage=MemoryStorage())
database = Database()
scheduler = AsyncIOScheduler()
keyboard = Keyboard()


@dp.message_handler(commands = ['start'],state=None)
async def start(message: types.Message):
    await message.answer('Бот запущен.',reply_markup = keyboard.main_buttons())
    database.create_user(message.from_user.id, message.from_user.username)


@dp.message_handler(Text(equals='Создать приказ'))
async def make_order(message: types.Message, state: FSMContext):
    Values.last_twenty_values, Values.max_len= get_last_twenty()
    await message.answer('Выберите данные для создания документа',reply_markup=keyboard.inline_get_order_kb(Values.last_twenty_values,Values.max_len+2))
    

@dp.callback_query_handler(text_contains="valueline_")
async def add_question(call: types.CallbackQuery):
    # await bot.answer_callback_query(
    #         call.id,
    #         text='Нажата кнопка с номером 5.\nА этот текст может быть длиной до 200 символов 😉', show_alert=True)

    values_id = int(call.data.split('_')[1])  
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await send_document_for_line(call.from_user.id,Values.last_twenty_values[values_id])

@dp.message_handler(content_types=['text'],state=None)
async def not_response(message: types.Message, state:FSMContext):
    await message.answer('Я вас не понимаю.',reply_markup = keyboard.main_buttons())

async def send_document_for_line(user_id, line_values):
    doc_name = make_document_for_line(line_values)
    await bot.send_document(user_id,open(doc_name,'rb'))
    os.remove(doc_name)

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
    # scheduler.add_job(send_document,"interval",seconds=5)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)