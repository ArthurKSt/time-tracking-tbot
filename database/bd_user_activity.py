
import sqlite3
from h_functions.tools import getStringedDate

from creators.c_logger_create import logger as log

# from decorators.d_check_params_decorator import check_parms

# conn = sqlite3.connect(r'store/bd.db')
from constants.config import DB_USER as dir
conn = sqlite3.connect(dir)
cur = conn.cursor()


# ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ 

def insert_group_password(group_id, password):
    """ Создает пароль для группы, позвращает ид записи"""

    sqlite_insert_query = """INSERT INTO auth(group_level, password)
        VALUES(?, (?));"""
    
    p = conn.execute(sqlite_insert_query, (group_id, password))

    conn.commit()

    return p.lastrowid #Возвращает ИД записи


# @check_parms( (0,None), ("", None))
def insert_user(telegram_id, telegram_name):
    """ Создает нового пользователя в бд (perm = 0, atWork=0, notif=" ")
    return = insert id"""

    #user: teleg_id INTEGER teleg_name TEXT level INTEGER at_work INTEGER needs_notification TEXT
    sqlite_insert_query = """INSERT INTO user(teleg_id, teleg_name)
        VALUES(?, (?));"""
    
    p = conn.execute(sqlite_insert_query, (telegram_id, telegram_name))

    conn.commit()

    return p.lastrowid #Возвращает ИД записи


def insert_cost( user_id, cost):
    """ Создает запись стоимости человека
    return = insert id"""

    #user: teleg_id INTEGER teleg_name TEXT level INTEGER at_work INTEGER needs_notification TEXT
    sqlite_insert_query = """INSERT INTO cost(teleg_id, cost)
        VALUES(?, ?);"""
    
    p = conn.execute(sqlite_insert_query, (user_id, cost))
    conn.commit()

    return p.lastrowid #Возвращает ИД записи



# @check_parms( ("",None), (0, None))
# def insert_day(date_today, telegram_id): 
#     """ date string like 'YYYY M D'.spliteable(' ') \nreturn post ID """
#     # day_information : post_id INTEGER teleg_id INTEGER date INTEGER id_come_time INTEGER id_leave_time INTEGER

#     sqlite_insert_query = """INSERT INTO day_information(teleg_id, date)
#         VALUES(?, ?);"""

#     r = conn.execute(sqlite_insert_query, (telegram_id, date_today))
#     conn.commit()

#     return r.lastrowid


# @check_parms( ("",None), (0, None), ("", None), (0,None))
# def insert_time_by_table_name(table_name, time_now, date, telegram_id):
#     """time unix type\n
#     return: postId , in: tbname, time, date, tgid"""
#  post_id  teleg_id date time,
#     sqlite_insert_query = f"""INSERT INTO {table_name}_time(teleg_id, date, time)
#         VALUES(?, ?, ?);"""


#     r = conn.execute(sqlite_insert_query, (telegram_id, date, time_now))
#     conn.commit()

#     return r.lastrowid



# ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ 


def select_group_byPassword(password):
    """
    return = group id
    """
    
    sqlite_select_query = f"""SELECT group_level FROM auth 
    WHERE password = (?) ;"""

    cur.execute(sqlite_select_query, ( password,) )
    result = cur.fetchone()

    return result



def select_cost_by_id(user_id):
    """
    return = integer cost
    """
    
    sqlite_select_query = f"""SELECT * FROM cost 
    WHERE teleg_id = ?
    ORDER BY id DESC ;"""
    #ORDER BY name COLLATE NOCASE ASC

    cur.execute(sqlite_select_query, ( user_id,))
    result = cur.fetchone()

    return result



def select_user_by_round(perm_min=0, perm_max=1, how_match=20):
    """ Вывести пользователей по диапазону \n
    in: perm_min, max, max count return \n
    return ([teleg_id, teleg_name, level],[],...) \n"""

    sqlite_select_query = """SELECT teleg_id, teleg_name, level FROM user
    WHERE level >= (?) AND level <= (?);"""

    cur.execute(sqlite_select_query, (perm_min, perm_max, ))
    result = cur.fetchmany(how_match)

    return result


# def select_uniq_date_for(*user_id, how_match=60):
#     """ Вывести уникальные даты для списка пользователей \n
#         in: list(users id) \n
#         return: list( dates )
#     """
#     dates = []

#     for id in user_id:

#         sqlite_select_query = """SELECT date FROM day_information
#         WHERE teleg_id = ? ;"""

#         cur.execute(sqlite_select_query, (id, ))
#         r = cur.fetchmany(how_match)

