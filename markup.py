from aiogram import types
from aiogram.types import ReplyKeyboardRemove,ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.types.message import ContentTypes
from aiogram.types.message import ContentType

class Keyboard:
    def main_buttons(self):
        main_buttons = ['Создать приказ','Сформировать по номеру','Месячный отчет']
        keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_main.add(*main_buttons)
        return keyboard_main

    def inline_get_order_kb(self, last_twenty_values, max_value):
        inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
        # print(last_twenty_values)
        for index,line in enumerate(last_twenty_values):
            inline_keyboard.add(types.InlineKeyboardButton(text=f'{max_value-(20-index)}|{line[0]}\n{line[2]}\n{line[3]}\n{line[4]}'.replace('школа','ш.'),callback_data=f'valueline_{index}'))

        return inline_keyboard