"""
Нужно получить ексель файл запрошенный пользователем
Так, что бы файл генерировался 1 раз в день по прошедшим дням (текущий не трогать)


(Вход - ид пользователя)
Пользователь может запросить файл о себе одному
    Запросить данные о днях об одном пользователе
        По списку дней создать Точку времени и получать 
                время начала работы и время конца работы
                кол-во проработанных часов

        Запросить данные о логах от дня, получить их количество
                записать рядом с кол-вом часов
                на страницу 2 записать логи


Пользователь может запросить файл о другом
Пользователь может запросить файл о всех
"""


import xlsxwriter
# from xlsxwriter.utility import xl_rowcol_to_cell

from database.bd_user_time_activity import select_days_list_byUser
from database.bd_user_activity import select_user
from Classes.User import User
from h_functions.translate import cyrIntoLat


#def avilible date


def get_user_excel(user_id):
    """ Вернет название файла """

    user_name = ""
    bd_user = select_user(user_id)
    if bd_user:
        ffname = cyrIntoLat( bd_user[1] )

    fname = f"download/{ffname}_report.xlsx"
    workbook = xlsxwriter.Workbook(f'{fname}')

    rowInfo=0
    colInfo=0
    rowLog=0

    months = []

    bd_days = select_days_list_byUser(user_id)
    if bd_days:# Если записи есть

        days = []
        for day in bd_days:
            days.append( day[0] )

        for day_date in days:
            umon = day_date[0:7]
            if umon not in months:
                months.append(umon)

        cfInfo = workbook.add_format()
        cfInfo.set_align('left')
        cfInfo.set_align('vcenter')

        tabInfo = workbook.add_format()
        tabInfo.set_align('right')
        tabInfo.set_align('vcenter')

        for month in months:

            worksheetInfo = workbook.add_worksheet(month+" Учет часов")

            for day_date in days:

                if month not in day_date:
                    continue
                
                print("day_date for user: ",day_date)
                user = User(user_id, _date=day_date)
                
                name = user.getName()

                start = user.getWhenStart()
                end = user.getWhenEnd()
                time = user.getWorkedTime()

                log = user.getLogCount()

                inform = [ #Пустота, Название поля, (Поле, форматирование)
                    ["", ("Имя:",tabInfo),     (name, cfInfo)           ],
                    ["", ("Н.дня:",tabInfo),   (start ,cfInfo)       ],
                    ["", ("К.дня:",tabInfo),   (end ,cfInfo)       ],
                    ["", ("Часов:",tabInfo),   (time,cfInfo)       ],
                    ["", ("Событий:",tabInfo), (log,cfInfo)      ]
                ]

                rowInfo += 1
                worksheetInfo.write(rowInfo, colInfo, day_date)
                rowInfo += 1

                _row = 0
                for  _void, _tname, _value in inform:
                    worksheetInfo.write( rowInfo+_row, colInfo*3+0, _void )
                    worksheetInfo.write( rowInfo+_row, colInfo*3+1, *_tname )
                    worksheetInfo.write( rowInfo+_row, colInfo*3+2, *_value )

                    worksheetInfo.set_column(rowInfo*3+0,colInfo*3+0, width=5)
                    worksheetInfo.set_column(rowInfo*3+2,colInfo*3+2, width=13)
                    worksheetInfo.set_column(rowInfo*3+2,colInfo*3+2, width=20)
                    _row += 1

                rowInfo += len(inform) #Когда пользователей закончили обрабатывать, переносим строчку ниже

    

    workbook.close()
    return fname


            

            

        








# from store.bd_user_activity import select_uniq_date_for, select_user_by_round, select_day_info, select_time_by_table_name, select_user, select_cost_by_id
# from database.bd_user_activity import select_user_by_round, select_user, select_cost_by_id

# from database.bd_user_time_activity import select_uniq_date_for, select_day_info

# from database.bd_log_activity import select_log_byDateAndId

# from constants.config import GTM

# from h_functions.tools import calcTimeLen, getStringedTime

# from creators.c_logger_create import logger as _log

# from constants.privileges import PRIVILEGES



# async def getExTable(permission):
#     """ выводит таблицу по всем работникам, чей допуск равен или меньше запросу
    
#     return new file name"""

#     costCounter=True if "Perk_see_cost" in PRIVILEGES[permission] else False
#     #Если человек, который вызвал создание файла не имеет доступа к ценникам, то и не давать

#     fname = f"download/{permission}_report.xlsx"

#     dateListName = [] # Названия месяцов для страниц екселевской таблицы
#     uniqDate = []
#     user_ids = []

#     bd_user = select_user_by_round(1,permission) #Вернет словарь, с картежеми внутри № В этой переменной лежат все люди с указанным уровнем (ид, имя, уровень)
#     if bd_user: ##print("Пользователи найдены")

