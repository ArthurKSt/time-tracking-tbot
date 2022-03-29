
"""
Отвечает за авторизацию пользователей!

#Инлайн клавиатура создается рядом с обработчиком старт     inline_auth(user_id)
    # key = types.InlineKeyboardButton(text="У меня есть пароль..", callback_data="BtnInl_Auth:"+str(user_id) )

(Может стоит перенести команду старт - сюда?)

"""




from creators.c_bot_create import bot#, company
from Classes.User import User
from creators.c_company_create import company

from aiogram import types, Dispatcher
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher import FSMContext

# from excel.worker_exc_out import getExTable

# from store.messages import MESSAGES

from handlers.fsmachine import FSMAuth

from keyboards.from_permission import make_keyboard


# from d_perm_decorator import check_permission


from database.bd_user_activity import select_group_byPassword
from database.bd_user_group_activity import insert_user_in_group, select_group_byID, delete_user_from_group, select_group_list_byUser


#Инлайн клавиатура создается рядом с обработчиком старт     inline_auth(user_id)
    # key = types.InlineKeyboardButton(text="У меня есть пароль..", callback_data="BtnInl_Auth:"+str(user_id) )

#Далее срабатывает событие здесь, задается вопрос "ВВеди пароль" и меняется у пользователя группа





# #Слушатель инл.клав для вывода Информации по пользователям
async def inline_auth_callback_handler(query: types.CallbackQuery):
    #in ChooseuTimePoint:таблица:  ид записи  или отмена(закрывает выобор даты)

    answer_data, user_id = query.data.split(":")

    if answer_data == 'BtnInl_Auth': # Если событие
        
        # user = company.getAndMakeUser(user_id)

        # user = User

        # bdPermission = select_group_byPassword("sadf")

        # if bdPermission: permission = bdPermission
        # else: permission = 0

        # user.setPermission(permission)


        await bot.send_message( chat_id=user_id, text="Введите пароль: " )
        # await bot.send_message(chatId, new_text+"Twice")

        await FSMAuth.getPassword.set() #В FSM машине в логи отдельно писать ответ пользователя (не передать ид задачи)

        state = Dispatcher.get_current().current_state()
        await state.update_data(key=f"{user_id}")

        # await query.message.reply_document( open(filename, 'rb') )
        # await query.answer("Получай!", show_alert=True)

        
    else:
        await query.answer("Что то пошло не так!", show_alert=True)


# Человек вводит пароль
async def FSMAuth_handler(message:types.Message , state: FSMAuth):
    # answer = message.text #добавляю текст от пользователя в переменную
    data_ = await state.get_data()
    user_id = data_['key']

    user = company.getAndMakeUser(user_id, "Попытавшийся авторизоваться")

    bdPermission = select_group_byPassword(message.text)

    if bdPermission: 

        # permission = bdPermission[0]

        group = select_group_byID( bdPermission[0] )
        if group:
            
            bd_group_list = select_group_list_byUser(user_id)
            if bd_group_list:
                for _group in bd_group_list:
                    delete_user_from_group( user_id, _group[0] ) #Удаляем человека из групп


            insert_user_in_group( user_id, bdPermission[0])
            msg = f" Вы авторизовались в группе: {group[3]}"

        else: msg = "Группы для которой создан пароль более не существует"

    else: 
        #permission = user.getPermission()
        msg = f" Такого пароля не найдено"

    await bot.send_message( chat_id=user_id, text=msg, reply_markup=make_keyboard( user.getPermList(now=True) ) )
    await state.finish()








def register_handlers_auth(dp: Dispatcher):

    dp.register_callback_query_handler(inline_auth_callback_handler, text_contains='BtnInl_Auth' )
    dp.register_message_handler(FSMAuth_handler, state = FSMAuth.getPassword)
    
    


