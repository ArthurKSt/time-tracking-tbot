
# from constants.privileges import PRIVILEGES


from database.bd_user_activity import insert_user, update_user_name, select_from_users_ByMaxMinLevel, select_user, select_userId_byName #, update_user_permission
from database.bd_user_time_activity import insert_day, select_day_info
from database.bd_log_activity import select_log_byDateAndId
from database.bd_user_group_activity import select_user_weight, select_userId_list_round

from h_functions.tools import getStringedDate, getStringedTime

from creators.c_scheduled_create import scheduled as scheduled_tasks
from creators.c_logger_create import logger as log

# from decorators.d_check_params_decorator import check_parms

from Classes.TimerPoint import TimerPoint

from Classes.UHash import _UHash, uhash






acceptedNameSymb = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMйцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮёЁ "


class User:

    # Выполняется инициализация только 1 раз
    def __init__(self, telegram_id, name= "", _date=""):#, permission=0):
        """ При инициализации пользователь ищется в БД, если его нет, то создается запись с нулевыпи правами"""
        # self.permission = permission
        self.name = name
        self.telegram_id = telegram_id
        self.__date = _date

        _UHash.s_create( self.telegram_id )

        bd = select_user(telegram_id) #Запрос данных из БД по пользователю
        if bd: #result = 0teleg_id INTEGER, 1teleg_name TEXT, 2level INTEGER, 3at_work INTEGER, 4needs_notification TEXT
            # log.info("User, __init__, user {}:{}".format(telegram_id, name))
            # self.permission=bd[2]
            self.name = bd[1]
            # self.inWorkStatus = bd[3]
            # self.needsNotification = bd[4]


            print("Init self date = " ,self.getDate() )

            


            bd = select_day_info( self.getDate() , telegram_id) #Запрос данных из БД по пользователю И дате
            if not bd: #0post_id 1teleg_id 2date 3id_come_time 4id_leave_time
                insert_day( self.getDate() , self.telegram_id)


        else: #Если пользователя не было в базе данных с 0уровнем
            log.info("User, __init__, unknown user {}:{}".format(telegram_id, name))

            insert_user(telegram_id, name) #Добавляется в бд с 0уровнем
            self.rename(name)

            bd = select_user(telegram_id)

            self.telegram_id = bd[0]
            self.name = bd[1]

    def getDate(self):
        if self.__date == "":
            return scheduled_tasks.getDate()  
        else: 
            return self.__date


    def do(self):
        """ Когда выполняется любое действие, ведет счетчик\n
        Вернет False если действие заперещено"""
        hash = _UHash.s_get( self.telegram_id )
        return hash.do()

    def s_check_name(name):
        newName = ""
        for s in name:
            if s in acceptedNameSymb:
                newName += s

        if len(newName)<5:
            newName = "Рядовой " + newName

        return newName[0].upper()+newName[1:]

    def s_checkInBd_name(name:str):
        bd = select_userId_byName(name)
        if bd:
            now_count = 1
            for count in name.split("I"):
                now_count +=1

            if now_count > 1:
                base,trash = name.split("-")

            name = base + "-" + "I"*now_count
            name = User.s_checkInBd_name(name)

        return name
            



    def rename(self, name):
        name = User.s_check_name(name) #Убираем лишние символы
        name = User.s_checkInBd_name(name) #Проверяем в бд
        update_user_name(self.telegram_id, name)
        self.setName(name)

    def update(self): #при любом действии с пользователем выполняется
        self._upd_user()
        # self._upd_day_info()

    def _upd_user(self):
        bd = select_user(self.getId())
        if bd: #result = 0teleg_id INTEGER, 1teleg_name TEXT, 2level INTEGER, 3at_work INTEGER, 4needs_notification TEXT
            # self.permission=bd[2]
            self.name = bd[1]
        else: log.warn("User:_upd_user: Не удалось загрузить информацию")
        

    # def setPermission(self, permission): 
    #     update_user_permission(self.getId(), permission) #Меняем права в БД
    #     self.permission = permission
    #     self.update()

    # def getPermission(self): return self.permission

    def getPermList(self, now=False): 
        hash = _UHash.s_get( self.telegram_id )
        return hash.getPermsList(now)

    # def getWeight(self):
    #     hash = _UHash.s_get( self.telegram_id )
    #     return hash.getWeight()

    def getWeight(self):
        return select_user_weight(self.telegram_id)

    def getLowerWorkers(self):
        return select_userId_list_round(minW=2, betterId=self.telegram_id, onlyLower=True)


    def setName(self, name): self.name = name
    def getName(self): return self.name

    def getId(self): return self.telegram_id

    def isAtWork(self):
        wtp = self.getTimePoint("work")
        return not wtp.isTimerEnded()

    def s_getWorkers(req_level=1):
        return select_from_users_ByMaxMinLevel(req_level, 1)

    def s_getWorkersNotAtWork(req_level=1):
        """req level уровень того, кто вызвал 1 по умолчанию"""
        ids = []
        
        for worker in User.s_getWorkers(req_level):
            usr = User(worker[0],worker[1],worker[2])
            if not usr.isAtWork(): ids.append( usr.getId() )

        return ids

    def hasPermission(self, command: str): # Проверяет, есть ли права на выполнении команды в зависимости от прав
        hash = _UHash.s_get( self.telegram_id )
        return command in hash.getPermsList()


    def __str__(self):
        user_str = "\n\n---___---\nUser: "
        user_str += f"\n{self.telegram_id}: {self.name}"
        # user_str += f"\npermission: {self.permission}"
        # user_str += f"\nstart: {self.timeStartId}"
        # user_str += f"\nend: {self.timeEndId}\n___---___\n"
        return user_str


    def getLastPressedTimerPointTime_s(self, date, cause, dir="s", causeId=0 ):
        """ 
        Возвращает строку ЧЧ:ММ если данные есть, иначе NONE \n AlterFor workStart\End
        table = come/ leave"""

        tp = self.getTimePoint(date, cause)
        return tp.getTime_s(dir, causeId)


    def getLastPressedStartTime_s(self):
        """ получить время начала (от последнего нажатия)"""
        schdate = self.getDate() 
        return self.getLastPressedTimerPointTime_s(schdate, "work", "s")

    def getLastPressedEndTime_s(self):
        """ получить время начала (от последнего нажатия)"""
        schdate = self.getDate() 
        return self.getLastPressedTimerPointTime_s(schdate, "work", "e")
        

    def getDayId(self):
        schdate = self.getDate() 

        day_bd = select_day_info(schdate, self.telegram_id) #Получаем запись про день
        if not day_bd: 
            day_id = insert_day(schdate, self.telegram_id) #Создаем ее, если ее нет
        else:
            day_id = day_bd[0]
        
        return day_id


    def getTimePoint(self, cause):
        return TimerPoint( self.getDayId() , cause)

    def getWhenStart(self):
        return getStringedTime( self.getTimePoint("work").firstJoin() )

    def getWhenEnd(self):
        return  getStringedTime( self.getTimePoint("work").lastEnd() )


    
    def getStatusSetterKeys(self):
        """ Используется для создания клавиатуры"""
        return TimerPoint.s_getAction( self.getDayId() )


    def setTimerPoint(self, time, cause, timePos, causePos= 0):
        """ Записывает в БД время \n
        time = время либо utime либо str "HH:MM"\n
        cause = код/название/причина таймера\n
        timePos = положение точки внутри таймера s=начало, e=конец\n
        causePos = положение таймера, -1 - создать новый, 0- исп. последний, число - исп указанный\n
        """
        schdate = self.getDate() 
        date = getStringedDate(time) # Конвертируем udate в строку для бд

        msg = ""

        if date != schdate:
            msg += "Попытка поменять дату прошедших дней"
            log.warn("User:setTimerPoint: "+msg)
            return 0

        wp = self.getTimePoint( cause)
        timeId = wp.putTime(time, timePos, causePos)

        return timeId

    def startWork(self, time):
        """ Используется для телеграмм фреймворка, возвращает ИД новой записи"""
        return self.setTimerPoint(time, "work", "s")

    def endWork(self, time):
        """ Используется для телеграмм фреймворка, возвращает ИД новой записи"""
        return self.setTimerPoint(time, "work", "e")


    def getTimePointInfo(self, cause):
        """
        Вытягиваем из причины список задействованных точек
        return (cause, [[utime,utime],..])
        """
        intervals = self.getTimePoint(cause).getUtimeIntervals()#.getTimeIntervals()

        return intervals

    def getWorkedTime(self):
        """ Вернет строку типа 3ч. 11м"""
        workedSec = TimerPoint.s_getWorkedTime( self.getDayId() )
        return getStringedTime(workedSec, addHM=True)

    def getLogList(self):
        """ return (count_lines, ( log ) ) \n
    logResultFull = [ logNote[2], logNote[4], *fromAdditionResult ] #Сохраняем текст, время лога и список дополнений с текстом и временем дополнения """
        log = select_log_byDateAndId( self.getDate(), self.telegram_id, 30 )
        return log

    def getLogCount(self):
        """ return (count_lines, ( log ) ) \n
    logResultFull = [ logNote[2], logNote[4], *fromAdditionResult ] #Сохраняем текст, время лога и список дополнений с текстом и временем дополнения """
        log = select_log_byDateAndId( self.getDate(), self.telegram_id, 30 )
        return log[0]


    def getDayInfo(self):


        strInfow = "Вы сегодня работали:\n"

        wktimes = self.getTimePointInfo("work")

        for t in wktimes:
            strInfow += f"\tС { getStringedTime(t[0]) } по {getStringedTime(t[1])}\n"

        strInfo = ""

        if strInfow!="Вы сегодня работали:\n":
            strInfo = strInfow

            strInfof = "\nВы сегодня брали перерывы:\n"

            frtimes = self.getTimePointInfo("free")
            for t in frtimes:
                strInfof += f"\tС { getStringedTime(t[0]) } по {getStringedTime(t[1])}\n"

            if strInfof!="\nВы сегодня брали перерывы:\n":
                strInfo += strInfof

            strInfo += ""
            workedSec = TimerPoint.s_getWorkedTime( self.getDayId() )
            strInfo += f"\nВы проработали: { getStringedTime(workedSec, addHM=True) }"

        else: strInfo = "Вы еще не начинали сегодня."
        
        return strInfo


