
import sqlite3

# from tools import getStringedDate

# from c_logger_create import logger as log

# from d_check_params_decorator import check_parms

# conn = sqlite3.connect(r'store/bd.db')
from constants.config import DB_TASK as dir
conn = sqlite3.connect(dir)
cur = conn.cursor()

# task           0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who 

# task_result    0:id  1:task_id  2:result_time  3:result_text
 

    # ВремяАктуальности (0-всегда или конкретная дата) ( )
    # ВремяУдалить (0 - не удалять)
    # Кому (Ур:Знак:ИДилиЗвезда) "(0:=:*)-для всех гостей","(1:+:*)-для всех кроме гостей","(0:+:Ид) для


# ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ 



def insert_task(task_text, for_who, create_time, actual_time=0, remove_time=0):
    """ Создает новую задачу\n
    in:\n
        task_text состоит из 2х полей (как часто повторять 1-1раз, 0-постоянно) и (Название задачи)\n
        for_who состоит из 3х:\n
            symbol. "-" системное, "g" группа, "u" пользователь\n
            >=<. ">" если символ группа, то тем, у кого вес более указанного, у системного или пользователя "="\n
            id. Ид пользователя или, если системное - то чего угодно. (сообщения, к примеру), если для всех, то *\n
        create,actual,remove указывает время создания, использования и удаления задачи соответственно\n\n

        return = insert id (Есть защита от повтора задачи)\n
        Если текст задачи и цель уже была в списке - вернет старый ид"""

    prev_bd = select_task_byForWho_byTaskText(for_who, task_text) #Если такая задача уже была
    if prev_bd:
        return prev_bd[0]

    # task           0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who 
    sqlite_insert_query = """INSERT INTO task(task_text, create_time, actual_time, remove_time, for_who)
        VALUES((?), ?, ?, ?, (?) );"""
    
    p = conn.execute(sqlite_insert_query, ((task_text), create_time, actual_time, remove_time, (for_who)) )

    conn.commit()

    return p.lastrowid #Возвращает ИД записи


def insert_result(task_id, result_time, result_text):
    """ Создает результат задачи\n
    in: task_id, result_time \n
    result_text (статус:сообщение) "y:Я уже пришел или n:Я болею"
    
    return = insert id"""

    # task_result    0:id  1:task_id  2:result_time  3:result_text
    sqlite_insert_query = """INSERT INTO task(task_id, result_time, result_text)
        VALUES(?, ?, (?) );"""
    
    p = conn.execute(sqlite_insert_query, (task_id, result_time, (result_text)) )

    conn.commit()

    return p.lastrowid #Возвращает ИД записи




# ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ 



def select_task_byForWho_byTaskText(for_who, task_text):
    """ получить задачу по "для кого"
    return ( (0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who ), ) """

    sqlite_select_query = f"""SELECT * FROM task
    WHERE for_who = (?) AND task_text = (?) ;"""

    cur.execute(sqlite_select_query, (for_who, task_text) )
    result = cur.fetchone()

    return result


def select_task_actual(actual_time):
    """ получить задачу по времени актуальности
    return ( (0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who ), ) """

    sqlite_select_query = f"""SELECT * FROM task
    WHERE actual_time <= ? ;"""

    cur.execute(sqlite_select_query, (actual_time,))
    result = cur.fetchone()


    return result



def select_task_byId(id):
    """ получить задачу по id
    return ( (0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who ), ) """

    sqlite_select_query = f"""SELECT * FROM task
    WHERE id = ? ;"""

    cur.execute(sqlite_select_query, (id,))
    result = cur.fetchone()


    return result


def select_task_byType_list(type:str, how_many_items=10, orderBy="DESC"):
    """ type like '1:'-повторяется 1 раз, '0:'  -обычная задача\n
    можно вместо типа сообщения ввести тип события :WhyNotAtWork \n
    return ( (0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who ), ) """

    sqlite_select_query = f"""SELECT * FROM task
    WHERE task_text like '%{type}%' ORDER BY id {orderBy} ;"""
    #ORDER BY name COLLATE NOCASE ASC

    cur.execute(sqlite_select_query,)
    result = cur.fetchmany(how_many_items)


    return result

def select_task_taskText(task_text):
    """ Вернет 1(даже если таких больше) задачу, с идентичным текстом\n
    Актуально для запросов ежедневных задач\n
    return (0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who )"""

    sqlite_select_query = f"""SELECT * FROM task
    WHERE task_text = (?)  ;"""
    #ORDER BY name COLLATE NOCASE ASC

    cur.execute(sqlite_select_query,(task_text,))
    result = cur.fetchone()
    return result


def select_task_results_list(id, how_many_items=5):
# task           0:id  1:task_text  2:create_time  3:actual_time  4:remove_time  5:for_who 

# task_result    0:id  1:task_id  2:result_time  3:result_text
    
    
    sqlite_select_query = f"""SELECT * FROM task_result 
    WHERE id = ? ORDER BY id DESC ;"""
    #ORDER BY name COLLATE NOCASE ASC

    cur.execute(sqlite_select_query, ( id,))
    result = cur.fetchmany(how_many_items)


    return result


# ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ 

 
def delete_Old_tasks(time_now):

    sqlite_select_query = """DELETE FROM task
    WHERE remove_time!=0 AND remove_time < ? ;"""
    cur.execute(sqlite_select_query, (time_now, ) )
    
    conn.commit()
    return


def delete_task_byId(id):
    sqlite_select_query = """DELETE FROM task
    WHERE id = ? ;"""
    cur.execute(sqlite_select_query, (id,) )
    
    conn.commit()
    return
 

# ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ 





# ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ COMPLEX ___ 


