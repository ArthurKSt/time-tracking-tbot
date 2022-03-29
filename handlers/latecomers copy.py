
from creators.c_bot_create import bot
from creators.c_scheduled_create import scheduled as sch
from creators.c_logger_create import logger as log

from handlers.fsmachine import FSMWhyNotAtWork, FSMWhoCanConfirm, FSMWhyNotCome
from aiogram import Dispatcher, types

from database.bd_tasks_activity import select_task_byId, delete_task_byId
from database.bd_log_activity import insert_addition, insert_log


# ____ Таймер который отвечает за написание сообщений людям, которые не отметились вовремя (Ниже)


# Создается в главном цикле планировщика, задает первый вопрос "Почему ты не пришел?"
async def timer_Why_Not_At_Work(user_id):
    """ Задает вопрос пользователю, почему не пришел вовремя
    Создает запрос на повторную проверку"""


    time = sch.getTime()

    #Создать задачу "Проверка, почему не пришел"
    #Создать запрос на повторную проверку (результат задачи)

    taskId = sch.createStartWorkAsk(user_id) # Лучше дополнить уровнем (насколько опоздал)
    #Дополнить временем актуальности. И если время актуальности близко ко времени удалению, то записывать задачу
    #И все ее пометки в Лог и его пометки!!
    # if taskId:
    #     logId = insert_log("NotAtWork","Задача повторилась. ", time, user_id)


    msg = "Вы не отметились, что пришли на работу, почему?"
    #Я еще не пришел, я уже пришел (Если пришел, то кто может подтвердить?)

    

    logId = insert_log("NotAtWork","Во время начала рабочего дня не был отмечен как на месте", time, user_id)
    #Написать в лог, что пользователь не был отмечен на рабочем месте

    #Передать в инлайн кнопку ид Задачи

    kb = inline_Already_or_Yet(taskId, logId)

    try:
        await bot.send_message(user_id, msg, reply_markup=kb)
    except:

        delete_task_byId(taskId)
        logId = insert_log("NotAtWork","Не вышло создать задачу, что человека нет на месте. (Заблокировал бота?)", time, user_id)
        pass


#Инлайн клавиатура для ответа
#Делаем инлайн клавиатуру для ответа на сообщение "Я уже пришел, Я еще не пришел.."
def inline_Already_or_Yet(taskId, logId):
    """ опис """
    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)

    mod = f":{taskId}:{logId}" #По нему можно отделять, для какой таблицы сработало событие

    text_and_data = (
        ("Я еще не пришел", 'BtnInl_Already_or_Yet'+mod+":yet"),
        ("Я уже пришел", 'BtnInl_Already_or_Yet'+mod+":already"),
        ("Я не приду", 'BtnInl_Already_or_Yet'+mod+":no"),
    ) #По тексту выводится кнопка, по данным слушает слушатель

    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.row(*row_btns)

    return keyboard_markup


#Делаем слушатель клавиатуры для ответа "Я уже пришел" или "Я еще не пришел"
async def Already_or_Yet_callback_handler(query: types.CallbackQuery):
    """слушатель инлайн клавиатуры """

    answer_data, task_id, log_id, status = query.data.split(":")

    msgId = query.message.message_id
    chatId = query.from_user.id

    oldMsg = query.message.text+"\n"

    #Проверяем, существует ли задача по этому запросу, если нет, то пишем пользователю, что он опоздал отчитываться
    bd = select_task_byId(task_id)
    if not bd:
        await query.answer("Вы не ответили вовремя и рапорт на вас уже написан")
        
        new_text = "Вы не ответили вовремя и рапорт на вас уже написан! :("
        await bot.edit_message_text( chat_id=chatId, message_id=msgId, text=oldMsg+new_text, reply_markup=None )
        #Человек отвечал так долго, что задача уже удалилась
        #В логи все равно должно это попасть. Решение: В цикле проверять "Актуальность задачи", которая на 10мин меньше времени удаления
        #И Если актуальность прошла, в логи писать, что человек не ответил вовремя
        return


    if status == 'yet': # Если событие сработало на "Я еще не пришел"

        # await timer_Why_Not_At_Work(chatId) 

        sch.createStartWorkAsk(chatId)

        await query.answer("Вопрос, почему вы не пришли?")

        new_text = "Напиши, почему вы не пришли?"

        await bot.edit_message_text( chat_id=chatId, message_id=msgId, text=oldMsg+new_text, reply_markup=None )
        # await bot.send_message(chatId, new_text+"Twice")

        await FSMWhyNotAtWork.getAnswer.set() #В FSM машине в логи отдельно писать ответ пользователя (не передать ид задачи)

        state = Dispatcher.get_current().current_state()
        await state.update_data(key=f"{task_id}:{log_id}")


    elif status == 'already': # Если событие сработало на "Я уже пришел"

        delete_task_byId(task_id)

        new_text = "Кто может подтвердить, что вы пришли раньше?"
        
        await bot.edit_message_text( chat_id=chatId, message_id=msgId, text=oldMsg+new_text, reply_markup=None )
        await FSMWhoCanConfirm.who.set() #В FSM машине в логи отдельно писать ответ пользователя (не передать ид задачи)

        state = Dispatcher.get_current().current_state()
        await state.update_data(key=f"{task_id}:{log_id}")

        pass

    elif status == 'no': # Если событие сработало на "Я уже пришел"

        new_text = "Почему вы не придете?"

        delete_task_byId(task_id)
        
        await bot.edit_message_text( chat_id=chatId, message_id=msgId, text=oldMsg+new_text, reply_markup=None )
        await FSMWhyNotCome.whyNotCome.set() #В FSM машине в логи отдельно писать ответ пользователя (не передать ид задачи)

        state = Dispatcher.get_current().current_state()
        await state.update_data(key=f"{task_id}:{log_id}")

    else: #Если событие сломанное
        log.warn("timer:Already_or_Yet_callback_handler: Не верный статус")


