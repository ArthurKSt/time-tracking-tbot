
from creators.c_bot_create import bot
from creators.c_scheduled_create import scheduled
from creators.c_logger_create import logger as log
from database.bd_user_activity import select_user

from decorators.d_callback_live_decorator import check_live_callback
from decorators.d_perm_decorator import check_permission
from h_functions.tools import addTime

from handlers.fsmachine import FSMAreYouLate
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from database.bd_tasks_activity import select_task_byId, delete_task_byId
from database.bd_log_activity import insert_addition, insert_log
from database.bd_user_time_activity import select_whoStarted

from handlers.functions.clock import DialogClock, clock_callback
from handlers.functions.inline_actions import inline_FSMAccept, inline_close_menu, inline_userList

from Classes.User import User


# ____ Таймер который отвечает за написание сообщений людям, которые не отметились вовремя (Ниже)


async def test_handler(message: types.Message):
    await WhyNotAtWork(message.from_user.id)

#Когда время текущее подходит ко времени аутуальности задачи опросить все ли начали, таймер узнает, нужно ли задать вопрос сейчас или позже
async def late_needAsk(user_id, taks_id):
    #Время актуальности = времени, когда человек должен начать работу
    user = User(user_id)
    if not user.isAtWork():
        await WhyNotAtWork(user_id)
    delete_task_byId(taks_id)
        

async def WhyNotAtWork(user_id):
    msg = "Вы не отметились, что пришли на работу, почему?"
    time = scheduled.getTime()
    logId = insert_log("NotAtWork","Во время начала рабочего дня не был отмечен как на месте", time, user_id)
    nextAskTaskId = scheduled.create_reask_task(user_id, "0:checkAtWork", 20)
    kb = inline_Already_or_Yet(nextAskTaskId)
    # await FSMAreYouLate.FirstAnswer.set()

    
    # fsmdata = await state.get_data() #Получаем информацию из ФСМ
    # userId, name, msg_id = fsmdata['key'].split(":")
    try:
        await bot.send_message(user_id, msg, reply_markup=kb)

    except:
        logId = insert_log("NotAtWork","Не вышло создать задачу, что человека нет на месте. (Заблокировал бота?)", time, user_id)


#Инлайн клавиатура для ответа
def inline_Already_or_Yet(taskId):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    text_and_data = (
        ("Я уже на рабочем месте", 'inline_late_Already'+f":{taskId}"),
        ("Я еще не на рабочем месте", 'inline_late_Yet'+f":{taskId}"),
        ("Меня не будет сегодня", 'inline_late_NoToday'+f":{taskId}"),
    ) #По тексту выводится кнопка, по данным слушает слушатель
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.add(*row_btns)
    return keyboard_markup


#######  ALREADY  #######  #######  #######  ALREADY  #######  #######  #######  ALREADY  #######
#######  #######  #######  #######  ALREADY  #######  #######  #######  ALREADY  #######  #######
#######  #######  ALREADY  #######  #######  #######  ALREADY  #######  #######  #######  #######
#######  #######  #######  ALREADY  #######  #######  #######  ALREADY  #######  #######  #######


#Человек нажал, что уже пришел. Нужно во сколько пришел? Кто подтвердит?
@check_live_callback(True)
async def inline_late_Already_callback_handler(query: types.CallbackQuery):
    user_id = query.message.chat.id

    await bot.delete_message( query.message.chat.id, query.message.message_id )

    nextAskTaskId = query.data.split(":")[1]

    text = """
    Вы утверждаете, что пришли, но забыли или не смогли нажать кнопку?
    Во сколько времени вы пришли?
    """

    await FSMAreYouLate.WhenYouCome.set()

    last_msg = await bot.send_message(user_id, text, reply_markup=await DialogClock().start_clock())
    last_msg_id = last_msg.message_id
    state = Dispatcher.get_current().current_state(user=user_id)
    await state.update_data(key=f"{nextAskTaskId}:{user_id}:{last_msg_id}:0")

#Человек выбирает время в которое пришел
async def process_dialog_clock(callback_query: types.CallbackQuery, callback_data: dict, state: FSMAreYouLate):
    selected, date = await DialogClock().process_selection(callback_query, callback_data)
    
    if selected:
        additionN = date.strftime("%H,%M")
        text = f'Вы выбрали {date.strftime("%Hч. %Mм. сегодняшнего дня")}\nКто видел как вы пришли?'
        user_id = callback_query.message.chat.id

        workersAtWork = select_whoStarted( scheduled.getDate() )
        userDict = {}
        for worker in workersAtWork:
            try:
                userDict[worker[0]] = select_user(worker[0])[1]
            except: pass
        kb=inline_userList(userDict)

        fsmdata = await state.get_data() #Получаем информацию из ФСМ
        nextAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":")
        await bot.delete_message(user_id, last_msg_id)
        
        last_msg = await bot.send_message(user_id, text, reply_markup=kb)
        last_msg_id = last_msg.message_id
        
        
        await state.update_data(key=f"{nextAskTaskId}:{user_id}:{last_msg_id}:{additionN}")


