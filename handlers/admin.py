from curses.ascii import isdigit
from Classes.User import User
from creators.c_bot_create import bot#, company
from creators.c_company_create import company

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from database.bd_user_activity import select_cost_by_id, insert_cost


from constants.messages import MESSAGES

from handlers.fsmachine import FSMChengeCost

from decorators.d_perm_decorator import check_permission



#Делаем инлайн клавиатуру для выбора работника
def inline_choose_worker_forRecosting():

    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    callbackData = "ChooseWorker:"

    workerIds = company.getWorkersId()
    if not workerIds : return None

    for id in workerIds:

        _user = company.getWorker( id )
        costbd = select_cost_by_id( id )
        cost = costbd[2] if costbd else 0


        text = f"> {_user.getName()} (Сейчас: {cost}) <"

        row_btn = types.InlineKeyboardButton(text, callback_data=callbackData+str( _user.getId() )  )
        keyboard_markup.insert( row_btn )
    
    keyboard_markup.add( types.InlineKeyboardButton(MESSAGES['Btn_message_cencel'], callback_data=callbackData+"cancel") )

    return keyboard_markup



async def inline_choose_worker_forRecosting_callback_handler( query: types.CallbackQuery):
    #in ChooseuTimePoint:таблица:  ид записи  или отмена(закрывает выобор даты)

    answer_data, user_id = query.data.split(":")

    if answer_data == 'ChooseWorker': # Если событие
        
        if user_id!='cancel': #Если в пост айди = айди

            await bot.send_message( chat_id=query.message.chat.id, text="Сколько установить ЗП в час?")
            
            await FSMChengeCost.getNewCost.set() #В FSM машине в логи отдельно писать ответ пользователя (не передать ид задачи)

            state = Dispatcher.get_current().current_state()
            await state.update_data(key=f"{user_id}")
        
        else:
            #cancel
            pass


async def FSMChengeCost_handler(message:types.Message , state: FSMChengeCost):
    # answer = message.text #добавляю текст от пользователя в переменную
    data_ = await state.get_data()
    user_id = data_['key']

    try:
        cost = message.text
    except:
        await bot.send_message( message.chat.id, "Нужно ввести Целое Число")
        return
    else: 

        user = company.getWorker(user_id)


        await bot.send_message( message.chat.id, f"Вы ввели: {cost}")
        insert_cost(user_id, message.text)

        await state.finish()




@check_permission("Btn_message_set_cost")
async def cmd_setCost(user, message: types.Message):
    """ Поменять стоимость человека в час"""


    # Вывести всех работников списком из инлайн-кнопок
    """
    При нажатии на человека открывается ФСМ с вводом стоимости в час
    """

    

    kb = inline_choose_worker_forRecosting()


    await bot.send_message(user.getId(), "Работники:", reply_markup=kb) 










def register_handlers_admin(dp: Dispatcher):

    dp.register_message_handler(cmd_setCost, Text(equals=MESSAGES["Btn_message_set_cost"], ignore_case=True) )
    dp.register_callback_query_handler( inline_choose_worker_forRecosting_callback_handler, text_contains='ChooseWorker:' )

    dp.register_message_handler(FSMChengeCost_handler, state = FSMChengeCost.getNewCost)


    # dp.register_callback_query_handler(inline_auth_callback_handler, text_contains='BtnInl_Auth' )
    # dp.register_message_handler(FSMAuth_handler, state = FSMAuth.getPassword)


    pass