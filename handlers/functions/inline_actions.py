from constants.re_messages import MESSAGES as rm
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Одна кнопка закрыть
def inline_key_close_menu():
    text = rm['Btn_message_close_t']
    return InlineKeyboardButton(text, callback_data="BtnInl_close")

# Меню с одной кнопкой - закрыть
def inline_close_menu():
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    keyboard_markup.add(inline_key_close_menu())
    return keyboard_markup

#клавиатура подтверждения FSM
def inline_FSMAccept(mod = ""):#callback_addition, FSMAsked):
    """ out inline_FSMAccept"+":yes/no/cancel"+mod"""
    keyboard_markup = InlineKeyboardMarkup(row_width=3)

    keyboard_markup.add( InlineKeyboardButton( rm["FSMAccept_yes"], callback_data="inline_FSMAccept"+":yes"+mod ) )
    keyboard_markup.add( InlineKeyboardButton( rm["FSMAccept_no"], callback_data="inline_FSMAccept"+":no"+mod ) )
    keyboard_markup.add( InlineKeyboardButton( rm["Btn_message_cancel"], callback_data="inline_FSMAccept"+":cancel"+mod ) )

    return keyboard_markup

#Клавиатура выбора человека из всей компании
def inline_userList(user_list:dict):
    """ in: {user_id:name,...} out 'from_user_list'+f':{id}:{user_list[id]}' """
    keyboard_markup = InlineKeyboardMarkup(row_width=1)
    for id in user_list.keys():
        keyboard_markup.add( InlineKeyboardButton( user_list[id], callback_data="from_user_list"+f":{id}:{user_list[id]}" ) )
    keyboard_markup.add( InlineKeyboardButton( "Никто", callback_data="from_user_list"+":0:0" ) )
    return keyboard_markup
