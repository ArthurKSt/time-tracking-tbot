from database.bd_user_group_activity import select_group_list_byUser, select_group_perms_list, select_user_perms_list, delete_perm_group, delete_perm_user, delete_user_from_group, select_group_weight
from creators.c_scheduled_create import scheduled

def bd_getUser_perm_list(user_id):
    """return user's perms\n"""

    # Лучше не перепроверять права часто.
    # Завести отдельную табличку пользователей, где хранить время последнего получения прав
    """
    Таблица в бд, в которой записаны права, срок последнего запроса прав, срок последнего сообщения
    Если человек запрашивает права второй раз за 10мин - отклонять, выдавать старые права
    Если человек пишет 3е сообщение за 10секунд - ничего не делать
    Если человек пишет 10е сообщение за минуту - ничего не делать
    Если человек пишет 20е сообщение за час - ничего не делать
    Хранить кеш внутри класса пользователя (не гениально ли?)
    """

    permD = {} # perm_name: [params, weight]

    timeNow = scheduled.getTime()

    # Получаем стандартные права
    bd_dPerms = select_group_perms_list( 0 )
    if bd_dPerms:

        for indPerm, val in enumerate(bd_dPerms):
            permEndTime = bd_dPerms[indPerm][5]
            permName = bd_dPerms[indPerm][2]

            if permEndTime > timeNow:
                delete_perm_user( user_id, permName )
                continue

            try: 
                if permD[ permName ][1] > currWeight: continue
            except KeyError: pass

            permParam = bd_dPerms[indPerm][4]
            if permParam == "allow": permParam = True
            elif permParam == "deny": permParam = False
            else: continue

            permD[ permName ] = [ permParam, 99 ]


    # Получаем права из группы
    bd_groups = select_group_list_byUser(user_id) # Получаем список групп в которых человек находится
    if bd_groups:

        for indGroup, val in enumerate(bd_groups):
            groupEndTime = bd_groups[indGroup][3]
            groupId = bd_groups[indGroup][2]
            #ремя действия устарел, то удалить его и пропустить это действие
            if groupEndTime > timeNow:
                delete_user_from_group( user_id, groupId )
                continue

            currWeight = select_group_weight( groupId )
            
            bd_group_perms = select_group_perms_list( groupId )
            if bd_group_perms:

                for indPerm, val in enumerate(bd_group_perms):
                    permEndTime = bd_group_perms[indPerm][5]
                    permName = bd_group_perms[indPerm][2]
                    if permEndTime > timeNow:
                        delete_perm_group( groupId, permName )
                        continue

                    permParam = bd_group_perms[indPerm][4]
                    if permParam == "allow": permParam = True
                    elif permParam == "deny": permParam = False
                    else: continue

                    try: 
                        if permD[ permName ][1] > currWeight: continue
                    except KeyError: pass

                    permD[ permName ] = [ permParam, currWeight ]

    # Получаем уникальные права пользователя
    bd_uPerms = select_user_perms_list( user_id)
    if bd_uPerms:

        for indPerm, val in enumerate(bd_uPerms):
            permEndTime = bd_uPerms[indPerm][5]
            permName = bd_uPerms[indPerm][2]

            if permEndTime > timeNow:
                delete_perm_user( user_id, permName )
                continue

            try: 
                if permD[ permName ][1] > currWeight: continue
            except KeyError: pass

            permParam = bd_uPerms[indPerm][4]
            if permParam == "allow": permParam = True
            elif permParam == "deny": permParam = False
            else: continue

            permD[ permName ] = [ permParam, 99 ]


    finalList = []
    for key, val in permD.items():
        if val[0] : finalList.append(key)

    return finalList