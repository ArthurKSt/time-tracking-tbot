import sqlite3

# для разделения работы на несколько компаний можно создавать разные базы данных и разных ботов

from constants.config import DB_LOG as dir


# dir = r'store/Kezo_log.db'

# conn = sqlite3.connect(r'store/bd.db')
conn = sqlite3.connect(dir)
cur = conn.cursor()


# Лог в бд:
#   Лог
#     ИдЗаписи
#     КлючевыеСлова #Для быстрого поиска, если "не пришел" или "Обычное информирование о запуске"
#     ТекстЗаписи #основная строка Имя.Суть.Текст(или ответ) Пользователь..Не пришел.. Потому что..
#     Время
#     сКемСвязано #Ид пользователя (если есть)
cur.execute("""CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY,
    words TEXT,
    text TEXT,
    date TEXT,
    time INTEGER,
    teleg_id INTEGER );
""")
conn.commit()

#   Дополнения: - хранит изменения со временем (если человек пришел позже, к примеру)
#     ИдДополнения
#     ИдЗаписи
#     ТекстДополнения
#     Время
cur.execute("""CREATE TABLE IF NOT EXISTS addition (
    id INTEGER PRIMARY KEY,
    id_log INTEGER,
    text TEXT,
    time INTEGER,

    FOREIGN KEY (id_log) REFERENCES log (id) ON DELETE CASCADE
    );
""")
conn.commit()