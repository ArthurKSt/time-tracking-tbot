#from store.bd_user_activity import insert_time_by_table_name, select_day_info_byID, select_timePoint_byDayID_and_Cause, insert_timePoint_by_table_name,\
#    select_time_byID, update_timePoint_time_byPos

from curses.ascii import isxdigit
from database.bd_user_time_activity import insert_time_by_table_name, select_time_byID, select_day_info_byID, select_timePoint_byDayID_and_Cause,\
    insert_timePoint_by_table_name, update_timePoint_time_byPos

from creators.c_logger_create import logger
from creators.c_scheduled_create import scheduled

from h_functions.tools import getStringedTime, getUTimeFromStringTime

MIN_ROUND = 1 * 60



"""
Этот класс нужен для подсчета времени между точками,
вывода времени и записи
"""
class _Time:
    def __init__(self, id_time, pos="s"):
        """ pos = position in time interval (s=start, e=end)"""
        self.id_time = id_time

        if not (pos in "se"):
            self.pos = "s"
            logger.warn("TimerPoint:_time: init: Не правильный вектор времени")
        else:
            self.pos = pos

        self.time = 0


    def bd_load(self):
        bd_time = select_time_byID(self.id_time)

        if bd_time: # Если время по указанному айди нашлось
            self.time = bd_time[4]
        elif self.pos == "e": # Если запрашиваемое время - является концом интервала и оно еще не установлено, то получаем текущее время
            self.time = scheduled.getTime() 
        else: self.time == 0

    def getDirect(self): return self.pos

    # Get
    def getTime_str(self):
        self.bd_load() #Перед получением, загружаем время

        return getStringedTime( self.time ) if self.time != 0 else "Не указано"

    def getTime_utime(self) -> int:
        """return utime or 0 (0 - is nothing)"""
        self.bd_load()
        return self.time

    # Set
    def setTime_utime(self, utime, day_id, timePoint_id):
        """ записывает время из utime\n
        in: strtime, day_id, timePoint_id \n
        return post_id"""
        
        self.time = utime
        self.id_time = insert_time_by_table_name(day_id, timePoint_id, utime, self.getDirect())
        return self.id_time

    def setTime_strtime(self, strtime, day_id, timePoint_id):
        """ Записывает время из строки типа ЧЧ:ММ\n
        in: strtime, day_id, timePoint_id \n
        return post_id"""
        utime = getUTimeFromStringTime(strtime)
        self.setTime_utime( utime, day_id, timePoint_id )
        return self.id_time

    #Static Set
    def s_setTime_utime( utime, day_id, timePoint_id, direction):
        """ Static записывает время из utime return time_di\n
        in: strtime, day_id, timePoint_id, direction \n
        return post_id"""
        return insert_time_by_table_name(day_id, timePoint_id, utime, direction)

    def s_setTime_strtime( strtime, day_id, timePoint_id, direction):
        """ Static Записывает время из строки типа ЧЧ:ММ return time_di\n
        in: strtime, day_id, timePoint_id, direction \n
        return post_id"""
        utime = getUTimeFromStringTime(strtime)
        return _Time.s_setTime_utime( utime, day_id, timePoint_id, direction )

    def __str__(self):
        return self.getTime_str()