# Человек оправдывает опоздание 
async def FSMAnswerWhyLate_handler(message:types.Message , state: FSMWhyNotAtWork):
    # answer = message.text #добавляю текст от пользователя в переменную
    taskNlog = await state.get_data()
    #print(taskNlog)
    taskId, logId = taskNlog['key'].split(":")

    answ = message.text

    #Если человек не успел ответить за время жизни задания:
    bd = select_task_byId(taskId)
    if not bd:
        await message.reply("Вы не ответили вовремя и рапорт на вас уже написан")

        answ = "Человек ответил поздно: " + answ

        insert_addition(logId, answ, sch.getTime())
        
        #Человек отвечал так долго, что задача уже удалилась
        #В логи все равно должно это попасть. Решение: В цикле проверять "Актуальность задачи", которая на 10мин меньше времени удаления
        #И Если актуальность прошла, в логи писать, что человек не ответил вовремя
    else:
        #Иначе пусть объясняется, message пойдет в лог

        msg = "Так и запишем. Вы не пришли вовремя потому что: \n {}".format(answ)

        insert_addition(logId, answ, sch.getTime())

        await bot.send_message(message.from_user.id, msg)

        # await state.update_data(answer1 = answer)#добавляю полученную инфу в класс выше

    await state.finish()


# Человек доказывает, что был на месте
async def FSMAnswerWhoConfirm_handler(message:types.Message , state: FSMWhoCanConfirm):
    # answer = message.text #добавляю текст от пользователя в переменную
    taskNlog = await state.get_data()
    #print(taskNlog)
    taskId, logId = taskNlog['key'].split(":")

    answ = message.text

    msg = "Так и запишем. Вы не отметились, но {} может подтвердить, что вы были на месте".format(answ)

    await bot.send_message(message.from_user.id, msg)
    await bot.send_message(message.from_user.id, "Около скольки часов вы пришли?")

    inBd = f"Работник оправдался тем, что он забыл отметиться, но {answ} может подтвердить, что он пришел вовремя"
    insert_addition(logId, inBd, sch.getTime())


    # await FSMWhoCanConfirm.time.set() #Не переходит, ошибка
    # await state.next() № ошибка
    # await FSMWhoCanConfirm.next()
    await FSMWhoCanConfirm.ctime.set()

    state = Dispatcher.get_current().current_state()
    await state.update_data(key=f"{taskId}:{logId}")



async def FSMAnswerTime_handler(message:types.Message , state: FSMWhoCanConfirm):
    
    taskNlog = await state.get_data()
    taskId, logId = taskNlog['key'].split(":")

    answ = message.text
    msg = "Так и запишем. Вы пришли около {}".format(answ)

    inBd = f"Работник написал, что был около {answ} на рабочем месте"
    insert_addition(logId, inBd, sch.getTime())

    await bot.send_message(message.from_user.id, msg)

    await state.finish()


async def FSMWhyNotCome_handler(message:types.Message , state: FSMWhyNotCome):
    
    taskNlog = await state.get_data()
    taskId, logId = taskNlog['key'].split(":")

    answ = message.text
    msg = "Так и запишем. Вы не придете потому что {}".format(answ)

    inBd = f"Работник написал, что не придет сегодня потому что: {answ} "
    insert_addition(logId, inBd, sch.getTime())

    await bot.send_message(message.from_user.id, msg)

    await state.finish()


# ____ Таймер который отвечает за написание сообщений людям, которые не отметились вовремя (Выше)

def register_handlers_latecomers(dp: Dispatcher):
    #dp.register_callback_query_handler( fcn , text_contains=' inlData:keys ' )

    dp.register_message_handler(FSMAnswerWhyLate_handler, state = FSMWhyNotAtWork.getAnswer)

    dp.register_message_handler(FSMAnswerWhoConfirm_handler, state = FSMWhoCanConfirm.who)
    dp.register_message_handler(FSMAnswerTime_handler, state = FSMWhoCanConfirm.ctime)

    dp.register_message_handler(FSMWhyNotCome_handler, state = FSMWhyNotCome.whyNotCome)

    dp.register_callback_query_handler( Already_or_Yet_callback_handler , text_contains='BtnInl_Already_or_Yet' )

    pass