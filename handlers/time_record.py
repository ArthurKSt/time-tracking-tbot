
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from creators.c_bot_create import bot

from decorators.d_callback_live_decorator import check_live_callback
from decorators.d_perm_decorator import check_permission

from constants.config import GTM
from constants.messages import MESSAGES
from constants.re_messages import MESSAGES as rm

from h_functions.workers_func import undo_placeTimerPointer
from h_functions.tools import getStringedTime




@check_permission("Btn_message_DayRecord")
async def cmd_timeRecord(pack, message: types.Message):

    await message.delete()

    user = pack[0] #User
    actions = user.getStatusSetterKeys() #[ ["cause", "pos", causemod],[...],... ]
    print(actions)
    message = MESSAGES["Answer_timeRecord"]
    keyboard = inline_recordAction(actions)

    await bot.send_message( chat_id=user.getId(), text=message, reply_markup=keyboard )  


#Делаем инлайн клавиатуру для выбора даты из предложенных
def inline_recordAction(actions):
    """[ ["cause", "pos", causemod],[...],... ] \n
    callback = recordAction cause, pos, causemod """

    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    if not actions:
        return keyboard_markup

    text = {
        "work"+"s": MESSAGES["Btn_message_startWork"],
        "work"+"e": MESSAGES["Btn_message_endWork"],
        
        "free"+"s": MESSAGES["Btn_message_startBreak"],
        "free"+"e": MESSAGES["Btn_message_endWBreak"],
    }


    callbackData = "recordAction:"

    for action in actions:
        mod = f"{action[0]}:{action[1]}:{action[2]}"

        btn = types.InlineKeyboardButton( text=text[action[0] + action[1]], callback_data=callbackData+mod )
        keyboard_markup.add( btn )
    
    keyboard_markup.add( types.InlineKeyboardButton(MESSAGES['Btn_message_info_t'], callback_data="BtnInl_DayInfo") )
    keyboard_markup.add( types.InlineKeyboardButton(rm['Btn_message_cancel'], callback_data=callbackData+"cancel") )

    return keyboard_markup


@check_permission("Btn_message_DayRecord")
@check_live_callback(True)
async def recordAction_callback_handler(pack, query: types.CallbackQuery):

    user = pack[0]
    # user = User
    #in ChooseuTimePoint:таблица:  ид записи  или отмена(закрывает выобор даты)

    #Проверяем, доступна ли еще эта кнопка.
    timeNow = int(query.message.date.timestamp())+GTM 
    # if ( scheduled.getTime() - timeNow ) > CALLBACKLIVE_TIME:
    #     # Если кнопка не нажималась слишком долго

    #     await query.answer(MESSAGES['Answer_oldButton'])
    #     await query.message.delete()

    if query.data == "recordAction:cancel":


        await query.answer(MESSAGES['Answer_success_canceled'])
        await query.message.delete()


    else:
        answer_data, cause, pos, causemod = query.data.split(":")

        text = {
        "work"+"s": MESSAGES["Answer_startWork"],
        "work"+"e": MESSAGES["Answer_stopWork"],
        
        "free"+"s": MESSAGES["Answer_startBreak"],
        "free"+"e": MESSAGES["Answer_stopBreak"],
        }

        current_text = text[cause+pos].format( getStringedTime(timeNow) )

        print( timeNow, cause, pos, causemod )
        # user = User
        post_id = user.setTimerPoint( timeNow, cause, pos, causemod )

        await query.answer(MESSAGES['Answer_success'])
        await query.message.delete()

        keyboard = inline_afterRecordAction(cause, pos, post_id)

        await bot.send_message(chat_id=user.getId(), text=current_text, reply_markup=keyboard)



def inline_afterRecordAction(cause, dir, post_id):
    """ cause - причина создания таймера\n
    dir - его нравление (s-start, e-end)\n
    post_id получается при создании времени """

    print(post_id)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3) #Отменить действие, закрыть меню
    # 'BtnInl_message_cancel': Случайно нажал
    # 'BtnInl_message_chooseAnother': исправить. выбрать из прошлых..

    # mod = ":"+cause #По нему можно отделять, для какой таблицы сработало событие
    mod = f":{cause}:{dir}:{post_id}"

    text_and_data = (
        (rm['Btn_message_cancel_t'], 'BtnInl_undoRecordAction'+mod),
        # (MESSAGES['Btn_message_info_t'], 'BtnInl_DayInfo'),
        (rm['Btn_message_close_t'], 'BtnInl_close'),
    ) #По тексту выводится кнопка, по данным слушает слушатель

    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.row(*row_btns)

    return keyboard_markup


def inline_close_menu():
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    text = rm['Btn_message_close_t']
    key = types.InlineKeyboardButton(text, callback_data="BtnInl_close")
    keyboard_markup.add(key)
    return keyboard_markup


@check_permission("Btn_message_DayRecord")
@check_live_callback(True)
async def dayInfo_callback_handler(pack, query: types.CallbackQuery):
    """слушатель инлайн клавиатуры, которая срабатывает при отмене нажатия или смены даты"""

    await query.answer(MESSAGES['Answer_success'])
    await query.message.delete()
    """
    Выводит сообщение с информации о текущем дне.
    Когда начал работать, когда брал перерывы

    Вы работали:
        С .. до ..
        С .. до ..

    Вы брали перерывы:
        С .. до ..
        С .. до ..

    Ваше имя в базе:
    Вы сегодня работали: 

    [Закрыть меню]
    """

    user = pack[0]

    strInfo = user.getDayInfo()

    await bot.send_message(chat_id=user.getId(), text=strInfo, reply_markup=inline_close_menu() )



@check_live_callback(True)
async def closeMenu_callback_handler(query: types.CallbackQuery):

    await query.answer(MESSAGES['Answer_closed'])
    await query.message.delete()



@check_live_callback(True)
async def undoRecordAction_callback_handler(query: types.CallbackQuery):
    print( query.data)
    answer_data, cause, dir, post_id = query.data.split(":") 

    status = undo_placeTimerPointer(post_id)

    if status: # Если получилось
        await query.answer(MESSAGES['Answer_undo_done'], show_alert=True) 
    else:
        await query.answer(MESSAGES['Answer_undo_error'], show_alert=True) 
    
    await query.message.delete()
    return





def register_handlers_time_record(dp: Dispatcher):
    dp.register_message_handler(cmd_timeRecord, Text(equals=rm["Btn_message_DayRecord"], ignore_case=True) )

    dp.register_callback_query_handler(recordAction_callback_handler, text_contains='recordAction:' )

    dp.register_callback_query_handler(closeMenu_callback_handler, text_contains='BtnInl_close' )
    dp.register_callback_query_handler(dayInfo_callback_handler, text_contains='BtnInl_DayInfo' )
    dp.register_callback_query_handler(undoRecordAction_callback_handler, text_contains='BtnInl_undoRecordAction' )