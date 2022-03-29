
import sqlite3


from constants.config import DB_USER as dir
conn = sqlite3.connect(dir)
cur = conn.cursor()


#'group' 0id  1weight  2name 3description
#user_group 0id 1user_id 2group_id 3end_time  
#perm_group 0id 1group_id 2name 3description 4params 5end_time
#perm_user 0id 1user_id2 name 3description 4params 5end_time

# ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ INSERTS ___ 


#'group' 0id  1weight  2name 3description
def insert_group(name="NoName", weight=1, description=""):
    """return id new post"""
    sqlite_insert_query = f"""INSERT INTO 'group'(weight, name, description)
        VALUES(?, (?) (?) );"""
    r = conn.execute(sqlite_insert_query, ( name, weight, description ) )
    conn.commit()
    return r.lastrowid


#user_group 0id 1user_id 2group_id 3end_time  
def insert_user_in_group(user_id, group_id, end_time=0):
    """return id new post"""
    sqlite_insert_query = f"""INSERT INTO user_group(user_id, group_id, end_time)
        VALUES(?, ?, ? );"""
    r = conn.execute(sqlite_insert_query, ( user_id, group_id, end_time ) )
    conn.commit()
    return r.lastrowid


#perm_group 0id 1group_id 2name 3description 4params 5end_time
def insert_perm_group(group_id, name, description="", params="", end_time=0):
    """return id new post"""
    sqlite_insert_query = f"""INSERT INTO perm_group(group_id, name, description, params, end_time)
        VALUES(?, (?), (?), (?), ? );"""
    r = conn.execute(sqlite_insert_query, ( group_id, name, description, params, end_time ) )
    conn.commit()
    return r.lastrowid


#perm_user 0id 1user_id2 name 3description 4params 5end_time
def insert_perm_user(user_id, name, description="", params="", end_time=0):
    """return id new post"""
    sqlite_insert_query = f"""INSERT INTO perm_user(group_id, name, description, params, end_time)
        VALUES(?, (?), (?), (?), ? );"""
    r = conn.execute(sqlite_insert_query, ( user_id, name, description, params, end_time ) )
    conn.commit()
    return r.lastrowid


# ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ SELECTS ___ 


def select_group_perms_list(group_id):
    """ Получаем список прав группы\n
    #perm_group 0id 1group_id 2name 3description 4params 5end_time\n
    params = a=allow, d=deny, or other!!
    """
    sqlite_select_query = """SELECT * FROM perm_group
    WHERE group_id = ?
    ORDER BY id DESC ;"""
    cur.execute(sqlite_select_query, (group_id, ))
    result = cur.fetchmany(20)
    return result


def select_user_perms_list(user_id):
    """ Получаем список прав человека\n
    #perm_user 0id 1user_id2 name 3description 4params 5end_time
    """

    #print(user_id)
    sqlite_select_query = """SELECT * FROM perm_user
    WHERE user_id = ?
    ORDER BY id DESC ;"""
    cur.execute(sqlite_select_query, (user_id, ))
    result = cur.fetchmany(20)
    return result

def select_group_list_byUser(user_id):
    """ Получаем список групп в которых участвует человек\n
        #user_group 0id 1user_id 2group_id 3end_time  
    """
    print("___DO TASK _ select_group_list_byUser",user_id )
    sqlite_select_query = """SELECT * FROM user_group
    WHERE user_id = ?
    ORDER BY id DESC ;"""
    cur.execute(sqlite_select_query, (user_id, ))
    result = cur.fetchmany(20)
    return result


def select_group_byID(group_id):
    """ Получаем список группу\n
        #'group' 0id  1weight  2name 3description
    """
    sqlite_select_query = """SELECT * FROM 'group'
    WHERE id = ?
    ORDER BY id DESC ;"""
    cur.execute(sqlite_select_query, (group_id, ))
    result = cur.fetchone()
    return result


def select_group_weight(group_id):
    """ Получаем вес группы\n
        #'group' 0id  1weight  2name 3description
    """
    sqlite_select_query = """SELECT weight FROM 'group'
    WHERE id = ? ;"""
    cur.execute(sqlite_select_query, (group_id, ))
    result = cur.fetchone()
    return result




# MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM

# SELECT * 
# FROM test1 a 
# LEFT OUTER JOIN test2 b ON b.c1=a.c1 
# LEFT OUTER JOIN test3 c ON c.c2=b.c2 


