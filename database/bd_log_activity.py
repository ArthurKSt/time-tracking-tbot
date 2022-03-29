
import sqlite3
from h_functions.tools import getStringedDate

from constants.config import GTM

from creators.c_logger_create import logger as log

# conn = sqlite3.connect(r'store/bd.db')
from constants.config import DB_LOG as dir
conn = sqlite3.connect(dir)
cur = conn.cursor()


# ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ 




def insert_log(words, text, time, teleg_id=0):
    """ Создает новую запись в логах. Возвращает ИД записи\n 
    \n
  Лог\n
    КлючевыеСлова #Для быстрого поиска, если "не пришел" или "Обычное информирование о запуске"\n
    ТекстЗаписи #основная строка Имя.Суть.Текст(или ответ) Пользователь..Не пришел.. Потому что..\n
    Время\n
    сКемСвязано #Ид пользователя (если есть)\n В ДАТУ ДОБАВЛЯЕТ GTM!!
"""

    # log  id words text time teleg_id
    sqlite_insert_query = """INSERT INTO log(words, text, time, teleg_id, date)
        VALUES((?), (?), ?, ?, (?));"""

    date = getStringedDate(time)
    
    p = conn.execute(sqlite_insert_query, (words, text, time, teleg_id, date) )
    conn.commit()

    return p.lastrowid #Возвращает ИД записи


def insert_addition(log_id, text, time):
    """ Дополняет запись в логах. Возвращает ИД записи дополнения)\n
    \n
  Дополнения: - хранит изменения со временем (если человек пришел позже, к примеру)\n
    ИдДополнения\n
    ИдЗаписи\n
    ТекстДополнения\n
    Время\n"""

    #  addition id id_log text time
    sqlite_insert_query = """INSERT INTO addition(id_log, text, time)
        VALUES(?, (?), ?);"""
    
    p = conn.execute(sqlite_insert_query, (log_id, text, time) )
    conn.commit()

    return p.lastrowid #Возвращает ИД  записи




# ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ 


def select_log_byDateAndId(date, user_id, how_match=100):
    """ Получить список ( (Запись, дополнения) ) по длине списка можно узнать, сколько записей \n
    in: date, user_id, max count return \n 
    return (count_lines, ( log ) ) \n
    logResultFull = [ logNote[2], logNote[4], *fromAdditionResult ] #Сохраняем текст, время лога и список дополнений с текстом и временем дополнения"""

    # log  id words text date time teleg_id
    #  addition id id_log text time

    outList = [] #Cписок, который вернет функция

    sqlite_select_query = """SELECT * FROM log
    WHERE date = (?) AND teleg_id = ?;"""

    cur.execute(sqlite_select_query, (date, user_id, ))
    fromLogResult = cur.fetchmany(how_match)

    lineCounter = 0 #Считаем, сколько строчек логов по человеку есть

    if fromLogResult: #Если есть результаты по поиску Логов по дате и пользователю (Все логи на дату)

        for logNote in fromLogResult: # По записе в логах ищем заметки
            lineCounter += 1 # Если запись в логах есть, прибавляем строку

            sqlite_select_query = """SELECT text, time FROM addition
            WHERE id_log = ?;"""

            id_log = logNote[0] # в 0 позиции лежит ид лога

            cur.execute(sqlite_select_query, ( id_log, ))  
            fromAdditionResult = cur.fetchmany(how_match) #Получаем все заметки по логу

            if fromAdditionResult: lineCounter += len(fromAdditionResult) # Если запись о дополнениях есть, прибавляем их кол-во

            logResultFull = [ logNote[2], logNote[4], fromAdditionResult ] #Сохраняем текст, время лога и список дополнений с текстом и временем дополнения
        
            outList.append( logResultFull ) #записываем отдельный лог (их может быть на одну дату несколько)

    return (lineCounter, outList)





# ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ 







# ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ 