#         for date in r: 
#             if date not in dates: dates.append(*date)

#     return dates



# @check_parms( ("",None), (0, None))
# def select_day_info(date, telegram_id):
#     """
#     Если нет записи на пользователя в указ.день не создастся пустая запись
#     date string like 'YYYY M D'.spliteable(' ')\n
#     return = 0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
#     """
    
#     sqlite_select_query = """SELECT * FROM day_information
#     WHERE teleg_id = ? AND 
#     (date=?) ;"""

#     cur.execute(sqlite_select_query, (telegram_id, date))
    
#     result = cur.fetchone()
#     # if not result:
#     #     insert_day(date, telegram_id)

#     return result if result else None




# @check_parms( ("", None), (0, None), ("", None))
# def select_time_list_by_table_name(date, telegram_id, table_name, how_many_items=5):
#     """date string like 'YYYY M D'.spliteable(' ')
#     return = list (post_id teleg_id date time)
#     """

    
#     if not table_name in ("come", "leave"):
#         ##print("db select time list by table ", table_name) #Как это выходит??
#         return None
    
#     sqlite_select_query = f"""SELECT * FROM {table_name}_time 
#     WHERE teleg_id = ? AND (date=?) 
#     ORDER BY post_id DESC ;"""
#     #ORDER BY name COLLATE NOCASE ASC

#     cur.execute(sqlite_select_query, ( telegram_id, date,))
#     result = cur.fetchmany(how_many_items)

    return result

# @check_parms( (0, None) )
def select_user(telegram_id=0):
    """
    result = 0teleg_id  1teleg_name  2level 3at_work 4needs_notification """

    sqlite_select_query = """SELECT * FROM user
    WHERE teleg_id == (?);"""

    cur.execute(sqlite_select_query, (telegram_id,))
    result = cur.fetchone()

    ##print("Из бд выгружен пользователь", result, "по ид: ", telegram_id)

    return result if result else None

def select_userId_byName(name):
    """ status:bool"""
    sqlite_select_query = """
    SELECT teleg_id FROM user
    WHERE teleg_name == (?)
    ;"""
    cur.execute(sqlite_select_query, (name,) )
    result = cur.fetchone()
    return result


def select_from_users_ByLevel(level, how_many="30"): # лимит выгруженных записей лучше инициализировать в настройках
    """
    in: level like ">1" or "<=0"
    result = list : teleg_id INTEGER, teleg_name TEXT, level INTEGER, at_work INTEGER, needs_notification TEXT"""

    
    sqlite_select_query = f"""SELECT * FROM user
    WHERE level {level};"""
    #print(sqlite_select_query)

    cur.execute(sqlite_select_query)
    result = cur.fetchmany(how_many)

    ##print('Из бд выгрузились пользователи с правами работник+ :',result)

    return result





def select_from_users_ByMaxMinLevel(maxLevel, minLevel, how_many="30"): # лимит выгруженных записей лучше инициализировать в настройках
    """
    in: level int and how many
    result = list : teleg_id INTEGER, teleg_name TEXT, level INTEGER, at_work INTEGER, needs_notification TEXT"""

    
    sqlite_select_query = f"""SELECT * FROM user
    WHERE level <= ? and level >= ?
    ;"""
    #print(sqlite_select_query)

    cur.execute(sqlite_select_query, (maxLevel, minLevel,))
    result = cur.fetchmany(how_many)

    ##print('Из бд выгрузились пользователи с правами работник+ :',result)

    return result



# @check_parms( (0,None), ("", None))
# def select_time_by_table_name(post_id, table_name):
#     """find by post_id when User leave\n
#     return = post_id teleg_id date time """

#     ##print("_postId", post_id)
#     if (post_id==0): return None #Если записи нет, то сразу отклонить

#     sqlite_select_query = f"""SELECT * FROM {table_name}_time
#     WHERE post_id = ? ;"""

#     cur.execute(sqlite_select_query, ( post_id,))
#     result = cur.fetchone()
#     return result


# ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ 

 
def delete_group_password(password):
    #print("t_act: delete_Old_tasks: time_now:", time_now)

    sqlite_delete_query = """DELETE FROM auth
    WHERE password = (?) ;"""

    cur.execute(sqlite_delete_query, (password, ) )
    
    conn.commit()
    return



# ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ 


# @check_parms( (0,None), ("", None))
def update_user_status_atWork(telegram_id, status):
    """ status:bool"""
    sqlite_update_query = """Update user set at_work = ? where teleg_id = ?"""
    conn.execute(sqlite_update_query, (telegram_id, 1 if status else 0))
    conn.commit()
    return True