#Человек пытается ввести отсебятину, когда у него спрашивают "Во сколько?"
async def Already_clock_message_handler(message: types.Message, state: FSMAreYouLate):
    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    nextAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":")
    await bot.delete_message(user_id, last_msg_id)

    text = "Вы должны сначала ответить, во сколько вы пришли!"
    last_msg = await bot.send_message(message.from_user.id, text, reply_markup=await DialogClock().start_clock() )
    last_msg_id = last_msg.message_id
    await state.update_data(key=f"{nextAskTaskId}:{user_id}:{last_msg_id}:{addition}")



# Узнаем, что был до него
async def whoWasThere(query: types.CallbackQuery, state: FSMAreYouLate):
    "from_user_list"+f":{id}"
    
    answer_data, picked_id, picked_name = query.data.split(":") 
    fsmdata = await state.get_data() #Получаем информацию из ФСМ

    await bot.delete_message( query.message.chat.id, query.message.message_id )

    extAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":")
    addition = addition.replace(",",":")

    if picked_id == user_id:
        text = f"Значит, вы пришли в {addition}. И только вы можете это подтвердить? Удобно."    
    elif int(picked_id) != 0: 
        text = f"Значит, вы пришли в {addition}. И {picked_name} может это подтвердить?"
    else:
        text = f"Значит, вы пришли в {addition}. И никто не может этого подтвердить? Вы уверены?"
    await bot.send_message(user_id, text, reply_markup=inline_FSMAccept(f":{addition}:{picked_id}:{picked_name}"))



async def Already_confirm_answer( query: types.CallbackQuery, state: FSMAreYouLate):
    answer_data, answer, hh, mm, picked_id, picked_name = query.data.split(":") #inline_FSMAccept:no:10:55:1368534442:А'ртур

    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    nextAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":") 

    user = User(user_id)
    await bot.delete_message( query.message.chat.id, query.message.message_id )

    print("________", query.data)

    if answer == "yes":
        await state.finish()

        time = scheduled.getTime()

        user.startWork( time )
        text = """
        Вы указали информацию и она будет записана в логах. 
        Увы, вы не пометили начало работы и рабочий день будет рассчитываться с текущего момента.
        При необходимости, вы сможете запросить информацию, о не рассчитаном времени.
        Не забывайте вовремя помечать начало и конец рабочего дня."""
        await bot.send_message(user.getId(), text, reply_markup=inline_close_menu() )
        delete_task_byId( int(nextAskTaskId) )

        logId = insert_log("NotAtWork",f"Не отметился вовремя, но в {hh}:{mm} был на рабочем месте и {picked_name} может подтвердить это", time, user_id)

    else:
        await state.finish()
        delete_task_byId( nextAskTaskId )
        await WhyNotAtWork(user_id) # Спросить сразу же 

  
#######  ##YET##  #######  #######  #######  ##YET##  #######  #######  #######  ##YET##  #######
#######  #######  #######  #######  ##YET##  #######  #######  #######  ##YET##  #######  #######
#######  #######  ##YET##  #######  #######  #######  ##YET##  #######  #######  #######  #######
#######  #######  #######  ##YET##  #######  #######  #######  ##YET##  #######  #######  #######

      
@check_live_callback(True)
async def inline_late_Yet_callback_handler(query: types.CallbackQuery):
    user_id = query.message.chat.id
    nextAskTaskId = query.data.split(":")[1]

    await bot.delete_message( query.message.chat.id, query.message.message_id )

    text = """
    Почему вы еще не пришли? Напишите.
    """

    await FSMAreYouLate.WhyLate.set()

    last_msg = await bot.send_message(user_id, text)
    last_msg_id = last_msg.message_id
    state = Dispatcher.get_current().current_state(user=user_id)
    await state.update_data(key=f"{nextAskTaskId}:{user_id}:{last_msg_id}:0")


#Человек рассказывает, почему опоздал
async def Yet_message_handler(message: types.Message, state: FSMAreYouLate):
    user_answer = message.text
    user_id = message.from_user.id

    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    nextAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":") 
    await bot.delete_message( user_id, last_msg_id )

    await bot.delete_message( user_id, message.message_id )


    text = f"""
    На вопрос 'Почему вы не пришли, вы ответили:
    {user_answer}
    Верно?
    """
    last_msg = await bot.send_message(user_id, text, reply_markup=inline_FSMAccept(f":{nextAskTaskId}"))
    last_msg_id = last_msg.message_id

    await state.update_data(key=f"{user_answer}:{last_msg_id}")