#          #Получаем список всех пользователей
#         for user in bd_user: ##print("in list < (),(:1)", user, user[:1] )
#             user_ids.append( *user[:1] ) #Добавляем в список только иды полученных людей

#         bd_dates = select_uniq_date_for( *user_ids )
#         if bd_dates: ##print("Даты найдены")

#             #Получаем названия месяца для названий страниц таблицы
#             for date in bd_dates:
#                 # year, month, day = date.split(" ") # Первый способ, куча действий
#                 # strYM = year+" "+month
#                 strYM = date[0:7]

#                 if date not in uniqDate: uniqDate.append(date) #Получаем список уникальных дат
#                 if strYM not in dateListName: dateListName.append(strYM) #Добавляем строку в список названий страниц таблицы


#         else: #print("Даты не найдены")
#             pass

            
#     else: #print("Пользователи не найдены") # Если так, то и обрабатывать ничего не надо.
#         return
#         pass


#Далее создаем сам файл
    
#     workbook = xlsxwriter.Workbook(f'{fname}')


#     for mon in dateListName:#Перебирает месяцы


#         cfInfo = workbook.add_format()
#         cfInfo.set_align('left')
#         cfInfo.set_align('vcenter')

#         tabInfo = workbook.add_format()
#         tabInfo.set_align('right')
#         tabInfo.set_align('vcenter')

#         worksheetInfo = workbook.add_worksheet(mon+" Учет часов")
#         rowInfo = 0 #Для каждого месяца(новой странице) писать сверху в левом углу
#         colInfo = 0

#         worksheetLog = workbook.add_worksheet(mon+" События")
#         rowLog = 0

#         for day in uniqDate: #перебирает уникальные даты (если есть такая дата, в которой нет логов, то они будут пустые)
#             #print("udate", d)

#             if not mon in day: # Месяц- строка от даты, с вырезанным числом дня. Если месяц сходится с текущей датой, то ее нужно записать в этот месяц
#                 continue #Или же пропустить, если это не так

            

#             rowInfo +=2 #Пропускаем строчку

#             worksheetLog.write(rowLog, 0, day)
#             rowLog += 1
#             monLogMax = 0


#             for place, user_id in enumerate( user_ids ): #print("uuser", u) select_day_info, select_time_by_table_name, select_user
                
#                 # Обрабатываем логи

#                 name = "Unknown"
#                 bd_user = select_user(user_id) # 0teleg_id 1teleg_name 2level 3at_work 4needs_notification
#                 if bd_user: name = bd_user[1]
#                 else: _log.warn("excel.getExTable(log): Не вышло получить имя пользователя!")

#                 logCount, logF = select_log_byDateAndId(day, user_id) # [ logNote[2], logNote[4], *fromAdditionResult ] #Сохраняем текст, время лога и список дополнений с текстом и временем дополнения

#                 if logF:
#                     worksheetLog.write(rowLog, 1, name)
#                     rowLog+=1

#                     for l in logF:
#                         #print(l)
                        
#                         ltext = l[0]
#                         ltime = l[1]

#                         worksheetLog.write(rowLog, 2, ltext)
#                         worksheetLog.write(rowLog, 0, getStringedTime( ltime, GTM) )
#                         rowLog+=1

#                         try:
#                             addition = l[2]
#                         except:
#                             pass # Если дополнений нет, то и не надо
#                         else:
#                             for a in addition:
#                                 atext = a[0]
#                                 atime = a[1]

#                                 worksheetLog.write(rowLog, 2, atext)
#                                 worksheetLog.write(rowLog, 0, getStringedTime( atime, GTM) )
#                                 rowLog+=1

                    





                

#                 # Обрабатываем Информацию пользователей


#                 #Получаем данные пользователя (для начала иниц по-умолчанию)
#                 name = "Unknown"
#                 comeTime = 0
#                 leaveTime = 0
#                 workTime = 0
#                 log_count = logCount

#                 bd_user = select_user(user_id) # 0teleg_id 1teleg_name 2level 3at_work 4needs_notification
#                 if bd_user: name = bd_user[1]
#                 else: _log.warn("excel.getExTable: Не вышло получить имя пользователя!")

#                 bd_day_info = select_day_info(day, user_id) #0post_id 1teleg_id 2date 3id_come_time 4id_leave_time or NONE
#                 if bd_day_info:
#                     bd_come_time = select_time_by_table_name( bd_day_info[3], "come" ) #post_id teleg_id date time
#                     if bd_come_time: comeTime = bd_come_time[3]
#                     # else: _log.warn("excel.getExTable: Не вышло получить время начала пользователя!")

#                     bd_leave_time = select_time_by_table_name( bd_day_info[4], "leave" ) #post_id teleg_id date time
#                     if bd_leave_time: leaveTime = leaveTime = bd_leave_time[3]
#                     # else: _log.warn("excel.getExTable: Не вышло получить время окончания пользователя!")

