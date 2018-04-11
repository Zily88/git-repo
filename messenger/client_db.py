from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from  sqlalchemy.exc import IntegrityError


class ClientDB:



    def __init__(self, user_name):
        self.Base = declarative_base()
        # self.Base2 = declarative_base()
        self.user_name = user_name

        class Contact(self.Base):
            __tablename__ = 'contacts'
            id = Column(Integer, primary_key=True, autoincrement=True)
            name = Column(String, unique=True)
            nick = Column(String)

            def __init__(self, id, name, nick):
                self.id = id
                self.name = name
                self.nick = nick

        self.Contact = Contact

        class MessageHistory(self.Base):
            __tablename__ = 'mesages'
            id = Column(Integer, primary_key=True, autoincrement=True)
            interlocutor = Column(Integer, ForeignKey(self.Contact.id))
            message = Column(String)
            time = Column(Integer)
            receiver = Column(Boolean)

            def __init__(self, interlocutor, message, time, receiver):
                self.interlocutor = interlocutor
                self.message = message
                self.time = time
                self.receiver = receiver

        self.MessageHistory = MessageHistory

        # class ChatHistory(self.Base):
        #     __tablename__ = 'chat_mesages'
        #     id = Column(Integer, primary_key=True, autoincrement=True)
        #     interlocutor = Column(Integer, ForeignKey(self.Contact.id))
        #     message = Column(String)
        #     time = Column(Integer)
        #     receiver = Column(Boolean)
        #
        #     def __init__(self, interlocutor, message, time, receiver):
        #         self.interlocutor = interlocutor
        #         self.message = message
        #         self.time = time
        #         self.receiver = receiver

    def add_contact(self, id, name, nick):
        self.session.add(self.Contact(id, name, nick))
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def del_contact(self, name):
        contact_id = self.select_user_id(name)
        contact = self.session.query(self.Contact).filter(self.Contact.id == contact_id).one()
        self.session.delete(contact)
        self.session.commit()

    def del_messages(self, name):
        print('Начинаем тереть')
        print(name)
        user_id = self.select_user_id(name)
        messages = self.session.query(self.MessageHistory).filter(self.MessageHistory.interlocutor == user_id).all()
        for msg in messages:
            print('Затираем')
            self.session.delete(msg)
        self.session.commit()

    def add_mesage(self, interlocutor, message, time, receiver):
        id = self.select_user_id(interlocutor)
        self.session.add(self.MessageHistory(id, message, time, receiver))
        self.session.commit()

    def get_contacts(self):
        contacts = self.session.query(self.Contact).all()
        return contacts
        # for contact in contacts:
        #     print(contact.nick)

    def select_user_id(self, user_name):
        try:
            user = self.session.query(self.Contact).filter(self.Contact.name == user_name).one()
        except NoResultFound:
            print('не существует таких')
        else:
            return user.id

    def select_user_name(self, id):
        try:
            print('Selectinuser by id ' + str(id))
            user = self.session.query(self.Contact).filter(self.Contact.id == id).one()
        except NoResultFound:
            pass
        else:
            print(user)
            return user.name

    def get_messages(self, interlocutor):
        id = self.select_user_id(interlocutor)
        messages = self.session.query(self.MessageHistory).filter(self.MessageHistory.interlocutor == id).all()
        # my_messages = self.session.query(self.MessageHistory).filter(self.MessageHistory.interlocutor == id and self.MessageHistory.receiver == 1).all()
        # for message in messages:
        #     print(message.message)
        # for message in my_messages:
        #     print(message.message)
        return messages

    def start(self):
        self.engine = create_engine('sqlite:///{}.sqlite'.format(self.user_name))
        # self.engine2 = create_engine('sqlite:///messages.sqlite')
        Session = sessionmaker(bind=self.engine)
        # Session2 = sessionmaker(bind=self.engine2)
        self.session = Session()
        # self.session2 = Session2()
        self.Base.metadata.create_all(self.engine)
        # self.Base2.metadata.create_all(self.engine)


# mydb = ClientDB()
# mydb.start()
# mydb.add_contact(5, 'vofka', 'morkofka')
# mydb.get_contacts()