# from libs.aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

from handlers.functions.clock import clock_callback, DialogClock

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text

from constants.menu_messages import MESSAGES as mm
from creators.c_bot_create import bot

start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)
start_kb.row('Часы')


# starting bot when user sends `/start` command, answering with inline calendar
# @dp.message_handler(commands=['start'])

async def cmd_start_calendar(query: CallbackQuery):
    chat_id = query.from_user.id
    await bot.send_message(chat_id, 'Введите "Часы" ', reply_markup=start_kb)
    await query.answer("Тест запущен")


# # # /@dp.message_handler(Text(equals=['Navigation Calendar'], ignore_case=True))
# async def nav_cal_handler(message: Message):
#     await message.answer("Please select a date: ", reply_markup=await SimpleCalendar().start_calendar())


# simple calendar usage
# @dp.callback_query_handler(simple_cal_callback.filter())
# async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
#     selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
#     if selected:
#         await callback_query.message.answer(
#             f'You selected {date.strftime("%d/%m/%Y")}',
#             reply_markup=start_kb
#         )


# @dp.message_handler(Text(equals=['Dialog Calendar'], ignore_case=True))
async def simple_cal_handler(message: Message):
    await message.answer("Пожалуйста, выберете время: ", reply_markup=await DialogClock().start_clock())


# dialog calendar usage
# @dp.callback_query_handler(dialog_cal_callback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await DialogClock().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%d/%m %Yгода %Hч. %Mм. %Sс.")}',
            reply_markup=start_kb
        )


def register_handlers_test_calendar(dp: Dispatcher):
    dp.register_callback_query_handler(cmd_start_calendar, text_contains='BtnM_message_test'  )

    # dp.register_message_handler(nav_cal_handler, Text(equals=['Navigation Calendar'], ignore_case=True) )

    # dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter() )

    dp.register_message_handler(simple_cal_handler, Text(equals=['Часы'], ignore_case=True) )

    dp.register_callback_query_handler(process_dialog_calendar, clock_callback.filter())
    




    # #Вывод меню
    # dp.register_message_handler(cmd_openMenu, Text(equals=rm["Btn_message_Menu"], ignore_case=True))

    # #Вывод Показать информацию о посещениях (сейчас таблицы времени работы)
    # dp.register_callback_query_handler(BtnM_message_time_callback_handler, text_contains='BtnM_message_time' )