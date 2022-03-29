# Задачи будут храниться в бд.

#   Задача:
#     ИдЗадачи 
#     ТекстЗадачи (Для логов) (type:text) type= 0-Обычная, 1-один раз в день
#     ВремяСоздания 
#     ВремяАктуальности (0-всегда или конкретная дата)
#     ВремяУдалить (0 - не удалять)
#     Кому (Ур:Знак:ИДилиЗвезда) "(0:=:*)-для всех гостей","(1:+:*)-для всех кроме гостей","(0:+:Ид) для конкр.человека"
    
#   Результат:
#     ИдРезультата
#     ИдЗадачи
#     ВремяРезультата
#     ТекстРезультата (статус:сообщение)


import sqlite3

# для разделения работы на несколько компаний можно создавать разные базы данных и разных ботов
# conn = sqlite3.connect(r'store/bd.db')
from constants.config import DB_TASK as dir
conn = sqlite3.connect(r''+dir)
cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY,
    task_text TEXT,
    create_time INTEGER,
    actual_time INTEGER,
    remove_time INTEGER,
    for_who TEXT );
""")
conn.commit()


cur.execute("""CREATE TABLE IF NOT EXISTS task_result (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    result_time INTEGER,
    result_text TEXT,
    
    FOREIGN KEY (task_id) REFERENCES task_result (id) ON DELETE CASCADE
    );
""")
conn.commit()