# ------------------------------ Базы данных -----------------------------

# SQLAlchemy. Часть 1

import sys

# Проверим версию SQLAlchemy
try:
    import sqlalchemy
    print(sqlalchemy.__version__)
except ImportError:
    print('Библиотека SQLAlchemy не найдена')    
    sys.exit(13)

# ----------------------------------------------------------------------------

print(' ------ Классическое создание таблицы, класса и отображения ------')

# Работа с классическим отображением (Classical Mapping) #
##########################################################

from sqlalchemy import create_engine

# Создадим БД в памяти или в файле
# Флаг `echo` включает ведение лога через стандартный модуль `logging` Питона.
engine = create_engine('sqlite:///mydb.sqlite', echo=False)

# Импортируем необходимые классы (типы данных, таблицы, метаданные, ключи)
from sqlalchemy import Table, Column, Integer, String, MetaData

# Подготовим "запрос" на создание таблицы users внутри каталога MetaData
metadata = MetaData()
users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String),
    Column('password', String)
)

# Выполним запрос CREATE TABLE
metadata.create_all(engine)


# Создадим класс для отображения таблицы БД
class User:
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
       return "<User('%s','%s', '%s')>" % \
                    (self.name, self.fullname, self.password)


# Выполним связывание таблицы и класса-отображения
from sqlalchemy.orm import mapper
m = mapper(User, users_table)
print('Classic Mapping. Mapper: ', m)

# Создадим объект-пользователя
classic_user = User("Вася", "Василий", "qweasdzxc")
print('Classic Mapping. User: ', classic_user)
print('Classic Mapping. User ID: ', classic_user.id)

# ----------------------------------------------------------------------------

print(' ------ Декларативное создание таблицы и класса ------')

# Декларативное создание таблицы, класса и отображения #
########################################################

# Для использования декларативного стиля необходима функция declarative_base
from sqlalchemy.ext.declarative import declarative_base

# Функция declarative_base создаёт базовый класс для декларативной работы
Base = declarative_base()

# На основании базового класса можно создавать необходимые классы
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password
    def __repr__(self):
        return "<User('%s','%s', '%s')>" % \
                     (self.name, self.fullname, self.password)

# Таблица доступна через атрибут класса
users_table = User.__table__
print('Declarative. Table:', users_table)

# Метеданные доступны через класс Base
metadata = Base.metadata
print('Declarative. Metadata:', metadata)

print(' ----------------- Работа с сессией ---------------------------------')

#                   Создание сессии                       #
###########################################################

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)


# Класс Session будет создавать Session-объекты, которые привязаны к базе данных
session = Session()
print('Session:', session)

#                   Добавление новых объектов                      #
####################################################################

# Для сохранения объекта User, нужно добавить его к имеющейся сессии
admin_user = User("vasia", "Vasiliy Pypkin", "vasia2000")
session.add(admin_user)

# Объект созданный через классическое отображение
# также сохраняется в БД через сессию
session.add(classic_user)

# Простой запрос
q_user = session.query(User).filter_by(name="vasia").first()
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
print('Simple query:', q_user)              
print('Simple query:', type(q_user)) 
print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

# Добавить сразу несколько записей
session.add_all([User("kolia", "Cool Kolian[S.A.]","kolia$$$"),
                 User("zina", "Zina Korzina", "zk18")])        

# Сессия "знает" об изменениях пользователя
admin_user.password = "-=VP2001=-"
print('Session. Changed objects:', session.dirty)

# Атрибут `new` хранит объекты, ожидающие сохранения в базу данных
print('Session. New objects:', session.new)

# Метод commit() фиксирует транзакцию, сохраняя оставшиеся изменения в базу
session.commit()

print('User ID after commit:', admin_user.id)
session.delete(admin_user)
session.commit()

session.rollback()

