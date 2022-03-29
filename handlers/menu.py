"""
Меню пользователя.

В нем он может:


-1) Показать информацию о посещениях
    О всех
        Выкидывает эксель файл
    О себе
        вывести информацию за день
        вывести информацию за месяц
            Законченный (прошлый)
            Новый (текущий)
        получить Excel файл
    О другом (если есть права)
        выведет список доступных людей
            тоже что о себе только о другом

3)Недавние события
Выводит последние записи из лога группы пользователя
    Для тех у кого есть права выводит кнопки
        Посмотреть события пользователя
        Посмотреть события группы
            выводит события группы, если доступны (Если есть события и есть права)
        Оставить заметку
            О себе
            О другом человеке

4)График дежурств
Выводит список дней и кто дежурит в эти дни
    Для тех у кого есть права выводит кнопки
        Изменить график

5)Помощь
    кнопка Обратная связь - выводит мои контакты
    Выводит список доступных пунктов и помощь по ним
    (как использовать эти команды)

6)Рабочие дни
    Выводит название группы и график рабочих дней группы человека 
    кнопка "изменить"
        выводит список дней в неделю [ПН:Р] или [СБ:В]
            при нажатии меняется осотояние
        сохранить навсегда - записывает в информацию пользователя
        сохранить до...
            выводит клавиатуру-календарь, при нажатии на дату записывает "время жизни правила"
                по истечению времени график удалится и будет стандартным

7)Администрирование
    Выводит кнопки
        поменять стоимость человка/час
            выводит пользователей
                запрашивает стоимость и сохраняет
        удалить пароль к группе
            выводит список паролей и групп, при нажатии на пароль - удаляет

        добавить пароль к группе
            выводит список групп
                запрашивает пароль

        удалить параметр группы
            группа
                список параметров
                    нажатие удаляет

        добавить параметр группы
            группа
                список возможных параметров
                    спрашивает строку параметра
                        при вводе сохраняет параметр

        удалить/добавить параметр пользователя
            как у группы

"""

from constants.help_messages import MESSAGES as hm
from constants.menu_messages import MESSAGES as mm
from constants.re_messages import MESSAGES as rm
from constants.config import MENU_AVILIBLE

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from creators.c_bot_create import bot
from decorators.d_perm_decorator import check_permission
from decorators.d_callback_live_decorator import check_live_callback

from h_functions.worker_excel_out import get_user_excel
from handlers.fsmachine import FSMChangeName
from handlers.functions.inline_actions import inline_FSMAccept, inline_key_close_menu, inline_close_menu

from Classes.User import User# Нужно для переименования

    
# Хендлер открытия меню 
@check_permission("Btn_message_Menu")
async def cmd_openMenu(pack, message: types.Message):

    await message.delete()

    user = pack[0] #User
    
    perm_list = user.getPermList()
    message = mm['Btn_message_Menu_answer']
    keyboard = inline_openMenu(perm_list)

    await bot.send_message( chat_id=user.getId(), text=message, reply_markup=keyboard )  



def inline_openMenu(user_perm_list):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    for a in MENU_AVILIBLE: #Добавляем те кнопки, к которым есть разрешения
        if a in user_perm_list:
            keyboard_markup.add( types.InlineKeyboardButton(text=mm[a], callback_data=a) )

    keyboard_markup.add( inline_key_close_menu() )
    return keyboard_markup



#Пользователь нажал Показать информацию о посещениях
@check_permission("BtnM_message_time")
@check_live_callback(True)
async def BtnM_message_time_callback_handler(pack, query: types.CallbackQuery):
    user = pack[0]

    fname = get_user_excel(user.getId())

    await query.message.reply_document( open(fname, 'rb') , reply_markup=inline_close_menu())
    await query.answer("Вот ваша таблица!", show_alert=True)

    await query.message.delete()



