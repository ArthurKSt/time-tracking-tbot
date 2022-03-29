from aiogram.utils import executor

from constants.config import SCHED_UPDTIME

from creators.c_bot_create import dp
from creators.c_company_create import company
from creators.c_logger_create import logger
from creators.c_scheduled_create import scheduled

from h_functions import timer # Для цикла

from handlers import other, worker, auth, admin, time_record, latecomers, menu, test_calendar

test_calendar.register_handlers_test_calendar(dp)
admin.register_handlers_admin(dp) #Админские фишки (устарело)
auth.register_handlers_auth(dp) #Авторизация в группу
time_record.register_handlers_time_record(dp) #Учет времени
menu.register_handlers_menu(dp) #действия из меню
worker.register_handlers_worker(dp) #Команды работника (устарело)
latecomers.register_handlers_latecomers(dp) #Команды при опоздании
other.register_handlers_other(dp) #Стандартные сообщения типо Эхо и Старт


import asyncio





async def func_scheduled(wait_for): # Циклично проходится по задачам планировщика
  while True:
    await asyncio.sleep(wait_for)

    # company.reloadWorkersFromBD()


    # scheduled.update()

    # scheduled.delete_Old_tasks()

    # await getExTable(1)

    #print("who not started: ", company.getWorkersNotAtWorkID())

    #Раз уж задача "проверить кто на месте сегодня" выполняется только раз, то можно в ее теле выполнять все действия, которые должны выполняться в начале дня
    #Типо поиск устаревших записей и их удаление
    #Сброс гостей, которых не подтвердили 

    # Обрабатывает случаи в целом, кто из всей компании не пришел
    # Далее создается позадача для каждого отдельного человека, узнать почему не пришел и сохранить ответы конкретного человека
    # if scheduled.checkStartWorkTask(): #Если задача "Проверить кто не пришел" начата (сама контролирует только 1 запуск)
    #   #print("___TasK Created")
    #   for id in company.getWorkersNotAtWorkID(): # Получаем список людей кто не пришел вовремя (кто не отметился как "пришел на работу")
    #     scheduled.createStartWorkAsk(id)

    # спрашиваем, почему не пришел (Там инлайн кнопка и/или машина состояний через которую можно отчитаться)
    # варианты: Скоро буду, отчитаться, меня сегодня не будет, уже пришел(забыл нажать), не ответил

    # await 

    #await timer.do_task() # Обрабатывает задачи

  #До какого-то время циклично будет спрашивать всех, кто еще не пришел "Почему не пришел?"
  # await timer.timer_Why_Not_At_Work(1368534442)

  # for workerId in company.getWorkersId():
  #   #await timer_hello(workerId)
  #   #await timer_workStart(company, workerId)
  #   #await timer.timer_workStart_IKB(company, workerId) # Спамит сообщениями всем, кто
  #   pass

  #Перебираем созданные задачи (берем 1, выполняем, удаляем, записываем заново если не выполнилась)
  # bd_tasks


  """
  Узнать время
  Если время более 9 и работник не на работе, создать задачу "писать пока не ответит"

  """


def bot_start():
  # scheduled.update()

  loop = asyncio.get_event_loop() #(600))  # Таймер который выполняется каждые 10минут
  loop.create_task(func_scheduled( SCHED_UPDTIME ) )#scheduled.getUpdateTime() )) #Запустить таймер на каждые N секунд (Начинает выполнять запланированные задачи)


  executor.start_polling(dp, skip_updates=True)



if __name__ == '__main__':
  bot_start()

