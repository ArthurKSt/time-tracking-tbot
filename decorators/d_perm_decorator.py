
from aiogram.types import Message, CallbackQuery

from creators.c_bot_create import bot
from creators.c_logger_create import logger as log

from Classes.User import User

from keyboards.from_permission import make_keyboard

from constants.messages import MESSAGES

from h_functions.delete_message_per_time import delete_msg_per_time


def check_permission(permission="", any_way_do=False, need_answer=False):
    "in: str_permission_name, insert into func pack[user, permission, hasPerm(bool), accessMsgId]"


    def decorator(handler_or_callback_function):
        _fname = handler_or_callback_function.__name__
        _fdoc = handler_or_callback_function.__doc__

        async def wrapper(*args): 

            id = 0
            name = "???"
            isCallBack = None

            for item in args:
                if isinstance(item, Message):
                    try:
                        id = item.from_user.id
                        name = item.from_user.full_name
                    except:
                        log.error("Не удалось получить пользователя из объекта месенджера")
                    else: break

                if isinstance(item, CallbackQuery):
                    try:
                        id = item.from_user.id
                        name = item.from_user.full_name
                        isCallBack = item
                    except:
                        log.error("Не удалось получить пользователя из объекта месенджера")
                    else: break

                else: continue

            user = User(id, name)
            TooManyActions = not user.do()
            if TooManyActions:
                if isCallBack:
                    await isCallBack.answer(MESSAGES['Answer_too_many_actions'], show_alert=True)
                else:
                    nmsg = await bot.send_message(id, MESSAGES['Answer_too_many_actions'] )
                    delete_msg_per_time( nmsg.message_id, 30 )

                #print("Too many actions! :", handler_or_callback_function.__name__)
                return None


            # pack = [user, permission, hasPerm(bool), prevMsgId]
            pack = [user, permission]


            if user.hasPermission(permission) or any_way_do: # Если у пользователя есть права или в любом случае нужно сделать
                pack.append(user.hasPermission(permission))

                if permission!="" and need_answer==True: 
                    permMsg = await bot.send_message(id, MESSAGES['Answer_perm_accees'] )
                    pack.append(permMsg.message_id)
                else:
                    pack.append(0)

                
                result = await handler_or_callback_function(pack, *args) #Выполняем команду и возвращаем результат

                return result
                
            else: 
                log.info(f"Пользователь {user.getName()} пытался выполнить \"{permission}\" не имея прав")
                if permission !="": await bot.send_message(id, MESSAGES['Answer_perm_error'], reply_markup=make_keyboard(user.getPermList() ) )
                return None

        wrapper.__name__ = _fname
        wrapper.__doc__ = _fdoc
        return wrapper #возвращаем новую функцию

    
    return decorator



# class FailedToGetUser(Exception):
#     def __init__(self, info: str, message: str = ""):
#         self.info = info
#         self.message = "Cant get User info from telegram activity" if not message else message
#         super().__init__(self.message)

#     def __str__(self):
#         return f"{self.message} :\n\t{self.info}"