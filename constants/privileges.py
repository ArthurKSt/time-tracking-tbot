"""
Здесь расписаны права пользователей
Что бы разрешить или запретить пользователю действие
нужно перенести команду из одной группы в другую
Действует на всех пользователей группы.

Теперь когда права подгружаются из БД
не актуальна запись сюда прав
Но их можно записывать, что бы не забыть что к чему
"""

"""
гость
Btn_message_start ввод старт
Btn_message_help ввод помощь
Perk_guest 

работник
Btn_message_DayRecord ввод учет времени
Btn_message_Menu ввод меню

BtnM_message_time #Видеть информацию о себе
BtnM_message_time_other #Видеть информацию о других
BtnM_message_help


Perk_worker
Perk_see_Menu
Conf_work_days Рабочие дни недели

администратор
Perk_see_cost возможность смотреть стоимость человека
Perk_admin
Btn_message_set_cost возможность устанавливать цену человека
"""


# guest = [
#     "Btn_message_start",  # Аналог старт
#     "Btn_message_help" # аналог хелп
# ]

# worker = [

#     'Btn_message_DayRecord', #: "Учет времени",
#     'Btn_message_Menu', #: "Меню",
#     'Perk_see_Menu', # Видеть меню
#     # "Btn_message_startWork", # записывает начало дня
#     # "Btn_message_endWork", # записывает конец дня
#     # "Btn_message_info", # выводит информацию о сегодняшнем дне
#     # "BtnInl_message_chooseAnother", # не нужно проверять доступ
#     # "BtnInl_message_cancel" # не нужно проверять доступ
#     ]
# worker.extend(guest)

# admin = [
#     # "Btn_message_get_info", # получить файл с информацией о проработанных часах
#     # "Btn_message_add_worker", # добавить пользователя в класс работники (альтернатива коду группы)
#     # "Btn_message_set_cost", # установить зп пользователю
#     "Perk_see_cost" # Возможность видеть стоимость в час
# ]
# admin.extend(worker)

# debug = [
#     # "Btn_add_admin"# добавить пользователя в класс админы (альтернатива коду группы)
# ]
# debug.extend(admin)


# PRIVILEGES = {
#     0: guest,
#     1: worker,
#     2: admin,
#     3: debug
# }

