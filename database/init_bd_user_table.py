import sqlite3

# для разделения работы на несколько компаний можно создавать разные базы данных и разных ботов
# conn = sqlite3.connect(r'store/bd.db')

from constants.config import DB_USER as dir

conn = sqlite3.connect(dir)
cur = conn.cursor()


# Пользователь
#   *Ид телеграма (ключ, по которому можно найти человека)
#   имя по которому обращается бот, и которое указывается в отчете
#   Уровень (Что можно делать в боте) (Изменяемое)
#   Сейчас на работе (Изменяемое)
#   Нужно оповестить (строка с запросами) (Изменяемое)
cur.execute("""CREATE TABLE IF NOT EXISTS user (
    teleg_id INTEGER PRIMARY KEY,
    teleg_name TEXT,
    level INTEGER DEFAULT 0,
    at_work INTEGER DEFAULT 0,
    needs_notification TEXT DEFAULT " " );
""")
conn.commit()


# наРаботе
#   *Ид записи
#   Дата (каждый новый день по работникам идет цикл, создаются таблички на новый день) (Если новый день, если нет таблицы на работника - создать таблицу)
#   Ид телеграма 
#   Время пришел (может быть много) (Изменяемое) (записывается ид из come_time.post_id)
#   Время ушел (может быть много) (Изменяемое)
cur.execute("""CREATE TABLE IF NOT EXISTS day_information (
    post_id INTEGER PRIMARY KEY,
    teleg_id INTEGER,
    date TEXT,
    id_come_time INTEGER DEFAULT 0,
    id_leave_time INTEGER DEFAULT 0,

    FOREIGN KEY (teleg_id) REFERENCES user (teleg_id) ON DELETE CASCADE
    );
""")
conn.commit()


# ВремяПришел
#   Ид записи
# Ид пользователя
#   время Во сколько пришел (по времени можно узнать и дату и сравнить ее со днем)
cur.execute("""CREATE TABLE IF NOT EXISTS come_time(

    post_id INTEGER PRIMARY KEY,
    teleg_id INTEGER,
    date TEXT,
    time INTEGER,

   FOREIGN KEY (teleg_id) REFERENCES user (teleg_id) ON DELETE CASCADE
   );
""")
conn.commit()


# ВремяУшел
#   Ид записи
# Ид пользователя
#   Время
cur.execute("""CREATE TABLE IF NOT EXISTS leave_time(

    post_id INTEGER PRIMARY KEY,
    teleg_id INTEGER,
    date TEXT,
    time INTEGER,

   FOREIGN KEY (teleg_id) REFERENCES user (teleg_id) ON DELETE CASCADE
   );
""")
conn.commit()


# Стоимость человека
cur.execute("""CREATE TABLE IF NOT EXISTS cost(

    id INTEGER PRIMARY KEY,
    teleg_id INTEGER,
    cost INTEGER DEFAULT 0,

   FOREIGN KEY (teleg_id) REFERENCES user (teleg_id) ON DELETE CASCADE
   );
""")
conn.commit()


# Таблица с авторизацией
cur.execute("""CREATE TABLE IF NOT EXISTS auth(

    id INTEGER PRIMARY KEY,
    group_level INTEGER,
    password TEXT
   );
""")
conn.commit()


# Таблица Точка времени
"""
    Ид - идентификатор записи
    дейинфоИд - ид записи за день пользователя (используется для поиска всех ТВ связанных со днем)
    ид старта - ид записи в которой записано время начала (может быть несколько к одной точке времени для возможности отката)
    ид конца - ид запи....
    тип таймера
"""
cur.execute("""CREATE TABLE IF NOT EXISTS timePoint(
    id INTEGER PRIMARY KEY,
    dayInfo_id INTEGER,

    id_start INTEGER DEFAULT 0,
    id_end INTEGER DEFAULT 0,

    cause TEXT,

   FOREIGN KEY (dayInfo_id) REFERENCES day_information (post_id) ON DELETE CASCADE
   );
""")
conn.commit()

# Таблица Время
"""
    Ид - идентификатор записи
    время - время
    dayInfo_id таблица которая содержит дату, к которой точка прикреплена
    timePoint_id нужна для того, что бы видеть, с какой записью связана точка (для какой создана, но может быть уже не используется)
    direction показывает в какую ячейку точкиВремени это записалось
"""
cur.execute("""CREATE TABLE IF NOT EXISTS time(
    id INTEGER PRIMARY KEY,
    dayInfo_id INTEGER,
    timePoint_id INTEGER,
    direction TEXT,

    time INTEGER,

   FOREIGN KEY (dayInfo_id) REFERENCES day_information (post_id) ON DELETE CASCADE
   );
""")
conn.commit()





# Permissions 

# Группы пользователей (Работник, Модератор, Администратор, Фрилансер, Освобожденный...)
"""'group' 0id  1weight  2name 3description
"""
cur.execute("""CREATE TABLE IF NOT EXISTS 'group'(
id INTEGER PRIMARY KEY,
weight INTEGER,
name TEXT,
description TEXT
);
""")
conn.commit()


# cur.execute("""CREATE TABLE IF NOT EXISTS group(
#     id INTEGER PRIMARY KEY,
#     weight INTEGER,
#     name TEXT
#    );
# """)
# conn.commit()


# Таблица пользователи в группы
"""
user_group 0id 1user_id 2group_id 3end_time  
endtime - это когда человека нужно будет выкинуть из группы (0=никогда)
"""
cur.execute("""CREATE TABLE IF NOT EXISTS user_group(
    id INTEGER PRIMARY KEY,

    user_id INTEGER,
    group_id INTEGER,

    end_time INTEGER DEFAULT 0,

    FOREIGN KEY (group_id) REFERENCES 'group' (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user (teleg_id) ON DELETE CASCADE
   );
""")
conn.commit()

# Таблица права группы
"""
perm_group 0id 1group_id 2name 3description 4params 5end_time
endtime - это когда право нужно будет убрать из группы (0=никогда)
"""
cur.execute("""CREATE TABLE IF NOT EXISTS perm_group(
    id INTEGER PRIMARY KEY,

    group_id INTEGER,
    name TEXT,
    description TEXT,
    params TEXT,

    end_time INTEGER DEFAULT 0,

    FOREIGN KEY (group_id) REFERENCES 'group' (id) ON DELETE CASCADE
   );
""")
conn.commit()

# Таблица права группы
"""
perm_user 0id 1user_id2 name 3description 4params 5end_time
endtime - это когда право нужно будет убрать от пользователя (0=никогда)
"""
cur.execute("""CREATE TABLE IF NOT EXISTS perm_user(
    id INTEGER PRIMARY KEY,

    user_id INTEGER,
    name TEXT,
    description TEXT,
    params TEXT,

    end_time INTEGER DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES user (teleg_id) ON DELETE CASCADE
   );
""")
conn.commit()