async def Yet_confirm_answer( query: types.CallbackQuery, state: FSMAreYouLate):
    answer_data, answer, nextAskTaskId = query.data.split(":") #inline_FSMAccept:no

    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    user_answer, last_msg_id = fsmdata['key'].split(":") 
    user_id = query.from_user.id

    await bot.delete_message( user_id, last_msg_id )

    if answer == "yes":
        await state.finish()

        time = scheduled.getTime()

        text = """
            Ответ принят. Следующая проверка будет через 30 минут.
        Если вы придете раньше - просто поставте пометку "Начало работы"
        """
        await bot.send_message(user_id, text, reply_markup=inline_close_menu() )
        delete_task_byId( int(nextAskTaskId) )
        scheduled.create_reask_task(user_id,"0:checkAtWork", 30)

        logId = insert_log("NotAtWork",f"не пришел вовремя потому что: {user_answer}", time, user_id)

    else:
        await state.finish()
        delete_task_byId( nextAskTaskId )
        await WhyNotAtWork(user_id) # Спросить сразу же 


#######  NOT_NOW  #######  #######  #######  NOT_NOW  #######  #######  #######  NOT_NOW  #######
#######  #######  #######  #######  NOT_NOW  #######  #######  #######  NOT_NOW  #######  #######
#######  #######  NOT_NOW  #######  #######  #######  NOT_NOW  #######  #######  #######  #######
#######  #######  #######  NOT_NOW  #######  #######  #######  NOT_NOW  #######  #######  #######


@check_live_callback(True)
async def inline_late_NoToday_callback_handler(query: types.CallbackQuery):
    user_id = query.message.chat.id
    nextAskTaskId = query.data.split(":")[1]

    await bot.delete_message( query.message.chat.id, query.message.message_id )

    text = """
    Почему вы не придете?
    """

    await FSMAreYouLate.WhyNot.set()

    last_msg = await bot.send_message(user_id, text)
    last_msg_id = last_msg.message_id
    state = Dispatcher.get_current().current_state(user=user_id)
    await state.update_data(key=f"{nextAskTaskId}:{user_id}:{last_msg_id}:0")


#Человек рассказывает, почему опоздал
async def NoToday_message_handler(message: types.Message, state: FSMAreYouLate):
    user_answer = message.text
    user_id = message.from_user.id

    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    nextAskTaskId, user_id, last_msg_id, addition = fsmdata['key'].split(":") 
    
    await bot.delete_message( user_id, last_msg_id )
    await bot.delete_message( user_id, message.message_id )

    await state.update_data(key=user_answer)

    text = f"""
    На вопрос 'Почему вы не придете, вы ответили:
    {user_answer}
    Верно?
    """
    await bot.send_message(user_id, text, reply_markup=inline_FSMAccept(f":{nextAskTaskId}"))


async def NoToday_confirm_answer( query: types.CallbackQuery, state: FSMAreYouLate):
    answer_data, answer, nextAskTaskId = query.data.split(":") #inline_FSMAccept:no

    await bot.delete_message( query.message.chat.id, query.message.message_id )

    fsmdata = await state.get_data() #Получаем информацию из ФСМ
    print("fsmdata ",fsmdata)
    user_answer = fsmdata['key'].split(":") 
    user_id = query.from_user.id

    if answer == "yes":
        await state.finish()

        time = scheduled.getTime()

        text = """
            Ответ принят. Сегодня более вопросов не будет.
        Если вы придете - просто поставте пометку "Начало работы"
        """
        await bot.send_message(user_id, text, reply_markup=inline_close_menu() )
        delete_task_byId( int(nextAskTaskId) )

        logId = insert_log("NotAtWork",f"не придет потому что: {user_answer}", time, user_id)

    else:
        await state.finish()
        delete_task_byId( nextAskTaskId )
        await WhyNotAtWork(user_id) # Спросить сразу же 




# # ____ Таймер который отвечает за написание сообщений людям, которые не отметились вовремя (Выше)

def register_handlers_latecomers(dp: Dispatcher):

    dp.register_message_handler(test_handler, Text(equals="444", ignore_case=True)) #FOR TEST

    #Я уже пришел!!
    dp.register_callback_query_handler(inline_late_Already_callback_handler, text_contains='inline_late_Already' )
    dp.register_callback_query_handler(process_dialog_clock, clock_callback.filter(), state = FSMAreYouLate.WhenYouCome)
    dp.register_message_handler(Already_clock_message_handler, state = FSMAreYouLate.WhenYouCome)
    dp.register_callback_query_handler(whoWasThere, text_contains='from_user_list', state = FSMAreYouLate.WhenYouCome)
    dp.register_callback_query_handler(Already_confirm_answer, text_contains='inline_FSMAccept', state = FSMAreYouLate.WhenYouCome)

    #Я еще не пришел
    dp.register_callback_query_handler(inline_late_Yet_callback_handler, text_contains='inline_late_Yet' )
    dp.register_message_handler(Yet_message_handler, state = FSMAreYouLate.WhyLate)
    dp.register_callback_query_handler(Yet_confirm_answer, text_contains='inline_FSMAccept', state = FSMAreYouLate.WhyLate)

    #Меня сегодня не будет
    dp.register_callback_query_handler(inline_late_NoToday_callback_handler, text_contains='inline_late_NoToday' )
    dp.register_message_handler(NoToday_message_handler, state = FSMAreYouLate.WhyNot)
    dp.register_callback_query_handler(NoToday_confirm_answer, text_contains='inline_FSMAccept', state = FSMAreYouLate.WhyNot)

    
