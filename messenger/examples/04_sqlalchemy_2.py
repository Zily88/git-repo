# ------------------------------ Базы данных -----------------------------

# SQLAlchemy. Часть 2

# Работа со связями таблиц и запросами

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import relationship

# Воспользуемся Chinook Database
engine = create_engine('sqlite:///Chinook_Sqlite.sqlite', echo=True)
Session = sessionmaker(bind=engine)


# Функция declarative_base создаёт базовый класс для декларативной работы
Base = declarative_base()

# ----  Структуру БД см. в файле ChinookDatabaseSchema1.1.png ----

# Определим классы, которые соответствуют таблицам в БД

class Artist(Base):
    __tablename__ = 'Artist'
    ArtistId = Column(Integer, primary_key=True)
    Name = Column(String)

    def __init__(self, name):
        self.Name = name

    def __repr__(self):
        return "<Artist ('%s')>" % self.Name


class Album(Base):
    __tablename__ = 'Album'
    AlbumId = Column(Integer, primary_key=True)
    Title = Column(String)

    # Внешний ключ указывается как аргумент для столбца таблицы
    # Указание внешнего ключа обязывает,
    # чтобы соответствующая запись была во внешней таблице
    ArtistId = Column(Integer, ForeignKey('Artist.ArtistId'))

    # Функция relationship() даёт указание ORM, 
    # что класс Album связан с классом Artist через атрибут Album.Artist.
    # Параметр back_populates указывается для реализации обратной связи из класса Artist
    Artist = relationship("Artist", back_populates="Albums")

    def __init__(self, title, fullname, password):
        self.Title = title

    def __repr__(self):
        return "<Album ('%s')>" % self.Title


class Track(Base):
    __tablename__ = 'Track'
    TrackId = Column(Integer, primary_key=True)
    Name = Column(String)
    AlbumId = Column(Integer, ForeignKey('Album.AlbumId'))
    MediaTypeId = Column(Integer)
    GenreId = Column(Integer)
    Composer = Column(String)
    Milliseconds = Column(Integer)
    Bytes = Column(Integer)
    UnitPrice = Column(Numeric(10,2))

    Album = relationship("Album", back_populates="Tracks")

    def __init__(self, name, album_id, media_id, genre_id, composer, msec, bytes_, price):
        self.Name = name
        self.AlbumId = album_id
        self.MediaTypeId = media_id
        self.GenreId = genre_id
        self.Composer = composer
        self.Milliseconds = msec
        self.Bytes = bytes_
        self.UnitPrice = price

    def __repr__(self):
        # При реализованных связях на уровне ORM 
        return "<Track ('%s' - %s)>" % (self.Album.Artist.Name, self.Name)


# Указываем дополнительные связи для ORM, 
# чтобы данные можно было получать в двух направлениях,
# т.е., например, artist.Albums будет давать список всех альбомов конкретного исполнителя,
# а album.Artist будет предоставлять непосредственно исполнителя альбома.

# Объявление дополнительных атрибутов классов выполняется здесь (вне описания класса),
# потому что при объявление внутри класса привело бы к циклической зависимости, 
# когда атрибут ссылается на класс, который ещё не определён.
Artist.Albums = relationship("Album", order_by=Album.AlbumId, back_populates="Artist")
Album.Tracks = relationship("Track", back_populates="Album")

# Создаём сессию
session = Session()

# -------------- Выполним различные запросы к БД ----------------------------

print(' ---- Все доступные исполнители ----')
# q_artists = session.query(Artist).all()
# print(q_artists)

print(' ---- Все альбомы одного исполнителя ----')
artist = session.query(Artist).filter(Artist.Name=='AC/DC').one()
print('Исполнитель:', artist.Name, artist.ArtistId)
# 
#albums = session.query(Album).filter(Album.AlbumId==artist.AlbumId)
albums = artist.Albums
print(' Альбомы:', albums)


album = albums[0]
print(' ---- Все треки с альбома {} ---- '.format(album.Title))
tracks = session.query(Track).filter(Track.Album==album).all()
print(tracks)

print(' -- Подсчёт количества записей в запросе --')
artist = session.query(Artist).filter(Artist.Name=='Lenny Kravitz').one()
track_count = session.query(Track).filter(Track.Album==album).count() 
print(' У исполнителя {} найдено {} треков'.format(artist, track_count))

print(' --- Все треки с упоминанием слова "rock" ---')
# Можно итерироваться сразу по результату запроса без извлечения all()
for track in session.query(Track).filter(Track.Name.like('%rock%')):
    print("{} - {}".format(track.Album.Artist.Name, track.Name))

print(' --- Некоторые треки с упоминанием слова "love" ---')
# Можно задавать порядок сортировки методом order_by() (аналог ORDER BY в SQL),
# а также использовать Python-срез (аналог параметров LIMIT и OFFSET в SQL)
for track in session.query(Track).order_by(Track.Name).filter(Track.Name.like('%love%'))[2:10]:
    print("{} - {}".format(track.Album.Artist.Name, track.Name))


# В случае, если результат выборки содержит несколько записей,
# то применение метода one() приведёт к исключению MultipleResultsFound:

# track = session.query(Track).order_by(Track.Name).filter(Track.Name.like('%love%')).one()
#           >>> sqlalchemy.orm.exc.MultipleResultsFound: Multiple rows were found for one()


print(' --- Усложнённые условия выборки ---')
from sqlalchemy import or_, and_

print(' --- Треки, содержащие love или war в названии ---')
for track in session.query(Track).filter(or_(Track.Name.like('%love%'), Track.Name.like('%war%'))):
    print("{} - {}".format(track.Album.Artist.Name, track.Name))

print(' --- Треки указанных исполнителей размером больше 500000 байт ---')
artists = session.query(Artist).filter(Artist.Name.in_(['ABBA', 'AC/DC', 'A-HA', 'Queen']))

# Напрямую применить операцию IN для связанных таблиц не получится:
# albums = session.query(Album).filter(Album.Artist.in_(artists))

# Поэтому нужно сначала получить список id исполнителей,
# и уже для этого списка применить оператор IN:

artists = session.query(Artist.ArtistId).filter(Artist.Name.in_(['ABBA', 'AC/DC', 'A-HA', 'Queen']))
albums = session.query(Album.AlbumId).filter(Album.ArtistId.in_(artists))

print('НАЧАЛО запроса')
results = session.query(Track).filter(Track.AlbumId.in_(albums))
new_results = results.filter(Track.Bytes > 500000)
print('КОНЕЦ запроса')
print(new_results)
#print('КОНЕЦ запроса')
#for track in new_results:
    #print("{} - {} / {} байт /".format(track.Album.Artist.Name, track.Name, track.Bytes))