class TimerPoint:
    """ Обработака времени между точками
    Создается из записи дня(в которой уже есть пользователь и дата)"""

    """
    Ф-я вызывающаяся под конец дня
    если есть таймеры, то завершить их
    оповестить человека, что сутки закончены и перечислить какие таймеры выключены
    оповестить какие таймеры запустятся в ноыве сутки

    после начала новых суток
    создать заново
    оповестить какие таймеры запущены
    """

    """
    реализация Манипуляции с таймером одной-двумя кнопкой.

    нужно знать какая сейчас задача активна, то есть получить данные
    что нажато последним

    1)запрос в БД за сегодня что нажато в free, work
    получить самое большее время из полученных и узнать его "причину" и "положение"
        у нас может быть:
            Человек еще ничего не нажимил (работа не начата, перерыв невозможен)
                Доступна кнопка "начать" - создает новый интервал

            человек нажал начать рабочий день...
                доступны кнопки "Закончить" и "Перерыв" - закончить интервал или создать интервал "перерыв"

                человек нажал закончить
                    доступны кнопка "начать" - создает новый интервал

                человек нажал "перерыв"
                    доступна кнопка "вернуться к работе" - заканчивает интервал перерыв
    """


    def __init__(self, day_id, cause:str):
        """ Перед созданием точки времени нужно убедиться, что такой день есть!! """
        
        self.day_id = day_id
        self.cause = cause # Название причины таймера (рабочий таймер, обеденный таймер, учет времени на задачу)
        self.timeIntervals = {} # Здесь хранится словарь Ид отрезка (начало ид, конец ид)

        self.bd_load(day_id, cause)

    
    def isTimerEnded(self):
        """ Вернет True если таймер закончен или не начат"""
        tp_bd = select_timePoint_byDayID_and_Cause(self.day_id, self.cause ,1)

        if tp_bd: #Если  есть такая запись
            if tp_bd[0][3]==0: #Если еще не закончено
                return False
            
            else:
                return True
        
        else:
            return True

    def firstJoin(self):
        """ Вернет время первого начала таймера или False"""
        tp_bd = select_timePoint_byDayID_and_Cause(self.day_id, self.cause ,1, invert=False )

        if tp_bd:
            timeId = tp_bd[0][2]

            if timeId == 0: # Если время не задано
                return False

            else:
                time = _Time(timeId).getTime_utime()
                return time

        else: return False

    def lastEnd(self):
        """ Вернет время последнего завершения таймера или False (Даже если таймер еще идет = False) """
        tp_bd = select_timePoint_byDayID_and_Cause(self.day_id, self.cause ,1, invert=True )

        if tp_bd:
            timeId = tp_bd[0][3]

            if timeId == 0: # Если время не задано
                return False

            else:
                time = _Time(timeId).getTime_utime()
                return time

        else: return False


    def s_getAction(day_id):
        """ Static \n
        Получает доступные следующие действия с их праметрами\n
        return  [ ["cause", "pos", causemod],[...],... ] \n
        for (method) putTime: (time: Any, pos: str = "s", causeId: int = 0) """


        wtp_bd = select_timePoint_byDayID_and_Cause(day_id, "work",2) # Хранит в себе список из временных интервалов (0 - самое последнее, 1-предпоследнее...)
        # Хранит в себе список из временных интервалов


        if not wtp_bd: #Если записи нет, то след кнопка "Начать работать"
            return [ ["work", "s", 0], ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

        else:
            if wtp_bd[0][3] != 0: #Если рабочий таймер завершен, то след кнопка "Начать работать"
                return [ ["work", "s", -1], ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

            else:

                if wtp_bd[0][2] == 0: # Если начало нет, то "Начать работать"
                    return  [ ["work", "s", 0], ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

                else:
                    # Проверка на ( Закончить перерыв или Закончить работу и Начать перерыв)?
                    ftp_bd = select_timePoint_byDayID_and_Cause(day_id, "free",2)
 
                    if not ftp_bd: # Если записей о перерывах нет, то даем возможность начать перерыв
                        return [ ["free", "s", 0], ["work", "e", 0] ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

                    else:

                        if ftp_bd[0][3] != 0: #Если последний перерыв был завершен
                            return [ ["free", "s", -1], ["work", "e", 0] ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

                        else:
                            if ftp_bd[0][2] == 0: # Если последний перерыв не был начат
                                return [ ["free", "s", 0], ["work", "e", 0] ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )
                            
                            else: # Если у перерыва было начало, но не было конца
                                return [ ["free", "e", 0],]

                                #Получить время начала перерыва и начала рабочего времени
                                # freeStartTime = _Time( ftp_bd[0][2], "s" ).getTime_utime()
                                # workStartTime = _Time( wtp_bd[0][2], "s" ).getTime_utime()

                                # if freeStartTime<workStartTime: # Если последний перерыв начался до работы, то не считается
                                #     return [ ["free", "s", -1], ["work", "e", 0] ] # Начать(e=закончить) рабочий таймер в новую ячейку (0 = в существующую )

                                # else:
                                #     return [ ["free", "e", 0],]
                            


    def bd_load(self, day_id, cause):
        self.timeIntervals = {}

        bd_dayInfo = select_day_info_byID(day_id) # Получить запись о дне по иду
        if bd_dayInfo: # Если такаяие записьи есть

            bd_cause = select_timePoint_byDayID_and_Cause(day_id, cause, howMany=40, invert=False) # Получаем записи на дату
            if bd_cause: # Если записи нашлись

                for cause in bd_cause:
                    #каждый каус - это один отрезок с началом и концом во времени дня для какого-то события
                    self.timeIntervals[ cause[0] ] = [ cause[2], cause[3] ] #Записываем в словарь. Ключ - ид отрезка, а значение - лист с идом начала и конца


            else: # Если поступил запрос на получение данных, а таблички нет - то ее надо создаьт
                rId = insert_timePoint_by_table_name(day_id, cause)
                self.timeIntervals[ rId ] = [ 0, 0 ]

        else: # Если записи дня у пользователя нет, то в лог записать ошибку о том, что нет записи дня (а должна быть)
            logger.warn("TimerPoint:bd_load: не удалось пролучить запись дня")
            pass

    def getUtimeIntervals(self):
        _intervals = []

        for time in self.timeIntervals.values():

            if time[0] == 0: continue

            start = _Time(time[0], "s").getTime_utime()
            end = _Time(time[1], "e").getTime_utime()

            _intervals.append( [start, end] )
        
        return _intervals

    # def s_intervals_sum(list_intervalsA, list_intervalsB):
    #     """ A + B \n lists is [[startUtime, endUtime, ],[..],..]"""

    #     crosses = []
    #     onlyA = []
    #     onlyB = []

    #     AllintA = list(list_intervalsA)
    #     AllintB = list(list_intervalsB)

    #     for intA in AllintA:
    #         AS = intA[0]
    #         AE = intA[1]

    #         for intB in AllintB:
    #             BS = intB[0]
    #             BE = intB[1]

    #             if AS>=BS: #456

    #                 if AS>=BE: #4 Не соприкасаются
    #                     pass

    #                 else: #56

    #                     if AE>=BE:#5 А начался до того как закончился Б
    #                         pass
    #                     else:#6 А находится посередине Б
    #                         pass

    #             else: #123

    #                 if AE<=BS: #1 Не соприкасаются
    #                     pass
    #                 else: #23

    #                     if AE>=BE: #3 А делится пополам Б (б находится посередине А)
    #                         pass
    #                     else: #2 А закончился после того как начился Б
    #                         pass

    #     return

    def s_intervals_sub(list_intervalsA, list_intervalsB):
        """ A - B \n lists is [[startUtime, endUtime, ],[..],..]"""

        #print("\n\n___ Intervals ____")


        AllintA = list(list_intervalsA)
        AllintB = list(list_intervalsB)

        for intA in AllintA:
            AS = intA[0]
            AE = intA[1]

            if AS==0 or AE==0: continue # Пропускаем пустые

            for intB in AllintB:
                BS = intB[0]
                BE = intB[1]

                if BS==0 or BE==0: continue # Пропускаем пустые

                if AS>=BS: #456
                    if AS>=BE: #4 Не соприкасаются
                        continue #Ничего не меняем

                    else: #56
                        if AE>=BE:#5 А начался до того как закончился Б (Нужно вырезать из А-Б)
                            intA[0] = intB[1] #Перемещаем начало А в конец Б
                            continue

                        else:#6 А находится посередине Б
                            #Удаляем эту запись (запишем в нее нули и отчистим их, при выходе)
                            intA[0] = 0
                            intA[1] = 0
                            continue

                else: #123
                    if AE<=BS: #1 Не соприкасаются
                        continue #Ничего не меняем

                    else: #23
                        if AE>=BE: #3 А делится пополам Б (б находится посередине А)
                            AllintA.append( [ intB[1], intA[1] ] ) #Сначала добавляем новый промяжуток (от конца Б до конца А)
                            intA[1] = intB[0] #Потом меняем конец уже существующего А на начало Б
                            continue
                        else: #2 А закончился после того как начился Б
                            intA[1] = intB[0]
                            continue
        
        #print("Count boids: ", AllintA.count([0,0]))
        for i in range(AllintA.count([0,0])):
            #print("")
            AllintA.remove( [0,0] )

        
        #print("\n--- Intervals ---\n")

        return AllintA


    # def getTimeIntervals(self, sec_round = MIN_ROUND): # Перед выдачей получить время, объединить пересечения
    #     """ получает список [[начало, конец],] объединенные на пересечениях сглаженое по указ.секундам\n
    #     сглаживание по-умолчанию равно 10минутам"""
    #     _intervals = []

    #     notSorted = list(self.timeIntervals.values())

    #     for item in notSorted:
    #         if item[0] == 0: continue

    #         strN = _Time(item[0], "s").getTime_utime()
    #         endN = _Time(item[1], "e").getTime_utime()

    #         if not _intervals: _intervals.append( [strN, endN] )
    #         else:

    #             for _interval in _intervals:
    #                 strO = _interval[0]
    #                 endO = _interval[1]

    #                 if strO>strN: #235

    #                     if strO<endN: #2 (не пересекаются, старая запись началась после конца новой)
    #                         _intervals.append( [strN, endN] )
    #                         pass

    #                     else: #35
    #                         if endO>strN: #3 ( старая запись заканчивается после начала новой)
    #                             _interval[0]=strN
    #                             _interval[1]=endO
                                
    #                             pass

    #                         else: #5 (старая запись полностью перекрывает новую )
    #                             _interval[0]=strN
    #                             _interval[1]=endN

    #                             pass

    #                 else: #146

    #                     if endO<strN: #4 (не пересекаются, старая запись закончилсь до начала новой)
    #                         _intervals.append( [strN, endN] )
    #                         pass

    #                     else: #14
    #                         if endO > endN: #6 (новая запись делит старую на две части)
    #                             _interval[0]=strO
    #                             _interval[1]=endO

    #                             pass

    #                         else: #1 (новая запись началась до конца старой)
    #                             _interval[0]=strO
    #                             _interval[1]=endN
    #                             pass



        

        # for key, interval in self.timeIntervals.items(): #интервал будет списком с идом начала и конца
        #     start = _Time(interval[0], "s")
        #     end = _Time(interval[1], "e")

        #     startTime = start.getTime_utime()
        #     endTime = end.getTime_utime()

        #     # if interval[0] == 0 and interval[1] == 0: #Если записи пустые
        #     #     continue
            
        #     # if _intervals:

        #     #     used = False

        #     #     for has in _intervals:

        #     #         if has[1] > startTime:
        #     #             if has[0] < endTime:
        #     #                 has[1] = endTime
        #     #                 used = True

        #     #         if has[0] < endTime:
        #     #             if has[1] > startTime:
        #     #                 has[0] = startTime
        #     #                 used = True

                    
        #     #         if not used: 
        #     #             _intervals.append( [startTime,endTime] )
        #     #             used = True
            
        #     # else:
        #     #     _intervals.append( [startTime,endTime] )

        # return _intervals

    # def getTime(self):
    #     """ Возвращает время(сек), сколько таймеры в целом отсчитали времени на указаный тип\n
    #     Не подходит для подсчета рабочего времени!"""
    #     allTime = 0

    #     times = self.getTimeIntervals()
    #     for t in times:
    #         allTime += t

    def s_getWorkedTime(day_id):
        """ Статический метод. \nПолучает проработанное время(сек) из Ида Дня\n
        по-умолчанию округляет временные промяжутки"""

        workedSeconds = 0

        worked = TimerPoint(day_id, "work")
        free = TimerPoint(day_id, "free")

        wi = worked.getUtimeIntervals()
        fi = free.getUtimeIntervals()

        workTime = TimerPoint.s_intervals_sub(wi,fi)
        for intw in workTime:
            workedSeconds += (intw[1] - intw[0])

        return workedSeconds

        

    # def s_getWorkedTime(day_id, sec_round = MIN_ROUND):
    #     """ Статический метод. \nПолучает проработанное время(сек) из Ида Дня\n
    #     по-умолчанию округляет временные промяжутки"""
        
    #     worked = TimerPoint(day_id, "work")
    #     free = TimerPoint(day_id, "free")

    #     wtime = worked.getTimeIntervals()
    #     ftime = free.getTimeIntervals()

    #     work_intervals = []

    #     for w in wtime:

    #         work_intervals.append(w)

    #         for alr in work_intervals:
    #             strO = alr[0]
    #             endO = alr[1]

    #             for f in ftime:
    #                 strN = f[0]
    #                 endN = f[1]

    #                 if strO>strN: #235

    #                     if strO<endN: #2 (не пересекаются, старая запись началась после конца новой) 
    #                         pass

    #                     else: #35
    #                         if endO>strN: #3 ( старая запись начинается перед концом новой) 
    #                             alr[0] = endN
    #                             alr[1] = endO
    #                             pass

    #                         else: #5 (старая запись полностью перекрывает новую ) 
    #                             alr[0] = 0
    #                             alr[1] = 0
    #                             pass

    #                 else: #146

    #                     if endO<strN: #4 (не пересекаются, старая запись закончилсь до начала новой) 
    #                         pass

    #                     else: #14
    #                         if endO > endN: #6 (новая запись делит старую на две части) 
    #                             alr[0] = strO
    #                             alr[1] = strN

    #                             work_intervals.append( [endN, endO] )
    #                             pass

    #                         else: #1 (новая запись началась до конца старой) 
    #                             alr[0] = strO
    #                             alr[1] = strN
    #                             pass

    #     hours_worked = 0
    #     for wint in work_intervals:
    #         hours_worked += ( wint[1] - wint[0] )



    #     #print( wtime, ftime)

    #     # for wint in wtime: # [начало, конец] проходимся по рабочим часам

    #     #     wstart = wint[0]
    #     #     wend = wint[1]

    #     #     free_time = 0
            
    #     #     for fint in ftime: #перебираем свободные часы, если на рабочие часы приходится свободные час, то вырезаем их
    #     #         fstart = fint[0]
    #     #         fend = fint[1]

    #     #         if wstart < fend:
    #     #             if wend > fstart:
    #     #                 free_time += ( fend-wstart )
    #     #                 continue
    #     #             else


    #     #         if wend  > fstart:
    #     #             if wstart < fend:
    #     #                 free_time += ( wend-fstart )
    #     #                 continue
            
    #     #     hours_worked += ( wend - wstart ) - free_time
    #     #     #print(hours_worked)
                

    #         # wLen = wint[1]-wint[0]
    #         # if wLen < sec_round:
    #         #     continue
    #         # else:
    #         #     hours_worked += wLen

    #     return hours_worked

    def getTime(self, pos="s", causeId=0):
        """ Вернет время utime\n
        Если указан ид конкретного случая, то вернет его время\n
        по умолчанию врернет время начала последнего из существующих"""

        if causeId ==0: 
            keys = list(self.timeIntervals.keys())
            causeId = max(keys) # Это ключ к последней записи И ид записи (у которого есть и время начала и время конца)

        if pos not in "se": logger.warn("TimerPoint:getTime: Не верная позиция: '{}'".format(pos))
        
        return _Time(self.timeIntervals[causeId][ 1 if pos=="e" else 0 ], pos).getTime_utime()

    def getTime_s(self, pos="s", causeId=0):
        """ Вернет время ЧЧ:ММ\n
        Если указан ид конкретного случая, то вернет его время\n
        по умолчанию врернет время начала последнего из существующих"""
        return getStringedTime( self.getTime(pos="s", causeId=0) )



    def putTime(self, time, pos="s", causeId=0): # { id1:[start, end], id2:[start, end] }
        """ Меняет время интервала\n
        если не указан конкретный интервал из существующих, берется последний\n
        если caucseId = -1, то создается новый интервал\n
        time принимается либо str"HH:MM" либо utime\n
        pos - позиция указанного времени в интервале (s = start, e = end)
        """

        try:
            causeId = int(causeId)
        except:
            pass

        if causeId ==0: 
            keys = list(self.timeIntervals.keys())
            causeId = max(keys) # Это ключ к последней записи И ид записи (у которого есть и время начала и время конца)

        
        if causeId == -1:
            causeId = insert_timePoint_by_table_name(self.day_id, self.cause)
            self.timeIntervals[ causeId ] = [ 0, 0 ]

        
        if isinstance(time, str):
            timeId = _Time.s_setTime_strtime(time, self.day_id, causeId, pos)
        elif isinstance(time, int):
            if time == 0: 
                timeId = 0 # Такого быть не должно!
                logger.warn("imerPoint:placeStart: время = 0!")
            else:
                timeId = _Time.s_setTime_utime(time, self.day_id, causeId, pos)

        update_timePoint_time_byPos(pos, timeId, causeId, self.day_id)
        return timeId

    def __str__(self):
        aStr = f"Cause:{self.cause}\n"
        intervals = self.getTimeIntervals()
        for pos, interval in enumerate( intervals, 1):
            aStr += f"{pos}: s:{_Time(interval[0],'s')}\te: {_Time(interval[0],'e')} \n"










        



