"""
Регулирует запланированные задачи

Хранит формированный список задач в памяти
Загружает запланированные задачи из/в БД

Отвечаает за время (хранит актуальное время, выдает его в другие функции)
"""

from h_functions.tools import getStringedDate, getStringetWeekDay, getStringedTime, addTime

import time as ltime
from datetime import datetime

from creators.c_logger_create import logger as log
import calendar

from constants.config import GTM, SCHED_WORK_TIME_START, SCHED_WORK_DAYS, SCHED_TIME_ACTUAL, SCHED_TIME_REMOVE, SCHED_BOT_DAY_START_TIME, weekDaysEn

from database.bd_tasks_activity import insert_task, insert_result, delete_Old_tasks, delete_task_byId, select_task_byType_list,select_task_taskText

class Scheduled:
    dayToday = ""
    inBotTime = 0
    id_counter = 0

    def __init__(self, update_time, gtm, prev_days_count):
        self.update_time = update_time
        self.gtm = gtm
        self.prev_days_count = prev_days_count
        pass

    def getDate(self): return getStringedDate( self.getTime() )
    # def setDate(self, date): self.dayToday=date

    # def getTime_old(self): return self.inBotTime
    def getTime(self): return (int( ltime.time() ) + GTM)

    def markEveryDayTask(self):
        """ Вернет True, если она создалась """
        if getStringedTime( self.getTime() ) == SCHED_BOT_DAY_START_TIME:
            #Если сейчас время начала ежедневных задач
            bd_hasTask = select_task_taskText("1:everyDay_task")
            if bd_hasTask: #Если такая задача уже была
                return False
            else:
                text = "1:everyDay_task"
                forWho = "-:=:*"
                timeNow = self.getTime()
                removeTime = addTime( timeNow, hour=2 )
                insert_task(text, forWho, timeNow , remove_time=removeTime)
                return True
        else:
            return False


    def getWeekDayPosition(self):
        """ Вернет индекс текущего дня недели для строки типа '0:0:0:0:0:0:0' """
        return datetime.now().weekday()*2

    
    def getOldDay_old(self, year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,

    hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second,
    modYear = 0, modMonth=0, modDay=0, modHour=0, modMinute=0, modSecond=0, gtm=3): 
    #ПОЧИТАТЬ КАК ВРЕМЯ БУДЕТ В 5НОЧИ НЕ СПАВШИ НЕ МОГУ ОПРЕДЕЛИТЬСЯ

        second = int(second)+modSecond
        if second<0:
            for i in range(second, 0, +60):
                second = i
                modMinute -= 1
        elif second>59:
            for i in range(second, 59, -60):
                second = i
                modMinute += 1
        minute = int(minute)+modMinute
        if minute<0:
            for i in range(minute, 0, +60):
                minute = i
                modHour -= 1
        elif minute>59:
            for i in range(minute, 59, -60):
                minute = i
                modHour += 1
        hour = int(hour)+modHour+gtm
        if hour<0:
            for i in range(hour, 0, +24):
                hour = i
                modHour -= 1
        elif hour>23:
            for i in range(hour, 23, -24):
                hour = i
                modDay += 1

        year = int(year)+modYear
        month = int(month)+modMonth
        if month>12:
            for m in range(month, 12, -12):
                month = m
                year -=1
        elif month<1:
            for m in range (month,1, 12):
                month = m
                year += 1
        
        modMonth = 0
        modYear = 0

        moncal = calendar.monthcalendar(year, month)
        dayinMonth = 0
        for week in moncal:
            for dayw in week:
                if dayw==0: continue
                else: dayinMonth+=1

        print("days in month: ", dayinMonth)
        print("days in stoker (d, mod): ", day, modDay)


        day = int(day)+modDay
        if day>dayinMonth:
            needCorrect = True
            while needCorrect:
                day-=dayinMonth
                modMonth += 1

                print("err: mod, mon",modMonth, month)

                month = int(month)+modMonth
                modMonth = 0
                if month>12:
                    for m in range(month, 12, -12):
                        month = m
                        year -=1
                elif month<1:
                    for m in range (month, 1, 12):
                        month = m
                        year += 1

                moncal = calendar.monthcalendar(year, month)
                dayinMonth = 0
                for week in moncal:
                    for dayw in week:
                        dayinMonth+=1
                if day<dayinMonth: needCorrect=False
        if day<1:
            needCorrect = True
            while needCorrect:
                modMonth -= 1
                month = int(month)+modMonth
                modMonth = 0
                if month>12:
                    for m in range(month, 12, -12):
                        month = m
                        year -=1
                elif month<1:
                    for m in range (month, 1, 12):
                        month = m
                        year += 1

                moncal = calendar.monthcalendar(year, month)
                dayinMonth = 0
                for week in moncal:
                    for dayw in week:
                        dayinMonth+=1
                day += dayinMonth
                if day>0:
                    needCorrect = False

        print(year, month, day, hour, minute, second)
        return int( datetime( year, month, day, hour, minute, second).timestamp() )


    def getOldDay(self, year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
        hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second,
        modYear = 0, modMonth=0, modDay=0, modHour=0, modMinute=0, modSecond=0, gtm=3): 

        year += modYear
        pd = int( datetime( year, month, day, hour, minute, second).timestamp() )

        lminute = 60
        lhour = 3600
        lday = 86400
        lmonth = 2629743

        modHour+=gtm

        pd += modSecond
        pd += modMinute*lminute
        pd += modHour*lhour
        pd += modDay*lday
        pd += modMonth*lmonth

        return pd


    def create_reask_task(self, telegram_id, task_text, actualMinute=20):
        text = task_text
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        actualTime = self.getOldDay( minute=actualMinute)
        removeTime = addTime( actualTime, minute=SCHED_TIME_REMOVE )
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)
        return id


    def create_CheckTask_startInTime(self, telegram_id, startTime):
        """ Создает задачу, проверять, пришел ли вовремя работник в этот день\nstartTime 'HH:MM' """
        text = "0:checkAtWork"
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        # actualTime = addTime( timeNow, minute=SCHED_TIME_ACTUAL) #Каждые 20минут будет задача повторяться (точнее когда время наступит, она исполнится удалив эту задачу и создав новую)
        h,m = ( int(time) for time in startTime.split(":") )
        # actualTime = int( datetime(hour=h, minute=m) ) + GTM
        actualTime = self.getOldDay( hour=h, minute=m)
        removeTime = addTime( actualTime, minute=SCHED_TIME_REMOVE )
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)
        print("time", self.getTime(), actualTime) 
        return id


    def create_CheckTask_needEcho(self, telegram_id, hour=18, minute=0):
        """ Создает задачу, проверять, появлялся ли человек (В 18:00)"""
        text = "0:checkEcho"
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        # actualTime = int( datetime(hour=18 ) ) + GTM
        actualTime = self.getOldDay( hour=hour, minute=minute) #
        removeTime = addTime( actualTime, minute=SCHED_TIME_REMOVE )
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)
        return id


    def create_CheckTask_noOverheat(self, telegram_id):
        """ Создает задачу, проверять, не перерабатывает ли человек \n
        актуальное время = 30минут"""
        text = "0:checkOverheat"
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        actualTime = addTime( timeNow, minute=30 ) 
        removeTime = addTime( actualTime, minute=SCHED_TIME_REMOVE )
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)
        return id


    def create_CheckTask_noFogetClose(self, telegram_id, timer):
        """ Создает задачу, проверять, не забыл ли выключить таймер \n
        актуальное время = 30минут"""
        text = f"0:noFogetClose.{timer}"
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        actualTime = addTime( timeNow, minute=30 ) 
        removeTime = addTime( actualTime, minute=SCHED_TIME_REMOVE )
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)
        return id
    


    def createStartWorkAsk(self, telegram_id):
        """ Если человека нет на работе, создает задачу '0:WhyNotAtWork' , возвращает ИД задачи """

        #Если компания инициализировало вопрос к работнику (Т.е. узнала, что его в нужное время нет на месте)

        text = "0:whyNotAtWork"
        forWho = f"1:+:{telegram_id}"
        timeNow = self.getTime()
        actualTime = addTime( timeNow, minute=SCHED_TIME_ACTUAL) #Каждые 20минут будет задача повторяться (точнее когда время наступит, она исполнится удалив эту задачу и создав новую)
        removeTime = addTime( timeNow, hour=SCHED_TIME_REMOVE )
        
        id = insert_task(text, forWho, timeNow , remove_time=removeTime, actual_time=actualTime)

        return id

        




    # def getDate_old(self): 
    #     if self.dayToday in ("",None): log.warn("Scheduled:getDate: Дата не указана")
    #     return self.dayToday


    

    # def setTime(self, time): 
    #     """ Меняет и дату"""
    #     self.inBotTime=time
    #     self.dayToday=getStringedDate(time)

    # def setStatus(self, task_id, status):
    #     self.tasks[task_id].setStatus(status)

    # def getTHDates(self, days=-1):
    #     """Возвращает list даты из суток от тек.момента (сегодня+вчера..) с поправкой на gtm из конфига\n
    #     Если days оставить по-умолчанию или -1, то выберется расстояние из конфига """
    #     day_len_sec = 86400
    #     _days = days if days<1 else self.prev_days_count
    #     dayList = []
    #     for i in range(_days):
    #         day = getStringedDate( self.getTime() -(i*day_len_sec) )
    #         dayList.append(day)

    #     return dayList

    def getUpdateTime(self):
        """Возвращает глобальную переменную в которой хранится время, через которое нужно """
        return self.update_time

    def getGTM(self): return self.gtm

    def delete_Old_tasks(self):
        delete_Old_tasks( self.getTime() ) #Удаляет устаревшие задачи

    # def update(self):
    #     """ Обновляет время, перебирает задачи \n
    #     возвращает списки задач, на которые нужны ответы пользователя?
    #     """
    #     self.setTime( int( ltime.time() ) + GTM )




