from creators.c_bot_create import bot#, company
from creators.c_company_create import company
from creators.c_logger_create import logger

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from constants.config import GTM

from constants.messages import MESSAGES
from constants.re_messages import MESSAGES as rm

from handlers.fsmachine import FSMChangeStartTime

from decorators.d_perm_decorator import check_permission


#Инлайн клавиатура для вывода Информации по пользователям
def inline_downloadInfo(permission):

    keyboard_markup = types.InlineKeyboardMarkup()

    key = types.InlineKeyboardButton(text="Скачать данные за ближ.время", callback_data="BtnInl_Download:"+str(permission) )
    keyboard_markup.insert( key )

    return keyboard_markup



@check_permission("Btn_message_info")
async def cmd_info(user, message: types.Message):
    """ Выводит статистику по дню"""


    workTime = user.getWorkedTime_s()
    if not workTime: workTime = "Нет информации"
    else: workTime = workTime.replace(":","ч. ")+"м."

    # startIn = user.getWorkStartTime_s()
    startIn = user.getStartTime_s()
    if not startIn: startIn = "Нет информации"

    # endIn = user.getWorkEndTime_s()
    endIn = user.getEndTime_s()
    if not endIn: endIn = "Нет информации"

    answer = MESSAGES['Answer_info'].format(
        user.getName(),
        startIn,
        endIn,
        workTime
    )

    keyb = inline_downloadInfo( user.getPermission() )

    await bot.send_message(user.getId(), answer, reply_markup=keyb)      


# WORK_START   Btn_message_startWork



@check_permission("Btn_message_startWork")
async def cmd_startWork(user, message: types.Message):

    # user.setWorkTime_byTable(int(message.date.timestamp()), "come") # Получает из Даты ЮниксДату и обрезает ее до инт
    post_id = user.startWork(int(message.date.timestamp())+GTM) # Получает из Даты ЮниксДату и обрезает ее до инт

    # Это лучше сделать здесь, потому что иначе придется отдельную библиотеку подключать в классах пользователя,бд и прочих
    # user = User()
    await bot.send_message(user.getId(), MESSAGES['Answer_startWork'].format(user.getLastPressedStartTime_s()), \
        reply_markup=inline_cancel_or_choose("work", "s", post_id ) )#, user.getuTimePointByTableName("come").getTimeId()))
        #Передаем в инлайн клавиатуру таблицу и ид записи в таблице
    #Тут нужно еще сообщене у которого есть инлайн клавиатура "Отменить ввод, выбрать из списка"  

from Classes.User import User




#Делаем инлайн клавиатуру для выбора даты из предложенных
def inline_choose_time_point(table, time_dict):
    """table = leave/come , time_dict - dict from User.getPrevWorkTime_byTable \n
    callback = ChooseuTimePoint : table : post_id or cancel"""

    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    if not time_dict:
        ##print("Проверить. Пустая клавиатура. ")
        return keyboard_markup


    callbackData = "ChooseuTimePoint:"
    callbackData += str(table)+":" #По нему можно отделять, для какой таблицы сработало событие
                                    #В итоге выхлдит ChooseuTimePoint:таблица:ид записи

    for id_post in time_dict.keys(): # 0 - data 1 - time
        # text = ( time_dict[id_post][0], time_dict[id_post][1] )
        text = f" {time_dict[id_post][0]} > {time_dict[id_post][1]} "
        
        row_btn = types.InlineKeyboardButton(text, callback_data=callbackData+str(id_post)  )
        keyboard_markup.insert( row_btn )
    
    keyboard_markup.add( types.InlineKeyboardButton(rm['Btn_message_cancel'], callback_data=callbackData+"cancel") )


    return keyboard_markup



    #Делаем слушатель клавиатуры
@check_permission("")
async def inline_choose_time_point_callback_handler(user, query: types.CallbackQuery):
    #in ChooseuTimePoint:таблица:  ид записи  или отмена(закрывает выобор даты)

    answer_data, table, post_id = query.data.split(":")

    if answer_data == 'ChooseuTimePoint': # Если событие
        
        if post_id!='cancel': #Если в пост айди = айди
            # user=User()
            user.setuTimePoint_byTable(post_id, table) #Из списка на сегодня выбирается дата и устанавливается

            ##print(int(post_id))
            msid = query.message.message_id
            newText = f"Вы выбрали время из списка: {User.s_getTime_s(int(post_id),table)}"

            

            # await bot.delete_message(user.getId(), msid)
            await bot.edit_message_text(chat_id=user.getId(), message_id=msid, text=newText, reply_markup=None)
            # await cmd_info(user, query.message)
        
        else:
            #cancel
            pass




