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
from parser import make_document, get_last_twenty, make_document_for_line, get_for_current_line
from month import MonthReport
from markup import Keyboard
from dataclasses import dataclass
from aiogram.types import InputFile

@dataclass
class Values:
    last_twenty_values:list
    max_len:int

class StateBot(StatesGroup):
    get_number = State()
    get_month = State()

bot = Bot(token='5741636953:AAHhRXNgcUK7sF-ENdQephPo9TJVI2c8Z5Q', parse_mode="HTML")
dp = Dispatcher(bot,storage=MemoryStorage())
database = Database()
scheduler = AsyncIOScheduler()
keyboard = Keyboard()


@dp.message_handler(commands = ['start'],state=None)
async def start(message: types.Message):
    await message.answer('Бот запущен.',reply_markup = keyboard.main_buttons())
    database.create_user(message.from_user.id, message.from_user.username)


@dp.message_handler(state=StateBot.get_number)
async def get_number(message: types.Message,state: FSMContext):
    if str(message.text).isnumeric():
        line = get_for_current_line(int(message.text)-2)
        await send_document_for_line(message.from_user.id,line)
    else:
        await message.answer('Вы отправили некорректный номер.')
    await state.finish()


@dp.message_handler(state=StateBot.get_month)
async def get_month(message: types.Message,state: FSMContext):
    if str(message.text).isnumeric():
        month_number = str(message.text)
        doc_name = MonthReport(month_number).write()
        await bot.send_document(message.from_user.id, InputFile(doc_name, filename=doc_name))
        os.remove(doc_name)
    await state.finish()


@dp.message_handler(Text(equals='Сформировать по номеру'))
async def make_order_for_number(message: types.Message, state: FSMContext):
    await message.answer('Отправьте номер строки из таблицы',reply_markup=keyboard.main_buttons())
    await StateBot.get_number.set()


@dp.message_handler(Text(equals='Создать приказ'))
async def make_order(message: types.Message, state: FSMContext):
    Values.last_twenty_values, Values.max_len = get_last_twenty()
    await message.answer('Выберите данные для создания документа',reply_markup=keyboard.inline_get_order_kb(Values.last_twenty_values,Values.max_len+2))
    

@dp.message_handler(Text(equals='Месячный отчет'))
async def make_month_stat(message: types.Message, state: FSMContext):
    await message.answer('Отправьте номер месяца',reply_markup=keyboard.main_buttons())
    await StateBot.get_month.set()
    

@dp.callback_query_handler(text_contains="valueline_")
async def add_question(call: types.CallbackQuery):
    values_id = int(call.data.split('_')[1])  
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await send_document_for_line(call.from_user.id,Values.last_twenty_values[values_id])


@dp.message_handler(content_types=['text'],state=None)
async def not_response(message: types.Message, state:FSMContext):
    await message.answer('Я вас не понимаю.',reply_markup = keyboard.main_buttons())


async def send_document_for_line(user_id, line_values):
    doc_name = make_document_for_line(line_values)
    await bot.send_document(user_id,InputFile(doc_name, filename=doc_name))
    os.remove(doc_name)


async def send_document():
    doc_name = make_document()
    print(doc_name, datetime.now())
    if not doc_name: return
    users = database.get_user_list()
    print(users)
    for id in users:
        try:
            await bot.send_document(id[0], InputFile(doc_name, filename=doc_name))
        except Exception as ex:
            print(ex)
    os.remove(doc_name)     


if __name__ == '__main__':
    scheduler.add_job(send_document,"interval",minutes=5)
    # scheduler.add_job(send_document,"interval",seconds=5)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)