#                     if bd_come_time==None or bd_leave_time==None: #Если БД выдало пустоту
#                         workTime = 0
#                     elif comeTime==0 or leaveTime ==0: # Если в бд пустая запись
#                         workTime = 0
#                     else:     # Если в бд есть запись и она не пустая, то считаем время

#                         #print("t BD",bd_come_time , bd_leave_time)
#                         #print("t Time", comeTime, leaveTime)

#                         workTime = calcTimeLen(leaveTime, comeTime)
                    
#                     # if bd_come_time!=0 and bd_leave_time!=0 :
                        
#                     #     #print("t BD",bd_come_time , bd_leave_time)
#                     #     #print("t Time", comeTime, leaveTime)
#                     #     if isinstance(comeTime, int) and isinstance(leaveTime, int):
#                     #         workTime = calcTimeLen(leaveTime, comeTime)
#                     #     else:
#                     #         workTime = 0
#                     #         _log.warn("ExTable error get work time")
#                     # else:
#                     #     #print("f",bd_come_time!=0 , bd_leave_time!=0)

                    
#                 # else:
#                 #     continue #Если о человеке нельзя получить день, то пропускаем его
#                     # _log.warn("excel.getExTable: Не вышло получить инфу о дне пользователя!")



#                 inform = [ #Пустота, Название поля, (Поле, форматирование)
#                     ["", ("Имя:",tabInfo),     (name,cfInfo)           ],
#                     ["", ("Н.дня:",tabInfo),   ( getStringedTime(comeTime, GTM) if comeTime!=0 else "Нет информации" ,cfInfo)       ],
#                     ["", ("Н.дня:",tabInfo),   ( getStringedTime(leaveTime, GTM) if leaveTime!=0 else "Нет информации" ,cfInfo)       ],
#                     ["", ("Часов:",tabInfo),   (workTime,cfInfo)       ],
#                     ["", ("Событий:",tabInfo), (log_count,cfInfo)      ]
#                 ]

#                 _row = 0
#                 #Подпишем дату, что бы не приходилось листать туда-сюда (Каждому третьему)
#                 if place%3==0:
#                     worksheetInfo.write(rowInfo-1, place*3+0, day)


#                 for  _void, _tname, _value in inform:
#                     worksheetInfo.write( rowInfo+_row, place*3+0, _void )
#                     worksheetInfo.write( rowInfo+_row, place*3+1, *_tname )
#                     worksheetInfo.write( rowInfo+_row, place*3+2, *_value )

#                     worksheetInfo.set_column(place*3+0,place*3+0, width=5)
#                     worksheetInfo.set_column(place*3+2,place*3+2, width=13)
#                     worksheetInfo.set_column(place*3+2,place*3+2, width=20)
#                     _row += 1

#             rowInfo += len(inform) #Когда пользователей закончили обрабатывать, переносим строчку ниже

#         #Когда закончили обрабатывать месяц нужно посчитать общее число часов
#         # У каждого пользователя в месяце запись состоит из 7строк
#         # Каждая 6я - это кол-во часов отработанных
#         # Посчитать сумму всех часов

#         for place, user_id in enumerate( user_ids ):

#             fString = "=SUM("

#             for _place in range(rowInfo-2, 0, -7):
#                 fString += xl_rowcol_to_cell( _place, place*3+2) + ","
#             fString += ")"


#             worksheetInfo.write(rowInfo+1, place*3+1, "Всего ч.:", tabInfo)
#             worksheetInfo.write(rowInfo+1, place*3+2, fString, cfInfo) #Формула подсчета


#         if costCounter:
#             finString = "=SUM(" #Здесь вообще вся стоимость считается
            
#             wasCost = False
#             for place, user_id in enumerate( user_ids ):
                
#                 cost = 0
#                 # bd = 0 #Подключаемся к бд, по иду получаем сколько стоит чел/час
#                 bd = select_cost_by_id(user_id)
#                 if bd: 
#                     wasCost = True
#                     cost = bd[2]

#                 worksheetInfo.write(rowInfo+2, place*3+1, "Руб/ч:", tabInfo) 
#                 worksheetInfo.write(rowInfo+2, place*3+2, cost, cfInfo) #Цена

#                 fString = "=(" + xl_rowcol_to_cell(rowInfo+1, place*3+2) + "*" + xl_rowcol_to_cell(rowInfo+2, place*3+2) + ")"

#                 worksheetInfo.write(rowInfo+3, place*3+1, "К оплате:", tabInfo) 
#                 worksheetInfo.write(rowInfo+3, place*3+2, fString, cfInfo) #Формула подсчета

#                 finString += xl_rowcol_to_cell(rowInfo+3, place*3+2)
            
#             if wasCost:
#                 finString += ")"

#                 worksheetInfo.write(rowInfo+5, 1, "Всего к оплате:", tabInfo) 
#                 worksheetInfo.write(rowInfo+5, 2, fString, cfInfo) #Формула подсчета



#     workbook.close()
#     return fname
        
