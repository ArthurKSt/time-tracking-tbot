
from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMGiveGEO(StatesGroup): # тест гео-положения
    giveGEO = State()


class FSMWorker(StatesGroup):
    user_class = State()        # Base information

    guest_menu = State()        # Base for unnamed
    ask_name = State()          # In registration field
    ask_gender = State()        # In registration field

    worker_menu = State()       # Base for worker
    worker_getInfo = State()    # How many worked and another answers

class FSMAreYouLate(StatesGroup): #
    FirstAnswer = State() # Вы не отметились, почему? Ответ сюда
    # Я еще не пришел
    WhyLate = State() # Почему вы опаздываете?
    WhyLateConfirm = State()
    # Я уже пришел
    WhoCanConfirm = State() #Выводим список людей, которые на работе
    ConfirmWhoCanConfirm = State() #Человек должен подтвердить, что все введено правильно
    WhenYouCome = State() #Выводим клавиатуру ввода времени
    ConfirmWhenYouCome = State() #Спрашиваем пользователя, который был указан, пришел ли работник вовремя
    # Я не приду
    WhyNot = State() # Почему не придешь
    ConfirmWhy = State() 



class FSMChangeStartTime(StatesGroup):
    date = State()

# class FSMWhyNotAtWork(StatesGroup): # Когда человек отчитывается, почему не пришел, попадает сюда
#     getAnswer = State()

# class FSMWhoCanConfirm(StatesGroup): # Когда человек забыл нажать "Пришел" , а потом пришлось отчитываться, кто может подтвердить, что он пришел рано
#     who = State()
#     ctime = State()

# class FSMWhyNotCome(StatesGroup): # когда человек отвечает "Я не приду"
#     whyNotCome = State()

class FSMAuth(StatesGroup): # Получаем пароль для авторизации
    getPassword = State()

class FSMChengeCost(StatesGroup): #Меняем стоимость человека в час
    getNewCost = State()

class FSMChangeName(StatesGroup): #Меняем имя человека
    getNewName = State()


