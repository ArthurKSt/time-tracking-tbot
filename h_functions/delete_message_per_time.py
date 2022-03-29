from database.bd_tasks_activity import insert_task
from creators.c_scheduled_create import scheduled
from constants.config import SCHED_TIME_REMOVE_AFTER_DO

from creators.c_bot_create import bot

def delete_msg_per_time(chat_id,message_id, utime):
    """ Удаляет сообщение в указанное время (секунды)"""

    task_text = "1:deleteMessage" 
    for_who = f"-:=:{chat_id}:{message_id}"
    create_time = scheduled.getTime()
    actual_time = create_time+utime
    remove_time = actual_time+SCHED_TIME_REMOVE_AFTER_DO

    insert_task(task_text, for_who, create_time, actual_time, remove_time)

    return

async def do_delete(for_who:str):
    parm = for_who.split(":")
    try:
        await bot.delete_message( parm[2], parm[3] )
    except:
        print("Попытка удалить сообщение, которое не существует или не доступно")