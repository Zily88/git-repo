# ------------------------------ Базы данных -----------------------------
#                        Использование row_factory

import sqlite3


# Создадим обработчик row_factory, возвращающий список данных, а не кортежей
# при выборе только одного поля из таблицы
def my_row_factory(cursor, row):
    d = {}
    print(cursor.description)
    print(row[0])
    if len(cursor.description) == 1:
        return row[0]
    else:
        return row    

con = sqlite3.connect(":memory:")

con.row_factory = my_row_factory
cur = con.cursor()

cur.execute('CREATE table USER(id integer primary key, name text)')

cur.execute('INSERT INTO USER(name) values (?)', ('petrushka',))
cur.execute('INSERT INTO USER(name) values (?)', ('barmalei',))
cur.execute('INSERT INTO USER(name) values (?)', ('alien',))
cur.execute('INSERT INTO USER(name) values (?)', ('scally',))
cur.execute('INSERT INTO USER(name) values (?)', ('molder',))
con.commit()


cur.execute("select * from USER as a")
print(cur.fetchall())
