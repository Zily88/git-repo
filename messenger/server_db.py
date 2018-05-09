# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import exists
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy.orm.exc import NoResultFound
import time
import traceback


class ServerDB:
    def add_user(self, user_name):
        try:
            self.session.add(self.User(user_name, user_name, '12345'))
            self.session.commit()
        except IntegrityError:
            self.session.rollback()


    def add_history(self, user_name, time, ip):
        self.session.add(self.History(user_name, time, ip))
        self.session.commit()

    def add_contact(self, owner, contact, all_right, contact_exists_error, no_user_error, arg):
        try:
            self.session.add(self.Contact(owner, contact))
            self.session.commit()
            all_right(arg)
        except IntegrityError as e:
            e = str(e.orig)
            if '1062' in e:
                contact_exists_error(arg)
                self.session.rollback()
            elif '1452' in e:
                no_user_error(arg)
                self.session.rollback()

    def get_contact_list(self, user_name):
        print('мы тут')
        user_id = self.select_user_id(user_name)
        lst = self.session.query(self.Contact, self.User).filter(self.Contact.owner_id == user_id).join(self.User, self.User.id == self.Contact.contact_id).all()
        for user in lst:
            print(user.User.name)
        return lst

    def exists_user(self, user_name):
        return self.session.query(exists().where(self.User.name == user_name)).scalar()

    Base = declarative_base()

    def select_user_id(self, user_name):
        try:
            user = self.session.query(self.User).filter(self.User.name == user_name).one()
        except NoResultFound:
            pass
        else:
            return user.id

    def select_user_nickname(self, user_name):
        try:
            user = self.session.query(self.User).filter(self.User.name == user_name).one()
        except NoResultFound:
            pass
        else:
            return user.nickname

    def select_user_name(self, id):
        try:
            user = self.session.query(self.User).filter(self.User.id == id).one()
        except NoResultFound:
            pass
        else:
            return user.name

    def delete_contact(self, owner, contact):
        owner_id = self.select_user_id(owner)
        contact_id = self.select_user_id(contact)
        contact = self.session.query(self.Contact).filter(self.Contact.owner_id == owner_id)\
        .filter(self.Contact.contact_id == contact_id).one()
        self.session.delete(contact)
        self.session.commit()


    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(15), nullable=False, unique=True)
        nickname = Column(String(15), nullable=False, unique=True)
        password = Column(String(25), nullable=False)


        def __init__(self, name, fullname, password):
            self.name = name
            self.nickname = fullname
            self.password = password

    class History(Base):
        __tablename__ = 'users_history'
        id = Column(Integer, primary_key=True, autoincrement=True)
        user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        time = Column(Integer, nullable=False)
        ip = Column(String(15), nullable=False)

        def __init__(self, user_id, time, ip):
            self.user_id = user_id
            self.time = time
            self.ip = ip

    class Contact(Base):
        __tablename__ = 'contacts'
        owner_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
        contact_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)

        def __init__(self, owner, contact):
            self.owner_id = owner
            self.contact_id = contact

    def start(self, name, user, password, error):
        try:
            self.engine = create_engine('mysql://{}:{}@localhost:3306/{}'.format(user, password, name), echo=False)
            if not database_exists(self.engine.url):
                create_database(self.engine.url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            self.Base.metadata.create_all(self.engine)
        except OperationalError as e:
            print('Неверное имя польователя или пароль')
            error()


    def stop(self):
        self.session.close()







