"""
Отвечает за события не связанные с какой-либо конкретной группой
Узнает, что за человек пишет, выдает первые состояния
Регистрирует новичков
Управляет выходом из сотояний
"""

#Packages

from aiohttp import request
from creators.c_bot_create import bot#, company
from creators.c_company_create import company

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from handlers.fsmachine import FSMGiveGEO



#local
from constants.messages import MESSAGES

from Classes.User import User

#keyboard
from keyboards.from_permission import make_keyboard


from decorators.d_perm_decorator import check_permission


async def cmd_giveGEO(message: types.Message):
    user = company.getAndMakeUser(message.from_user.id, message.from_user.full_name)

    print("GEO FSM ACTIVATED")

    await FSMGiveGEO.giveGEO.set()


    await bot.send_message(user.getId(), "Подтвердите геолокацию. Нажмите на кнопку в заготовленной клавиатуре.", reply_markup=mkbtn_request_geo()) #Привязать клавиатуру

def mkbtn_request_geo():
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=1)
    
    key = types.KeyboardButton("Поделиться геолокацией", request_location=True)
    keyboard_markup.add(key)

    return keyboard_markup

# @dp.message_handler(content_types=['location'])
async def FSMnGEO_handler(message: types.Location, state: FSMGiveGEO):

    user = company.getAndMakeUser(message.from_user.id, message.from_user.full_name)

    print("GEO FSM RECIVED")

    print(message)

    try:
        print("GEO FSM try")

        lat = message.location.latitude
        lon = message.location.longitude
        reply = "latitude:  {}\nlongitude: {}".format(lat, lon)

    except:
        print("GEO FSM except")
        await bot.send_message(user.getId(), "Подтвердите геолокацию. Нажмите на кнопку в заготовленной клавиатуре.", reply_markup=mkbtn_request_geo()) #Привязать клавиатуру

    else:
        print(reply)
        await message.answer(reply, reply_markup=inline_auth( user.getId() ) ) 
        await state.finish()


    





# async def getUser(any_user_data: types.Message, perm=""):
#     """Создает пользователя из данных от Телеги, проверяет права, если задана строка perm\n
#     return вернет True, если указана строка Запроса на права и права есть\n
#     Иначе отправит пользователю "нет прав" и вернет False"""
#     id = 0
#     name = "???"

#     try: 
#         id = any_user_data.from_user.id
#         name = any_user_data.from_user.full_name
#     except:
#         print("getUserFromCompany EXCEPT")
#         return

#     user = company.getAndMakeUser(id, name)

#     if perm: #Если строка проверки прав указана
#         if user.hasPermission(perm): # Если у пользователя есть права
#             return user, True
            
#     await bot.send_message(id, MESSAGES['Answer_perm_error'])
#     return user, False # Если задана строка прав,если у пользователя нет на нее прав


# dbg = True

# def get_user(id, name="???"):
#     """Получает запись по пользователю
#     Пытается получить пользователя из Объекта компания
#     Если его там нет, то создает из полученого Id и имени (подставляет ?? если имя не указано))

#     Проверяет, загружен ли пользователь в список компании"""

#     user_req = company.getWorker(id)
#     if user_req: #Если пользователь есть в списке компании (сбрасывается при перезапуске бота)
#         user = user_req
#     else: # Если нет, то создается новый пользователь (выполняется только, если пользователь первый раз после перезапуска написал боту)
#         user = user = User(id, name)
#         user.update() #Если пользователя не было в БД, то он записывается с нулевыми правами, иначе вся его статистика загружается из БД

#         company.addWorker(user) #добавляем пользователя в список компании (Что бы иметь возможность обрабатывать всех людей, которые есть)

#     return user





# START


async def cmd_start(message: types.Message, state: FSMContext):
    user = company.getAndMakeUser(message.from_user.id, message.from_user.full_name)

    msg = MESSAGES['Answer_start']
    if user.hasPermission("Perk_see_Menu"):
        msg += """
        
        Вас должны добавить в список работников или 
        вы должны получить и ввести пароль, что бы
        отмечаться о начале/конце рабочего дня """

    await bot.send_message(user.getId(), msg, reply_markup=make_keyboard(user.getPermList()) ) #Привязать клавиатуру

    await bot.send_message(user.getId(), "Нажмите, если у вас есть пароль:", reply_markup=inline_auth( user.getId() ) ) #Привязать клавиатуру


#Инлайн клавиатура для авторизации
def inline_auth(user_id):

    keyboard_markup = types.InlineKeyboardMarkup()

    key = types.InlineKeyboardButton(text="У меня есть пароль..", callback_data="BtnInl_Auth:"+str(user_id) )
    keyboard_markup.insert( key )

    return keyboard_markup














# HELP   Btn_message_help


async def cmd_help(message: types.Message, state: FSMContext):
    user = company.getAndMakeUser(message.from_user.id, message.from_user.full_name)

    await bot.send_message(user.getId(), MESSAGES['Answer_help'])  


# SPECIAL


async def special_msg(message: types.Message):
    await bot.send_message(1368534442, f"Бот {message.from_user.id} написал") 


# ANY ELSE


async def echo_message(message: types.Message):

    user = company.getAndMakeUser(message.from_user.id, message.from_user.full_name)
    kb = make_keyboard(user.getPermList() )
    message = MESSAGES['Answer_echo']

    await bot.send_message(user.getId(), message, reply_markup=kb)





def register_handlers_other(dp: Dispatcher):

