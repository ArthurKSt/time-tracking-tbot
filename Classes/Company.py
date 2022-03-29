from Classes.User import User

from database.bd_user_activity import select_from_users_ByLevel

#Класс компания можно перенести в класс Пользователи (как статические ф-ии и массив статический)

class Company:
    """ Не все пользователи - работники! Нужно исправить класс"""
    name = "None"
    user_limit = 0

    def __init__(self, name="None", users_limit=0):
        self.name = name
        self.user_limit = users_limit
        self.workers = {}

        #Загружать работников при инициализации компании (users.level >0)
        #select_from_users_workersP возвращает список пользователей
        #для создания пользователей нужно загрузить класс пользователь

    def reloadWorkersFromBD(self):
        self.workers = {}

        bd = select_from_users_ByLevel(">= 1",self.user_limit) #Запрос на список работников при инициализации компании (users.level >0)
        for worker_info in bd:
            worker = User(worker_info[0], worker_info[2], worker_info[3]) #id, name, perm

            self.addWorker(worker)

    def getWorker(self, id): 
        """Возвращает объект пользователя из объекта Компании, если нет, то возвращает None"""
        try:
            return self.workers[id]
        except KeyError:
            return None

    def getAndMakeUser(self, user_id, user_name):
        """Возвращает объект пользователя из объекта Компании, если нет, то создает новый и возвращает"""

        if not self.getWorker(user_id): #Если такого пользователя нет в объекте компании
            user = User(user_id, user_name)

            # self.scheduled_tasks.addTask("admins", "докажи что это работник, а не левый чел") # Реализовать

            #self.addWorker(user) # Не правильно. Новый человек будет с уровнем 0, а работник - с 1м уровнем
            return user

        return self.workers[user_id] #Если пользователь нашелся, возвращает его

    def getWorkersId(self): return list(self.workers)

    def getWorkersNotAtWorkID(self):
        wlist = []
        for id, worker in self.workers.items():
            if not worker.isAtWork(): wlist.append( id )
        return wlist

    def addWorker(self, worker): self.workers[worker.getId()] = worker

    def removeWorker(self, worker): self.workers.pop({worker.getId()})


