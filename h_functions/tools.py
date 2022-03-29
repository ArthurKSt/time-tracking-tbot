import time

from constants.config import GTM
from creators.c_logger_create import logger as log

#Перенести в статические ф-ии планировщика


def calcTimeLen(u_time_end, u_time_start):
    """ Вернет кол-во часов"""
    try:
        hour = 3600
        result = (u_time_end-u_time_start)/hour
    except:
        log.warn("tools:calcTimeLen: не верный тип данных {}-{}".format( type(u_time_end), type(u_time_start) ) )
        return 0
    return result

def getStringedDate(u_time, gtm=0):
    """u_time is thing what gives telegram.message.date"""
    if not isinstance(u_time, int):
        log.warn("tools:getStringedDate: не верный тип данных {} : {}".format(u_time, type(u_time)))
        return ""

    hour = 3600
    return time.strftime("%Y %m %d", time.gmtime(u_time+(gtm*hour)))
    

def getStringedTime(u_time, gtm=0, addHM=False):
    """ перевод u_time в строку ЧЧ:ММ"""
    if not isinstance(u_time, int):
        log.warn("tools:getStringedTime: не верный тип данных {} : {}".format(u_time, type(u_time)))
        return ""

    if u_time == 0: return "Не указано"
    
    hour = 3600

    answ = time.strftime("%H:%M", time.gmtime(u_time+(gtm*hour)))
    # answ = time.strftime("%H:%M:%S", time.gmtime(u_time+(gtm*hour)))

    if addHM:
        # h,m,s = answ.split(":")
        h,m = answ.split(":")
        answ = ""
        if h != "00":
            answ += h + "ч. "
        if m != "00":
            answ += m + "м. "
        # if s != "00":
        #     answ += s + "с. "

        

    return answ

def getStringetWeekDay(u_time, gtm=0):
    """ получить из u_time строку с названием недели out'Tue'"""
    if not isinstance(u_time, int):
        log.warn("tools:getStringetWeekDay: не верный тип данных {} : {}".format(u_time, type(u_time)))
        return ""

    hour = 3600
    return time.strftime("%a", time.gmtime(u_time+(gtm*hour)))


def getUTimeFromStringTime(strTime):
    """ Получить из строки ЧЧ:ММ ютайм сегодняшней даты указанного времени"""
    now = int( time.time() ) +GTM
    wanna = strTime

    try:
        now_h, now_m = ( int(i) for i in getStringedTime(now).split(":")  )
        ask_h, ask_m = ( int(i) for i in wanna.split(":") )
    except:
        log.warn("tools:getUTimeFromStringTime: не верный тип данных или формат(HH:MM) {} : {}".format( strTime, type(strTime) ))
        return 0
    else:

        if ask_h > now_h:
            if ask_m > ask_h:
                mod_h = ask_h - now_h
                mod_m = ask_m - now_m
            else:
                mod_h = ask_h - now_h - 1
                mod_m = ask_m+( 60-ask_m )
        else:
            if ask_m < now_h:
                mod_h = -1* ( now_h - ask_h )
                mod_m = -1* ( now_m - ask_m )
            else:
                mod_h = -1* ( now_h - ask_h -1 )
                mod_m = -1* ( now_m + ( 60-ask_m ) )

        asked = addTime(now, hour=mod_h, minute=mod_m)
        return (asked)


def addTime(u_time, minute=0, hour=0, day=0, month=0):
    """ прибавляет к ютайм указанные минуты, часы, дни, месяцы"""
    if not isinstance(u_time, int):
        log.warn("tools:addTime: не верный тип данных {} : {}".format(u_time, type(u_time)))
    lminute = 60
    lhour = 3600
    lday = 86400
    lmonth = 2629743
    return u_time+(minute*lminute)+(hour*lhour)+(day*lday)+(month*lmonth)