#test inline



    dp.register_message_handler(cmd_giveGEO, Text(equals="geo") )

    dp.register_message_handler(FSMnGEO_handler, content_types=['location'])
    dp.register_message_handler(FSMnGEO_handler, state = FSMGiveGEO.giveGEO)


    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_start, Text(equals=MESSAGES["Btn_message_start"], ignore_case=True), state="*")

    dp.register_message_handler(cmd_help, state="*", commands='help')
    dp.register_message_handler(cmd_help, Text(equals="?") , state="*" )
    dp.register_message_handler(cmd_help, Text(equals=MESSAGES["Btn_message_help"], ignore_case=True), state="*")

    dp.register_message_handler(special_msg, commands=['special'])
    dp.register_message_handler(echo_message)
    
    

    









# #import imp
# from aiogram import types, Dispatcher
# from aiogram.dispatcher.filters import Text

# #from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher import FSMContext
# #from rx import empty

# from store.bd_link import get_user_info, write_new_user

# from fsmachines.other import FSMGuestGreeting
# # машина состояний. Для приветствия, регистрации (fsms file)
# # class FSMGuestGreeting(StatesGroup):
# #     name = State()
# #     photo = State()
# #     #contact = State()
# from fsmachines.other import FSMWorker

# from bot_create import dp, bot
# from store.messages import MESSAGES

# from keyboards import kb_guest

# from UserClass import User


# # @dp.message_handler(commands=['start'])
# async def cmd_start(message: types.Message):
#     """ 
#     Человек написал старт. Проверяется кто он, есть ли он в базе данных, выдаются права, меняются статусы
#     """
#     user_info = get_user_info(message.from_user.id)

#     if not user_info: #Есть ли человек в бд
#         # print("Пользователя нет в бд")
        
#         await FSMGuestGreeting.name.set()
#         await bot.send_message(message.from_user.id,"Привет. Как тебя зовут? По какому имени узнают?")

#     else: 
#         # print("Пользователь есть в бд")
#         await bot.send_message(message.from_user.id, f"Привет. Я тебя знаю. Ты {user_info['name']}.")
#         await FSMWorker.user.set()

#         #await bot.send_photo(message.from_user.id, user_info['photo_id'])
#         #await bot.send_message(message.from_user.id,f"Это же ты? {user_info['name']}")


# # @dp.message_handler(state="*", commands="help")
# # @dp.message_handler(Text(equals='помощь', ignore_case=True), state="*")
# async def cmd_help(message: types.Message, state: FSMContext):
#     await message.reply("Если что-то не так, то введи любое сообщение и выведется клавиатура с доступными тебе кнопками")    


# # машина состояний. Контролирует выход из состояний
# # @dp.message_handler(state="*", commands="cancel")
# # @dp.message_handler(Text(equals='cancel', ignore_case=True), state="*")
# async def cmd_cancel(message: types.Message, state: FSMContext):
#     """ Обрабатывает выход из состояний машины"""
#     current_state = await state.get_state()

#     # print("state: ", current_state,  )
#     if current_state is None:
#         await message.reply("Ты вне состояний. Нельзя отменить")
#         return

#     if (current_state.find("FSMWorker")!=-1):
#         await message.reply("Ты в состоянии \"работа\". Нельзя отменить")
#         return

#     if (current_state.find("FSMGuestGreeting")!=-1):
#         await state.finish()
#         await message.reply("Регистрация отменена. Введи /start что бы повторить попытку")
#         return


#     # Оповещать разработчика об этом
#     await state.finish()
#     await message.reply("Введи /start . Что-то пошло не так")


# # машина состояний. Для приветствия, регистрации. Обрабатывает Имя.
# # @dp.message_handler(state=FSMGuestGreeting.name)
# async def process_name(message: types.Message, state: FSMContext):
#     """
#     Обработка ввода имени
#     """
#     async with state.proxy() as data:
#         data['name'] = message.text

#     await FSMGuestGreeting.next()
#     await bot.send_message(message.from_user.id,"Сделай селфач плс.")    
#     #print( get_user_info(message.from_user.id) )

#     # await message.reply(MESSAGES['start'])

# # машина состояний. Для приветствия, регистрации. Обрабатывает Фото
# # @dp.message_handler(content_types=['photo'], state=FSMGuestGreeting.photo)
# async def load_photo(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['photo'] = message.photo[0].file_id
        
#     #await FSMGuestGreeting.next()
#     await bot.send_message(message.from_user.id,"Фото получил.")  

#     user_data = await state.get_data()
#     print(user_data)
#     write_new_user([(message.from_user.id, message.from_user.username, message.from_user.full_name,
#         user_data['name'], "",  user_data['photo'] )])
        
#     #)

#     await message.reply("Администраторам выслан запрос об одобрении заявки. Жди подтверждения.")
#     await state.finish()


# # @dp.message_handler()
# async def echo_message(msg: types.Message):
#     """
#     Если человек вне машины состояния, можно вывести клавиатуру с кнопкой "Восстановить" что бы получить состояние или "Зарегистрироваться" что бы получить статус
#     """
#     await bot.send_message(msg.from_user.id,"Используй клавиатуру для действий", reply_markup=kb_guest)
#     # await bot.send_message(msg.from_user.id, msg.text)


# def register_handlers_other(dp: Dispatcher):
#     dp.register_message_handler(cmd_start, commands=['start'])
    
#     dp.register_message_handler(cmd_help, state="*", commands="help")
#     dp.register_message_handler(cmd_help, Text(equals='помощь', ignore_case=True), state="*")

#     dp.register_message_handler(cmd_cancel, state="*", commands="cancel", )
#     dp.register_message_handler(cmd_cancel, Text(equals='вернуться', ignore_case=True), state="*")

#     dp.register_message_handler(process_name, state=FSMGuestGreeting.name)

#     dp.register_message_handler(load_photo, content_types=['photo'], state=FSMGuestGreeting.photo)

#     dp.register_message_handler(echo_message)
    