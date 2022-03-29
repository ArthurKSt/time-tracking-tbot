
from aiogram.types import CallbackQuery

from creators.c_bot_create import bot
from creators.c_logger_create import logger as log
from creators.c_scheduled_create import scheduled

from constants.config import CALLBACKLIVE_TIME, GTM
from constants.messages import MESSAGES


def check_live_callback(needCheck = True):
    "in: str_permission_name, insert into func pack[user, permission, hasPerm(bool), accessMsgId]"

    def decorator(handler_or_callback_function):
        _fname = handler_or_callback_function.__name__
        _fdoc = handler_or_callback_function.__doc__

        async def wrapper(*args): 

            query = CallbackQuery

            timeNow = scheduled.getTime()
            timeMsg = 0

            for item in args:
                if isinstance(item, CallbackQuery):
                    try:
                        query = item
                        timeMsg = int(item.message.date.timestamp())+GTM
                    except:
                        log.warn(f"Не получилось получить время из callback")
                        return
                else:
                    continue

            if (timeNow - timeMsg) < CALLBACKLIVE_TIME: #Делаем действие

                

                result = await handler_or_callback_function(*args)

                return result
                
            else: 
                await query.answer(MESSAGES['Answer_oldButton'])
                await query.message.delete()
                
                log.info(f"попытка выполнить действие после его устаревания")
                return

        wrapper.__name__ = _fname
        wrapper.__doc__ = _fdoc
        return wrapper #возвращаем новую функцию

    
    return decorator