def update_user_permission(telegram_id, permission):
    """ status:bool"""

    #print("bda update_user_permission", telegram_id, permission, type(permission))
    sqlite_update_query = """Update user set level = ? where teleg_id = ?"""
    conn.execute(sqlite_update_query, (permission, telegram_id, ) )
    conn.commit()

    return True


def update_user_name(telegram_id, name):
    """ status:bool"""
    sqlite_update_query = """Update user set teleg_name = (?) where teleg_id = ?"""
    conn.execute(sqlite_update_query, (telegram_id, name,) )
    conn.commit()
    return True


# @check_parms( ("",None), (0, None), (0, None), ("", None) )
# def update_date_time_by_time_and_table_name(table_name, time_id, telegram_id, date):
#     """ меняет у таблицы пользователь-дата Ид времени по названию таблицы \n
#     in: table_name (come/leave), time_id, telegram_id, date\n
#     return: true если все норм, false если не получилось"""

#     ##print("upd_bd_data_time Проверить, вышло ли обновить дату, если даты нет")

#     ##print("upd_bd_data_time time_id, date", time_id, date)

#     sqlite_update_query = f"""Update day_information set id_{table_name}_time = ? 
#     WHERE teleg_id = ? AND date = ?"""
#     r = conn.execute(sqlite_update_query, (time_id, telegram_id, date,))
#     conn.commit()

#     ##print("upd_bd_data_time", r)

#     return True




# ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ FOR TIME POINT ___ 


# Выбираем день по его айди (перепроверяем его существование)
# def select_day_info_byID(day_id):
#     """
#     return = 0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
#     """
    
#     sqlite_select_query = """SELECT * FROM day_information
#     WHERE post_id = ? ;"""

#     cur.execute(sqlite_select_query, (day_id, ))
    
#     result = cur.fetchone()

#     return result

# получаем записи об отрезках времени 
# def select_timePoint_byDayID_and_Cause(day_id, cause, howMany=10):
#     """
#     return = ((0id 1dayInfo_id 2id_start 3id_end 4cause),)
#     """
    
#     sqlite_select_query = """SELECT * FROM timePoint
#     WHERE dayInfo_id = ? AND cause=(?);"""

#     cur.execute(sqlite_select_query, (day_id,cause ))
    
#     result = cur.fetchmany(howMany)

#     return result

# получаем время по ИД
# def select_time_byID(time_id):
#     """return 0id 1dayInfo_id 2timePoint_id 3time """
    
#     sqlite_select_query = """SELECT * FROM time
#     WHERE id = ? ;"""

#     cur.execute(sqlite_select_query, (time_id, ))
    
#     result = cur.fetchone()
#     return result

# Вставляем новую запись о времени
# def insert_timePoint_by_table_name(day_id, cause, start_id=0, end_id=0):
#     """return id new post"""
#  post_id  teleg_id date time,
#     sqlite_insert_query = f"""INSERT INTO timePoint(dayInfo_id, id_start, id_end, cause)
#         VALUES(?, ?, ?, (?) );"""

#     r = conn.execute(sqlite_insert_query, ( day_id, start_id, end_id, cause ) )
#     conn.commit()

#     return r.lastrowid

# def insert_time_by_table_name(day_id, timePoint_id, time, direction):
#     """return id new post"""
#  0id 1dayInfo_id 2timePoint_id 3time
#     sqlite_insert_query = f"""INSERT INTO time(dayInfo_id, timePoint_id, time)
#         VALUES(?, ?, ? );"""

#     r = conn.execute(sqlite_insert_query, ( day_id, timePoint_id, time, ) )
#     conn.commit()

#     return r.lastrowid

# def update_timePoint_time_byPos(pos, time_id, cause_id, day_id):
#     """ меняет ид времени в таблице точка времани\n
#     in: pos(Начальная точка или конечная точка)\n
#     time_id, cause_id
#     """
#     #0id 1dayInfo_id 2id_start 3id_end 4cause
#     if pos=="s": pos = "id_start"
#     elif pos=="e": pos = "id_end"
#     else: 
#         log.warn(" userBD:update_timePoint_time_byPos: incorrect position: {}".format(pos))
#         pos=="id_start"

#     sqlite_update_query = f"""Update timePoint set {pos} = ? 
#     WHERE id = ? AND dayInfo_id = ?"""

#     conn.execute(sqlite_update_query, ( time_id, cause_id, day_id, ) )
#     conn.commit()


#     return True



    