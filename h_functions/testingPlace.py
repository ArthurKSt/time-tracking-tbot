import calendar
from datetime import datetime
import time

def getStringedDate(u_time, gtm=0):
    """u_time is thing what gives telegram.message.date"""
    if not isinstance(u_time, int):
        return ""

    hour = 3600
    return time.strftime("%Y %m %d", time.gmtime(u_time+(gtm*hour)))
    

def getStringedTime(u_time, gtm=0, addHM=False):
    """ перевод u_time в строку ЧЧ:ММ"""
    if not isinstance(u_time, int):
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

    return answ


def getOldDay(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
    hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second,
    modYear = 0, modMonth=0, modDay=0, modHour=0, modMinute=0, modSecond=0, gtm=3): 
        print(modHour)

        second = int(second)+modSecond
        if second<0:
            for i in range(second, 60, +60):
                second = i
                modMinute -= 1
        elif second>59:
            for i in range(second, -1, -60):
                second = i
                modMinute += 1

        minute = int(minute)+modMinute
        if minute<0:
            for i in range(minute, 60, +60):
                minute = i
                modHour -= 1
        elif minute>59:
            for i in range(minute, -1, -60):
                minute = i
                modHour += 1

        
        print(modHour)

        modHour += gtm

        print(modHour)
        hour = int(hour)+modHour
        if hour<0:
            for i in range(hour, 24, +24):
                hour = i
                modDay -= 1
        elif hour>23:
            for i in range(hour, -1, -24):
                hour = i
                modDay += 1

        year = int(year)+modYear

        month = int(month)+modMonth
        if month<1:
            for m in range(month, 13, +12):
                month = m
                year -=1
        elif month>12:
            for m in range (month,0, -12):
                month = m
                year += 1
        
        modMonth = 0

        moncal = calendar.monthcalendar(year, month)
        dayinMonth = 0
        for week in moncal:
            for dayw in week:
                if dayw==0: continue
                else: dayinMonth+=1

        day = int(day)+modDay

        if day>dayinMonth:
            needCorrect = True
            while needCorrect:
                day-=dayinMonth
                month+=1
                if month<1:
                    for m in range(month, 13, +12):
                        month = m
                        year -=1
                elif month>12:
                    for m in range (month,0, -12):
                        month = m
                        year += 1
                moncal = calendar.monthcalendar(year, month)
                dayinMonth = 0
                for week in moncal:
                    for dayw in week:
                        if dayw==0: continue
                        else: dayinMonth+=1
                if day<=dayinMonth:
                    needCorrect=False

        if day<1:
            needCorrect = True
            while needCorrect:
                month-=1
                if month<1:
                    for m in range(month, 13, +12):
                        month = m
                        year -=1
                elif month>12:
                    for m in range (month,0, -12):
                        month = m
                        year += 1
                moncal = calendar.monthcalendar(year, month)
                dayinMonth = 0
                for week in moncal:
                    for dayw in week:
                        if dayw==0: continue
                        else: dayinMonth+=1
                day += dayinMonth
                if day>=1:
                    needCorrect = False

        print(year, month, day, hour, minute, second)
        return int( datetime( year, month, day, hour, minute, second).timestamp() )

def getDay(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
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


if __name__ == "__main__":

    now = getDay()
    print("nowT date:", getStringedDate(now) )
    print("nowT time:", getStringedTime(now) )

    newTime = getDay( month=1, modMonth=1 )

    print("newT date:", getStringedDate(newTime) )
    print("newT time:", getStringedTime(newTime) )