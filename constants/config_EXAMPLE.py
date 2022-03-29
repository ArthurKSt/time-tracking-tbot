
TOKEN = 'BOT_TOKEN'


COM_NAME = r"Name"
COM_LIMIT = 20

LOG_DIR = ""#"./logs/"


# DB_LOG = r'database/' + COM_NAME + r'_log.db'
# DB_USER = r'database/' + COM_NAME + r'_user.db'
# DB_TASK = r'database/' + COM_NAME + r'_task.db' 

DB_LOG = r'database/' + COM_NAME + r'bd.db'
DB_USER = r'database/' + COM_NAME + r'bd.db'
DB_TASK = r'database/' + COM_NAME + r'bd.db' 



SCHED_UPDTIME = 5 # Как часто обновляется внутренний цикл (Чем меньше, тем больше запросов к БД, но быстрее выполняются запланированные действия)
SCHED_PREV_DATES_DAYS = 1

# SCHED_WORK_TIME_START = "09:00"
SCHED_WORK_TIME_START = "09:50"
# SCHED_WORK_TIME_START = getStringedTime( int( tnow() ) )
SCHED_BOT_DAY_START_TIME = "6:00" #Во сколько бот начинает ежедневную задачу

SCHED_TIME_REMOVE = 20 # (устарело) время удаления задачи
SCHED_TIME_ACTUAL = 10

SCHED_TIME_REMOVE_AFTER_DO = 60 # Сколько секунд после выполнения задачи удалить задачу (должно быть больше, чем SCHED_UPDTIME)

monthsEn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
monthsRu = ["Янв", "Фев", "Мар", "Апр", "Май", "Инь", "Иль", "Авг", "Сен", "Окт", "Ноя", "Дек"]

weekDaysEn = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
weekDaysRu = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
WorkDays = [1,1,1,1,1,0,0] 

SCHED_WORK_DAYS = dict(zip(weekDaysEn, WorkDays))

GTM = 3*3600

CALLBACKLIVE_TIME = 5*60 # Сколько времени доступна инлайн кнопка


USR_MAX_PER10 = 3 #Сколько действий можно сделать за 10 сек
USR_MAX_PER30 = 15
USR_PERM_LIVE = 30 #Раз в какое время перепроверять права

TIMER_OLD_SET = 30*60 # Через сколько спрашивать пользователя "Не забыл ли он выключить таймер"

MENU_AVILIBLE = [
        "BtnM_message_time", # Показать информацию о посещениях
        "BtnM_message_help", # Помощь
        # "BtnM_message_history", # Недавние события
        # "BtnM_message_duty", # График дежурств Рабочие дни
        # "BtnM_message_workDays", # Рабочие дни
        "BtnM_message_admin", # Администрирование
        "BtnM_message_test", #Для тестирования новых фич
    ]

