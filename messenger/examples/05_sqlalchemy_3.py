# ------------------------------ Базы данных -----------------------------

# SQLAlchemy. Часть 3

# Создание БД. Добавление, редактирование, удаление записей
# Реализация связи "Многие ко многим"

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import relationship

# Создадим простую БД "Библиотека" - будет храниться информация о книгах и авторах
engine = create_engine('sqlite:///Library.db')
Session = sessionmaker(bind=engine)

# Функция declarative_base создаёт базовый класс для декларативной работы
Base = declarative_base()

# Определим классы, которые соответствуют таблицам в БД

# Поскольку между сущностями Автор - Книга существует отношение "многие ко многим"
# (один автор может написать несколько книг,
# одна книга может быть написана несколькими авторами),
# то нужна таблица-связка:
association_table = Table('BookAuthor', Base.metadata,
                   Column('author_id', Integer, ForeignKey('Author.AuthorId')),
                   Column('book_id', Integer, ForeignKey('Book.BookId'))
)

# много - много - пригодиться дома
# class AuthorBook(Base):
#     AutorBookId = Column(Integer, primary_key=True)
#     AuthorId = Column(Integer, ForeignKey('Author.AuthorId'))
#     BookId = Column(Integer, ForeignKey('Book.BookId'))


# Класс Автор будет выступать первичным классом во взаимодействии Автор-Книга
class Author(Base):
    __tablename__ = 'Author'
    AuthorId = Column(Integer, primary_key=True)
    Name = Column(String)

    def __init__(self, name):
        self.Name = name

    def __repr__(self):
        return "<Author ('%s')>" % self.Name

# Класс Книга - дочерний по отношению к Автору
class Book(Base):
    __tablename__ = 'Book'
    BookId = Column(Integer, primary_key=True)
    Title = Column(String)

    # Создание взаимосвязи на уровне ORM через функцию relationship.
    # Параметр secondary указывает таблицу-связку.
    # Параметр backref указывает ORM использовать аргумент secondary
    #                                     для обратной связи от Автора к Книгам
    Authors = relationship("Author",
                           secondary=association_table, 
                           backref="Books")

    def __init__(self, title, authors):
        self.Title = title
        self.Authors = authors

    def __repr__(self):
        return "<Book ('%s')>" % self.Title

def print_books(session):
    ''' Печать книг в библиотеке
    '''
    print(' -- Книги в библиотеке --')
    for book in session.query(Book):
        print('"{}"'.format(book.Title))
        print(' Authors:', ', '.join(author.Name for author in book.Authors))

# Создание БД, объявленной в декларативном стиле
Base.metadata.create_all(engine)

session = Session()

# Добавление данных в БД
author_1 = Author('Erich Gamma')
author_2 = Author('Richard Helm')
author_3 = Author('Ralph Johnson')
author_4 = Author('John Vlissides')

# При создании книги авторов нужно передавать в списке - 
# при этом ORM автоматически выполнит заполнение таблицы-связи.
book_1 = Book('Design Patterns', [author_1, author_2, author_3, author_4])

# Для сохранения данные нужно сначала добавить в сессию
session.add_all([author_1, author_2, author_3, author_4, book_1])

author_5 = Author('David Beazley')
author_6 = Author('Brian K. Jones')
book_2 = Book('Python Cookbook', [author_5, author_6])
book_3 = Book('Python. Essential Reference', [author_5])

session.add_all([author_5, author_6, book_2, book_3])

# После выполнения commit() все имеющиеся данные будут сохранены в БД
session.commit()

print_books(session)


print(' -- Изменим книгу в библиотеке --')
print(book_3.Title, book_3.BookId)

# Изменение объекта выполняется простым изменением атрибутов объекта и последующим commit()
book_3.Title = 'Python. Essential Reference. Fourth Edition'
book_3.Authors = [author_5, author_1]
print('Session.dirty:', session.dirty)
session.commit()

print_books(session)

print(' -- Удалим книгу из библиотеки --')
print(book_2.Title, book_2.BookId)

# Удаление объекта из БД выполняется удалением объекта из сессии и последующим commit()
# При удалении ORM автоматически удалит соответствующие записи из таблицы-связки.
session.delete(book_2)
print('Session.deleted:', session.deleted)
session.commit()

print_books(session)
