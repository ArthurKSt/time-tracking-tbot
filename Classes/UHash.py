from constants.config import USR_MAX_PER10, USR_MAX_PER30, USR_PERM_LIVE

from database.bd_get_perms import bd_getUser_perm_list

# from database.bd_get_allowed_perms import bd_getUser_perm_list
from database.bd_user_group_activity import  insert_user_in_group, select_group_list_byUser, select_user_weight, select_userId_list_round
from creators.c_scheduled_create import scheduled as scheduled_tasks

class _UHash:
    users = {}


    def __init__(self, user_id):
        self.user_id = user_id

        self.userPermList = []
        self.lastGetPermsTime = 0
        # self.user_weight = 0

        #10sec
        self.lastActPer10sec_Count = 0
        self.lastActPer10sec_Time = 0

        #30sec
        self.lastActPer30sec_Count = 0
        self.lastActPer30sec_Time = 0

    def s_check(user_id):
        #print("hash keys",_UHash.users.keys())
        return user_id in list( _UHash.users.keys() )

    def s_create(user_id):
        if _UHash.s_check(user_id):
            return
        else:
            _UHash.users[user_id] = _UHash(user_id)

    def s_get(user_id):
        if _UHash.s_check(user_id):
            return _UHash.users[user_id]
        else:
            return _UHash(user_id)

    
    # def getWeight(self):
    #     self.getPermsList()

    #     return self.user_weight
        

    def getPermsList(self, now=False):
        #print("Hash getPerms uid", self.user_id)
        if self.user_id == 0:
            return []

        if now:
            self.userPermList = bd_getUser_perm_list( self.user_id, onlyAllow=True )
            # self.user_weight = select_user_weight(self.user_id) #Получаем вес пользователя
            self.lastGetPermsTime = scheduled_tasks.getTime()
            return self.userPermList

            
        if self.lastGetPermsTime == 0:
            #Добавляем пользователя в группу "гости", если он не состоит в группах
            bd_group_list = select_group_list_byUser(self.user_id)
            if not bd_group_list:
                insert_user_in_group( self.user_id, 1 )

            self.userPermList = bd_getUser_perm_list( self.user_id, onlyAllow=True )
            # self.user_weight = select_user_weight(self.user_id) #Получаем вес пользователя
            self.lastGetPermsTime = scheduled_tasks.getTime()

        if (( scheduled_tasks.getTime() - self.lastGetPermsTime ) > USR_PERM_LIVE): 
            #print("__generate new permissions")
            self.userPermList = bd_getUser_perm_list( self.user_id, onlyAllow=True )
            # self.user_weight = select_user_weight(self.user_id) #Получаем вес пользователя
            self.lastGetPermsTime = scheduled_tasks.getTime()
            
        
        #print( " cur pems = ", self.userPermList)

        print( select_userId_list_round(betterId=self.user_id, onlyLower=True) )
        return self.userPermList

    def do(self):
        if self.user_id == 0:
            return False


        #print("self.lastActPer10sec_Count", self.lastActPer10sec_Count)
        self.lastActPer10sec_Count += 1
        self.lastActPer30sec_Count += 1

        if (self.lastActPer10sec_Time == 0): # Если это первое нажатие после загрузки
            self.lastActPer10sec_Time = scheduled_tasks.getTime()
            self.lastActPer30sec_Time = scheduled_tasks.getTime()

        # Если время с последней проверки прошло достаточно, то обновляем таймер
        if (scheduled_tasks.getTime() - self.lastActPer10sec_Time) > 10:
            self.lastActPer10sec_Time = scheduled_tasks.getTime()
            self.lastActPer10sec_Count = 0
        else:

            if self.lastActPer10sec_Count > USR_MAX_PER10:
                return False

        # Если время с последней проверки прошло достаточно, то обновляем таймер
        if (scheduled_tasks.getTime() - self.lastActPer30sec_Time) > 30:
            self.lastActPer30sec_Time = scheduled_tasks.getTime()
            self.lastActPer30sec_Count = 0
        else:

            if self.lastActPer30sec_Count > USR_MAX_PER30:
                return False

        return True

uhash = _UHash(0)