def select_user_weight(user_id):
    sqlite_select_query = f"""SELECT MAX('group'.weight)
    FROM 'group' JOIN user_group
    ON user_group.group_id == 'group'.id
    WHERE user_group.user_id == ?
    ;"""

    cur.execute(sqlite_select_query, (user_id, ))
    result = ( cur.fetchone() )[0]
    return result

def select_userId_list_round(minW=2, maxW=2, betterId=0, onlyLower=False):
    """ Получить список идов людей, вес группы которых ходит в указанное расстояние\n
    betterId - заменяет максимальный вес, весом этого человека (если он указан)\n
    return [(uniq_id),..] Возвращает список людей, которые есть в группах ниже указанных\n
    ВНИМАНИЕ! Для получения списка людей, чей вес только ниже(нет в более высоких группах), нужно указать фильтр OnlyLower=True"""

    if betterId != 0:
        maxW = select_user_weight(betterId) #Получаем максимальный вес человека, если его нет
        if not maxW or maxW==1: #То нет никого меньше него (если он в гостевой группе -то тоже)
            return []

    if minW==0:
        sqlite_select_query = f"""SELECT teleg_id FROM user;"""
    else:
        sqlite_select_query = f"""SELECT DISTINCT user_group.user_id
        FROM user_group JOIN 'group'
        ON user_group.group_id == 'group'.id
        WHERE 'group'.weight <= ? AND 'group'.weight >= ?
        ;""" #Мы получили список людей, которые находятся в группах, ниже чем загаданный (но они могут быть ЕЩЕ и в группах выше загаданных)

    cur.execute(sqlite_select_query, (maxW,minW ))
    result = cur.fetchall() #result = ((id,),..)

    if onlyLower:
        finalList = []
        for id in result:
            weight = select_user_weight(id[0])
            if weight <= maxW:
                finalList.append((id[0],))
        return finalList

    return result





# def selectWhoReached(user_id):
#     #Получаем самый большой вес группы этого человека
#     #Получаем список групп меньше полученного
#     #Получаем список пользователей с этими группами

#     sqlite_select_query = f"""SELECT MAX(group.weight)
#     FROM user_group, 

#     WHERE user_group.user_id = ?

#     INNER JOIN group ON group
    
#     """


#     sqlite_select_query = f"""SELECT user.teleg_id, user.name 
#     FROM user_group, group, user

#     WHERE 
#     user.teleg_id != ? 
#     AND
#     group.weight > 0
#     AND

        
#     LEFT OUTER JOIN group ON group.id=user_group.group_id
#     LEFT OUTER JOIN user ON user.teleg_id=user_group.user_id



#     WHERE level {level};"""

#     sqlite_select_query = f"""SELECT user.teleg_id, user.teleg_name, group FROM user
#     WHERE level {level};"""




# MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM








# ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ DELETE ___ 

#user_group 0id 1user_id 2group_id 3end_time  
def delete_user_from_group(user_id, group_id):
    sqlite_select_query = """DELETE FROM user_group
    WHERE user_id = ? AND group_id = ? ;"""
    cur.execute(sqlite_select_query, (user_id, group_id, ) )
    conn.commit()
    return

#perm_group 0id 1group_id 2name 3description 4params 5end_time
def delete_perm_group(group_id, perm):
    sqlite_select_query = """DELETE FROM perm_group
    WHERE group_id = ? AND name = (?) ;"""
    cur.execute(sqlite_select_query, (group_id, perm, ) )
    conn.commit()
    return

#perm_user 0id 1user_id2 name 3description 4params 5end_time
def delete_perm_user(user_id, perm):
    sqlite_select_query = """DELETE FROM perm_user
    WHERE user_id = ? AND name = (?) ;"""
    cur.execute(sqlite_select_query, (user_id, perm, ) )
    conn.commit()
    return


def delete_user(id):
    sqlite_delete_query = """DELETE user WHERE teleg_id = ? ;"""
    cur.execute(sqlite_delete_query, (id, ) )
    conn.commit()
    return


def delete_guests():
    lowerBD = select_userId_list_round(minW=0, maxW=1, onlyLower=True)
    if lowerBD:
        for id in lowerBD:
            delete_user(id[0])
    return


    
 



# ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ UPDATES ___ 




# ___ ANOTHER ___ ANOTHER ___ ANOTHER ___ ANOTHER ___ ANOTHER ___ ANOTHER ___ 


