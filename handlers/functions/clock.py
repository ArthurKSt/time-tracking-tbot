"""
Взято с https://github.com/noXplode/aiogram_calendar
Крутая идея, спасибо автору! 
Сделал тоже самое только для часов/минут
"""

import calendar
from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types import CallbackQuery


# setting callback_data prefix and parts
clock_callback = CallbackData('dialog_clock', 'act', 'hour', 'minute' )
ignore_callback = clock_callback.new("IGNORE", -1, -1)  # for buttons with no answer


class DialogClock:

    def __init__(self,year: int = datetime.now().year,\
        month: int = datetime.now().month, day: int = datetime.now().day, \
        hour: int = datetime.now().hour, minute: int = datetime.now().minute):
        self.year = year
        self.month = month
        self.day = day
        self.hours = hour
        self.minute = minute

    async def start_clock(
        self,
        hour: int = datetime.now().hour
    ) -> InlineKeyboardMarkup:
        inline_kb = InlineKeyboardMarkup(row_width=6)
        # first row - years


        inline_kb.row(InlineKeyboardButton(
            f"Это было в..",
            callback_data=ignore_callback
        ))
        
        inline_kb.row()

        hmod = [0, 3, 6]
        hours = []
        for p in hmod:
            if p==0:
                hours.insert(0,hour)
                continue

            mnh = hour-p
            if mnh <=0: mnh=0
            elif mnh >=23: mnh=23
            hours.insert(0,mnh)

            mxh = hour+p
            if mxh <=0: mxh=0
            elif mxh >=23: mxh=23
            hours.append(mxh)

        print(hours)


        for value in hours:
            inline_kb.insert(InlineKeyboardButton(
                f"{value}ч.",
                callback_data=clock_callback.new("SET-HOUR", value, -1)
            ))

        # nav buttons
        inline_kb.add(InlineKeyboardButton(
            '<<',
            callback_data=clock_callback.new("PREV-HOUR", hour, -1)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=clock_callback.new("NEXT-HOUR", hour, -1)
        ))

        return inline_kb

    async def _get_minut_kb(self, hour: int, minute: int = datetime.now().minute
    ) -> InlineKeyboardMarkup:

        inline_kb=None

        inline_kb = InlineKeyboardMarkup(row_width=5)
        # first row with year button
        inline_kb.row()
        inline_kb.insert(InlineKeyboardButton(
            f"{hour} часов и...",
            callback_data=clock_callback.new("START", hour, -1)
        ))

        # two rows with 6 months buttons
        inline_kb.row()

        mmod = [0, 10, 20]
        minuts = []
        for p in mmod:
            mnh = minute-p
            if mnh <=0: mnh=0
            elif mnh >=55: mnh=55
            minuts.insert(0,mnh)

            mxh = minute+p
            if mxh <=0: mxh=0
            elif mxh >=55: mxh=55
            minuts.insert(-1,mxh)



        for minute in minuts:
            inline_kb.insert(InlineKeyboardButton(
                f"{minute} м.",
                callback_data=clock_callback.new("SET-MINUT", hour, minute)
            ))


        inline_kb.insert(InlineKeyboardButton(
            '<<',
            callback_data=clock_callback.new("PREV-MINUT", hour, minute)
        ))
        inline_kb.insert(InlineKeyboardButton(
            '>>',
            callback_data=clock_callback.new("NEXT-MINUT", hour, minute)
        ))
        # for month in self.months[6:12]:
        #     inline_kb.insert(InlineKeyboardButton(
        #         month,
        #         callback_data=calendar_callback.new("SET-MONTH", year, self.months.index(month) + 1, -1)
        #     ))
        return inline_kb

    # async def _get_days_kb(self, year: int, month: int):
    #     inline_kb = InlineKeyboardMarkup(row_width=7)
    #     inline_kb.row()
    #     inline_kb.insert(InlineKeyboardButton(
    #         year,
    #         callback_data=calendar_callback.new("START", year, -1, -1)
    #     ))
    #     inline_kb.insert(InlineKeyboardButton(
    #         self.months[month - 1],
    #         callback_data=calendar_callback.new("SET-YEAR", year, -1, -1)
    #     ))
    #     inline_kb.row()
    #     for day in weekDaysRu:
    #         inline_kb.insert(InlineKeyboardButton(day, callback_data=ignore_callback))

    #     month_calendar = calendar.monthcalendar(year, month)
    #     for week in month_calendar:
    #         inline_kb.row()
    #         for day in week:
    #             if(day == 0):
    #                 inline_kb.insert(InlineKeyboardButton(" ", callback_data=ignore_callback))
    #                 continue
    #             inline_kb.insert(InlineKeyboardButton(
    #                 str(day), callback_data=calendar_callback.new("SET-DAY", year, month, day)
    #             ))
    #     return inline_kb

    async def process_selection(self, query: CallbackQuery, data: CallbackData) -> tuple:
        return_data = (False, None)
        if data['act'] == "IGNORE":
            await query.answer(cache_time=60)
        
        if data['act'] == "START":
            await query.message.edit_reply_markup(await self.start_clock(int(data['hour'])))

        if data['act'] == "PREV-HOUR":
            new_hour = int(data['hour']) - 1 if int(data['hour']) > 2 else 2
            await query.message.edit_reply_markup(await self.start_clock(new_hour))
        if data['act'] == "NEXT-HOUR":
            new_hour = int(data['hour']) + 1 if int(data['hour']) < 22 else 22
            await query.message.edit_reply_markup(await self.start_clock(new_hour))

        if data['act'] == "SET-HOUR":
            await query.message.edit_reply_markup(await self._get_minut_kb(int(data['hour'])))

        if data['act'] == "PREV-MINUT":
            new_minute = int(data['minute']) - 10 if int(data['minute']) > 10 else 10
            await query.message.edit_reply_markup(await self._get_minut_kb(int(data['hour']), new_minute))
        if data['act'] == "NEXT-MINUT":
            new_minute = int(data['minute']) + 10 if int(data['minute']) < 50 else 50
            await query.message.edit_reply_markup(await self._get_minut_kb(int(data['hour']), new_minute))
        
        if data['act'] == "SET-MINUT":
            await query.message.delete_reply_markup()
            return_data = True, datetime( self.year, self.month, self.day, int(data['hour']), int(data['minute']) )

            # await query.message.edit_reply_markup(await self._get_days_kb(int(data['hour']), int(data['minute'])))


        # if data['act'] == "SET-DAY":
        #     await query.message.delete_reply_markup()   # removing inline keyboard
        #     return_data = True, datetime(int(data['year']), int(data['month']), int(data['day']))
        return return_data
