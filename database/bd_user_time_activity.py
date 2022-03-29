
import sqlite3
from h_functions.tools import getStringedDate

from creators.c_logger_create import logger as log

# from decorators.d_check_params_decorator import check_parms

from constants.config import DB_USER as dir
conn = sqlite3.connect(dir)
cur = conn.cursor()


# ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ 






# @check_parms( ("",None), (0, None))
def insert_day(date_today, telegram_id): 
    """ date string like 'YYYY M D'.spliteable(' ') \nreturn post ID """
    # day_information : post_id INTEGER teleg_id INTEGER date INTEGER id_come_time INTEGER id_leave_time INTEGER

    sqlite_insert_query = """INSERT INTO day_information(teleg_id, date)
        VALUES(?, ?);"""

    r = conn.execute(sqlite_insert_query, (telegram_id, date_today))
    conn.commit()

    return r.lastrowid





# ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ 





def select_uniq_date_for(*user_id, how_match=60):
    """ Вывести уникальные даты для списка пользователей \n
        in: list(users id) \n
        return: list( dates )
    """
    dates = []

    for id in user_id:

        sqlite_select_query = """SELECT date FROM day_information
        WHERE teleg_id = ? ;"""

        cur.execute(sqlite_select_query, (id, ))
        r = cur.fetchmany(how_match)

        for date in r: 
            if date not in dates: dates.append(*date)

    return dates



# @check_parms( ("",None), (0, None))
def select_day_info(date, telegram_id):
    """
    Если нет записи на пользователя в указ.день не создастся пустая запись
    date string like 'YYYY M D'.spliteable(' ')\n
    return = 0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
    """
    
    sqlite_select_query = """SELECT * FROM day_information
    WHERE teleg_id = ? AND 
    (date=?) ;"""

    cur.execute(sqlite_select_query, (telegram_id, date))
    
    result = cur.fetchone()
    # if not result:
    #     insert_day(date, telegram_id)

    return result if result else None


def select_days_list_byUser(telegram_id):
    """Получить все дни связанные с пользователем
    return = 0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
    \n [('date'),(..),..]
    """
    
    sqlite_select_query = """SELECT date FROM day_information
    WHERE teleg_id = ?;"""

    cur.execute(sqlite_select_query, (telegram_id,))
    
    result = cur.fetchall()

    return result


def select_whoStarted(date):
    """ Получить список работников, которые были на рабочем месте в указанный день\n
    Если человек отмечался за день, то он был\n ((id,),..)"""

    sqlite_select_query = """SELECT teleg_id FROM day_information
    WHERE date = (?);"""

    cur.execute(sqlite_select_query, (date,))
    result = cur.fetchall()

    return result







# ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ 

 
# def delete_Day(date):
#     sqlite_select_query = """DELETE FROM day_information
#     WHERE date = (?) ;"""
#     cur.execute(sqlite_select_query, (date, ) )
#     conn.commit()
#     return

def delete_older_Day(u_time):
    """Удаляем старые дни    """
    sqlite_delete_query = """
    DELETE day_information
    FROM time JOIN day_information
    WHERE time < ? ;"""

    cur.execute(sqlite_delete_query, (u_time, ) )
    conn.commit()
    return


# ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ 









# ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ 






# Выбираем день по его айди (перепроверяем его существование)
def select_day_info_byID(day_id):
    """
    return = 0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
    """
    
    sqlite_select_query = """SELECT * FROM day_information
    WHERE post_id = ? ;"""

    cur.execute(sqlite_select_query, (day_id, ))
    
    result = cur.fetchone()

    return result


# получаем время по ИД
def select_time_byID(time_id):
    """return 0id 1dayInfo_id 2timePoint_id 3direction 4time """
    
    sqlite_select_query = """SELECT * FROM time
    WHERE id = ? ;"""

    cur.execute(sqlite_select_query, (time_id, ))
    
    result = cur.fetchone()
    return result



# получаем время по ИД
def select_timePoint_byID(time_id):
    """0id 1dayInfo_id 2id_start 3id_end 4cause"""
    
    sqlite_select_query = """SELECT * FROM timePoint
    WHERE id = ? ;"""

    cur.execute(sqlite_select_query, (time_id, ))
    
    result = cur.fetchone()
    return result


def select_time_byCauseID_and_Direction(cause_id, direction, how_many=10):
    """
    ORDER BY id DESC \n
    return 0id 1dayInfo_id 2timePoint_id 3direction 4time """
    
    sqlite_select_query = """SELECT * FROM time
    WHERE timePoint_id = ? AND direction=(?)
    ORDER BY id DESC ;"""

    cur.execute(sqlite_select_query, (cause_id, direction, ))
    
    result = cur.fetchmany(how_many)
    return result


# получаем записи об отрезках времени 
def select_timePoint_byDayID_and_Cause(day_id, cause, howMany=10, invert=True):
    """ return = ((0id 1dayInfo_id 2id_start 3id_end 4cause),)  \n
    Сначала самые последние (те что недавно нажаты)"""

    direct = "DESC" if invert else "ASC"
    
    sqlite_select_query = f"""SELECT * FROM timePoint
    WHERE dayInfo_id = ? AND cause=(?)
    ORDER BY id {direct} ;"""

    cur.execute(sqlite_select_query, (day_id,cause ))
    
    result = cur.fetchmany(howMany)

    return result







# Вставляем новую запись о времени
def insert_timePoint_by_table_name(day_id, cause, start_id=0, end_id=0):
    """return id new post"""
#  post_id  teleg_id date time,
    sqlite_insert_query = f"""INSERT INTO timePoint(dayInfo_id, id_start, id_end, cause)
        VALUES(?, ?, ?, (?) );"""

    r = conn.execute(sqlite_insert_query, ( day_id, start_id, end_id, cause ) )
    conn.commit()

    return r.lastrowid



def insert_time_by_table_name(day_id, timePoint_id, time, direction):
    """
    in: day_id, timePoint_id, time, direction\n
    return id new post"""
#  0id 1dayInfo_id 2timePoint_id 3time

    sqlite_insert_query = f"""INSERT INTO time(dayInfo_id, timePoint_id, time, direction)
        VALUES(?, ?, ?, (?) );"""

    r = conn.execute(sqlite_insert_query, ( day_id, timePoint_id, time, direction ) )
    conn.commit()

    return r.lastrowid



















def update_timePoint_time_byPos(pos, time_id, cause_id, day_id):
    """ меняет ид времени в таблице точка времани\n
    in: pos(Начальная точка или конечная точка)\n
    time_id, cause_id, day_id
    """
    #0id 1dayInfo_id 2id_start 3id_end 4cause
    if pos=="s": pos = "id_start"
    elif pos=="e": pos = "id_end"
    else: 
        log.warn(" userBD:update_timePoint_time_byPos: incorrect position: {}".format(pos))
        pos=="id_start"

    sqlite_update_query = f"""Update timePoint set {pos} = ? 
    WHERE id = ? AND dayInfo_id = ?"""

    conn.execute(sqlite_update_query, ( time_id, cause_id, day_id, ) )
    conn.commit()


    return True



    





def delete_timePoint_byID(id):
    sqlite_select_query = """DELETE FROM timePoint
    WHERE id = (?) ;"""
    cur.execute(sqlite_select_query, (id, ) )
    conn.commit()
    return

def delete_time_byID(id):
    sqlite_select_query = """DELETE FROM time
    WHERE id = (?) ;"""
    cur.execute(sqlite_select_query, (id, ) )
    conn.commit()
    return