#Делаем инлайн клавиатуру для ответа на сообщение создания временной метки
def inline_cancel_or_choose(cause, dir, post_id):
    """ cause - причина создания таймера\n
    dir - его нравление (s-start, e-end)\n
    post_id получается при создании времени """

    #print(post_id)
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    # 'BtnInl_message_cancel': Случайно нажал
    # 'BtnInl_message_chooseAnother': исправить. выбрать из прошлых..

    # mod = ":"+cause #По нему можно отделять, для какой таблицы сработало событие
    mod = f":{cause}:{dir}:{post_id}"

    text_and_data = (
        (MESSAGES['BtnInl_message_cancel'], 'BtnInl_message_cancel'+mod),
        (MESSAGES['BtnInl_message_chooseAnother'], 'BtnInl_message_chooseAnother'+mod),
    ) #По тексту выводится кнопка, по данным слушает слушатель


    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.row(*row_btns)

    return keyboard_markup


#Делаем слушатель клавиатуры
# @check_permission("")
# async def cancel_or_choose_callback_handler(user, query: types.CallbackQuery):
#     """слушатель инлайн клавиатуры, которая срабатывает при отмене нажатия или смены даты"""

#     #print(query.data)
#     answer_data, cause, dir, post_id = query.data.split(":") 

#     if answer_data == 'BtnInl_message_cancel': # Если событие сработала на отмену нажатия Начал/закончил - отмена

#         status = undo_placeTimerPointer(post_id)

#         if status: # Если получилось
#             await query.answer(MESSAGES['Answer_undo_done'], show_alert=True) 
#         else:
#             await query.answer(MESSAGES['Answer_undo_error'], show_alert=True) 
#         await query.message.edit_text("Отменено.", reply_markup=None)
#         return


#     elif answer_data == 'BtnInl_message_chooseAnother': # Если событие сработала на смену нажатия Начал/закончил - выбрать из списка..


#         # time_dict = user.getPrevWorkTime_byTable(current_date_list, table)
#         time_dict = user.getPrevuTimePoints_byTable(table)
#         # time_dict = user.choosePrevStartWork(current_date_list) # post_id = [дата, время]

#         if not time_dict: # Если словарь пуст
            
#             await query.answer( "Не нашлось записей на сегодня" , show_alert=True)
#             return

#         #Загрузить сообщение из MESSAGES
#         kb = inline_choose_time_point(table, time_dict)

        
#         # await bot.send_message(user.getId(), "Время, на которое можно откатиться: ", reply_markup=kb)
#         await query.message.edit_text("Время, на которое можно откатиться:", reply_markup=kb)


#         await query.answer("Вот записи на сегодня")

#         #
#         return
#         #ставим машину состояний, выбираем правильную дату
    
#     logger.warn(f"cancel_or_choose_callback_handler inlineKB_error необрабатываемое событие вызвал: {user.getId()}")
#     await query.answer( "Как это получилось?" , show_alert=True)


# WORK_END   Btn_message_endWork

@check_permission("Btn_message_endWork")
async def cmd_endWork(user, message: types.Message):

    post_id = user.endWork( int(message.date.timestamp())+GTM ) # Получает из Даты ЮниксДату и обрезает ее до инт

    await bot.send_message(user.getId(), MESSAGES['Answer_stopWork'].format(user.getLastPressedEndTime_s()),\
         reply_markup=inline_cancel_or_choose("work", "e", post_id))







def register_handlers_worker(dp: Dispatcher):
    dp.register_message_handler(cmd_startWork, Text(equals=MESSAGES["Btn_message_startWork"], ignore_case=True) )

    dp.register_message_handler(cmd_endWork, Text(equals=MESSAGES["Btn_message_endWork"], ignore_case=True) )

    # dp.register_message_handler(cmd_info, Text(equals=MESSAGES["Btn_message_info"], ignore_case=True) )

    # dp.register_callback_query_handler(cancel_or_choose_callback_handler, text_contains='BtnInl_message_cancel' )
    # dp.register_callback_query_handler(cancel_or_choose_callback_handler, text_contains='BtnInl_message_chooseAnother' )


    # dp.register_callback_query_handler(inline_infoDownload_callback_handler, text_contains='BtnInl_Download' )


    dp.register_callback_query_handler(inline_choose_time_point_callback_handler, text_contains='ChooseuTimePoint' )
    
    

