from database.bd_user_time_activity import select_time_byID, select_timePoint_byID, select_time_byCauseID_and_Direction, update_timePoint_time_byPos,\
    delete_time_byID, delete_timePoint_byID

def undo_placeTimerPointer(post_id):
    """ Вернет True если действие получилось отменить, иначе False """

    #print(post_id)

    bd_time = select_time_byID(post_id) #0id 1dayInfo_id 2timePoint_id 3direction 4time
    if bd_time: # Если запись такая и существует

        direction = bd_time[3]

        CurInTP, AthInTP = (2, 3) if direction=="s" else (3, 2) #Получаем иды противоположных направления
        cur_dir, ath_dir = ("s", "e") if direction=="s" else ("e", "s") #Получаем иды противоположных направления

        #print("h_f cInTP, aInTP, cDir, aDir: ", CurInTP, AthInTP,cur_dir, ath_dir )

        tpi = bd_time[2]
        day_id = bd_time[1]
        bd_timePoint = select_timePoint_byID( tpi ) #0id 1dayInfo_id 2id_start 3id_end 4cause

        if bd_timePoint: # вдруг мы не смогли получить к чему прикреплена запись..

            allTimesCurrentDir = select_time_byCauseID_and_Direction(tpi, cur_dir, 2) # Вернет самые последние сверху
            if len(allTimesCurrentDir) > 1:
                #Если там более 2х записей берем предпоследнюю 0-тек,1-нужная и берем оттуда ид записи и записываем его в таймпоинт
                #pos(Начальная точка или конечная точка) time_id, cause_id, day_id
                oldId = allTimesCurrentDir[1][CurInTP]
                update_timePoint_time_byPos(cur_dir, oldId, tpi, day_id)
                delete_time_byID(post_id)
                return True #Успешно отменилось действие
            
            else: # Если это единственная запись, то смотрим, что в другой ячейке 

                # Если вторая ячейка - это конец таймера, а мы удаляем начало таймера, то можно удалять tpi
                if ath_dir == "e":
                    delete_timePoint_byID(tpi) # Удаляем всю запись tpi (Удалятся все точки)
                    return True

                elif bd_timePoint[AthInTP] == 0: #Если противоположный пустой (Мб можно просто всю запись удалить и забить)
                    delete_timePoint_byID(tpi) # Удаляем всю запись tpi (Удалятся все точки)
                    return True

                else: # Если в другой ячейке написано начало таймера, а конец нам не нужен, то отчищаем информацию о конце.
                    
                    delete_time_byID(post_id) #Удаляем текущую точку и заменяем в точке времени ид на ноль
                    update_timePoint_time_byPos(cur_dir, 0, tpi, day_id) 
                    return True

        else: # Если не удалось получить данные о точке времени
            return False
    
    else: # Если не удалось найти запись по иду
        return False