#Пользователь нажал Администрирование 
@check_permission("BtnM_message_admin")
@check_live_callback(True)
async def BtnM_message_admin_callback_handler(pack, query: types.CallbackQuery):

    """ Переименование тут будет пока что
    для этого нужно
    +Создать клавиатуру с кнопкой поменять имя 
    +Вызвать ее здесь
    Создать слушатель этой кнопки (где будет вход в стейт машин и вопрос)
    Создать слушаетель стейтмашины (где будет анализироваться текст и меняться параметры)
    """

    user = pack[0] #User
    
    perm_list = user.getPermList()
    message = mm['BtnM_message_admin_answer']
    keyboard = inline_admin_menu(perm_list)

    await bot.send_message( chat_id=user.getId(), text=message, reply_markup=keyboard ) 

    # await query.answer("Вот ваша таблица!", show_alert=True)
    await query.message.delete()

#клавиатура администрирования
def inline_admin_menu(user_perm_list):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)

    if "BtnM_message_rename" in user_perm_list:
        keyboard_markup.add( types.InlineKeyboardButton( mm["BtnM_message_rename"], callback_data="BtnM_message_rename" ) )

    keyboard_markup.add(inline_key_close_menu())
    return keyboard_markup



#Пользователь нажал "переименоваться" открывается ФСМ с запросом имени
@check_permission("BtnM_message_rename")
@check_live_callback(True)
async def BtnM_message_rename_callback_handler(pack, query: types.CallbackQuery):
    user = pack[0]
    userId = user.getId()

    await FSMChangeName.getNewName.set()


    msgId = await bot.send_message(userId, mm["BtnM_message_rename_ask"])

    state = Dispatcher.get_current().current_state()
    await state.update_data(key=f"{userId}:None:{msgId.message_id}")

    await query.message.delete()
    pass

# Человек вводит свое имя
async def FSMChangeName_message_handler(message:types.Message , state: FSMChangeName):
    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    userId, name, msg_id = fsmdata['key'].split(":")

    state = Dispatcher.get_current().current_state() #Записываем новую
    await state.update_data(key=f"{userId}:{message.text}:{msg_id}")

    text = message.text

    await bot.delete_message( message.from_user.id, message.message_id )

    kb=inline_FSMAccept()
    await bot.send_message(userId, mm["BtnM_message_rename_reask"].format(text) , reply_markup=kb)

# Обработка события инлайн клавиатуры
async def FSMChangeName_query_handler(query: types.CallbackQuery , state: FSMChangeName):
    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    userId, name, msg_id = fsmdata['key'].split(":")

    try:
        bot.delete_message(msg_id)
    except:
        print("FSMChangeName_query_handler except")

    if query.data == "inline_FSMAccept"+":yes":
        user_id = query.from_user.id
        user = User(user_id)
        user.rename(name)
        nname = user.getName()

        await query.answer( mm["BtnM_message_rename_answer"].format(nname) )
        await query.message.delete()
        await state.finish()

    elif query.data == "inline_FSMAccept"+":no":
        await query.answer( "Напишите новое имя" )
        await query.message.delete()

    elif query.data == "inline_FSMAccept"+":cancel":
        await query.answer( "Вы оставили свое старое имя.", show_alert=True )
        await query.message.delete()
        await state.finish()

    else:
        query.answer( "FSMChangeName_handler непредвиденный исход!.", show_alert=True )
        






def register_handlers_menu(dp: Dispatcher):
    #Вывод меню
    dp.register_message_handler(cmd_openMenu, Text(equals=rm["Btn_message_Menu"], ignore_case=True))

    #Вывод Показать информацию о посещениях (сейчас таблицы времени работы)
    dp.register_callback_query_handler(BtnM_message_time_callback_handler, text_contains='BtnM_message_time' )

    #Вывод Администрирование
    dp.register_callback_query_handler(BtnM_message_admin_callback_handler, text_contains='BtnM_message_admin')
    #События переименоватьСЯ
    dp.register_callback_query_handler(BtnM_message_rename_callback_handler, text_contains='BtnM_message_rename')
    dp.register_message_handler(FSMChangeName_message_handler, state = FSMChangeName.getNewName )
    dp.register_callback_query_handler(FSMChangeName_query_handler, state = FSMChangeName.getNewName)
    
    