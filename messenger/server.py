from socket import socket, AF_INET, SOCK_STREAM
from jim_protocol import JIM, JIMPresence, JIMMessage, JIMResponse, OK, JIMAddContact, JIMDelContact, WRONG_REQUEST, FORBIDDEN, GONE, NOT_FOUND, CONFLICT, JIMCreateChat, JIMJoinChat, JIMLeaveChat, CREATED, JIMGetContacts, JIMContactList, JIMRespect, ACCEPTED, ADDED, MESSAGE_SIZE, SENDED, NOT_ADDED, NOT_SENDED, DELETED, JIMInviteChat, INVITED, JIMGetUsers, ACCEPT
from server_db import ServerDB
from select import select
import sys
from server_chat import Chat
from user import User
from queue import Queue
from threading import Thread

PORT = 7777
HOST = ''


class Server:

    def __init__(self):
        self.clients = []
        self.chats = []
        self.queue = Queue()
        # self.t1 = Thread(target=self.really_receiv)
        # self.t2 = Thread(target=self.hope)
        # self.t2 = Thread(target=self.really_send)
        # self.t1.start()
        # self.t2.start()

    def input_db(self):
        self.user = input('Введите имя пользователя БД: ')
        self.password = input('Введите пароль БД: ')
        self.name = input('Введите название БД: ')
        self.db = ServerDB()
        self.db.start(self.name, self.user, self.password, self.input_db)

    def good_func(self, user):
        try:
            self.clients.remove(user)
        # Откуда except!?
        except ValueError:
            pass

    # def hope(self):
    #     while True:
    #         r = []
    #         w = []
    #         e = []
    #         try:
    #             r, w, e = select(self.get_sckt_list(), w, e, 0)
    #         except Exception:
    #             pass
    #         for sckt in r:
    #             try:
    #                 msg = self.receive(sckt)
    #             except ConnectionResetError:
    #                 for user in self.clients:
    #                     if user.sckt == sckt:
    #                         self.clients.remove(user)
    #             else:
    #                 if isinstance(msg, JIMRespect):
    #                     user = self.get_user(msg.user_name)
    #                     user.queue.put(user.name + '.OK')



    # def send(self, sock, *answer):
    #     for msg in answer:
    #         sock.send(msg.packing())
            # resp = self.queue.get()
            # if resp == 'OK':
            #     continue
            # else:
            #     break

    # def chat_send(self):
    #     for chat in self.chats:
    #         chat.done()

    # def really_send(self):
    #     for user in self.clients:
    #         if not user.is_empty():
    #             self.send(user.sckt, *user.msg)
    #     self.clear()

    def get_user(self, name):
        for user in self.clients:
            if user.name == name:
                return user

    def get_user_by_socket(self, sckt):
        for user in self.clients:
            if user.sckt == sckt:
                return user

    def get_chat(self, room):
        for chat in self.chats:
            if chat.name == room:
                return chat

    def get_sckt_list(self):
        lst = []
        for user in self.clients:
            lst.append(user.sckt)
        return lst

    def get_user_list(self):
        lst = []
        for user in self.clients:
            lst.append(user.name)
        return lst

    def get_chat_list(self):
        lst = []
        for chat in self.chats:
            lst.append(chat.name)
        return lst

    def clear(self):
        for chat in self.chats:
            if chat.is_empty():
                self.chats.remove(chat)

    def join(self):
        for user in self.clients:
            user.thread.join()

    def receive(self, sock):
        # try:
            data = sock.recv(MESSAGE_SIZE)
            return JIM.unpacking(data)
        # except BlockingIOError:
        #     pass

    def start(self):
        self.input_db()
        print('Соединение с БД установленно')
        self.serv = socket(AF_INET, SOCK_STREAM)
        self.serv.bind((HOST, PORT))
        self.serv.listen(10)
        self.serv.settimeout(0.1)
        print('Сервер запущен')


        while True:
            try:
                client_sock, client_addr = self.serv.accept()
                print('соединение с {} установленно'.format(client_addr))
            except OSError:
                pass
            else:
                try:
                    msg = self.receive(client_sock)
                except ConnectionResetError:
                    pass
                else:
                    if isinstance(msg, JIMPresence):
                        user_name = msg.user_name
                        time = msg.time
                        self.db.add_user(user_name)
                        new_user = User(user_name, client_sock, self.good_func)#, self.t1)
                        self.clients.append(new_user)
                        if self.db.exists_user(user_name):
                            user_id = self.db.select_user_id(user_name)
                            self.db.add_history(user_id, time, client_addr[0])
                        answer = JIMResponse(OK, 'добро пожаловать, {}'.format(user_name))
                        new_user.add_msg(answer)
                        # new_user.add_respect()
                        new_user.thread.start()
                # message = self.receive(client_sock)
                # if isinstance(message, JIMGetContacts):
                #     user_name = message.user_name
                #     contact_list = self.db.get_contact_list(user_name)
                #     answer = JIMResponse(OK, quantity=len(contact_list))
                #
                #     new_user.add_msg(answer)
                #     for contact in contact_list:
                #         new_user.add_msg(JIMContactList(contact.User.name, contact.User.nickname, contact.User.id))



            finally:

                #serv.setblocking(0)

                # for_send = {}
                # for_send_from_chats = {}
                r = []
                w = []
                e = []
                try:
                    r, w, e = select(self.get_sckt_list(), w, e, 0)
                except Exception:
                    pass

                #print(w)

                def contact_exists_error(user):
                    user.add_msg(JIMResponse(NOT_ADDED, 'этот контакт уже существует'))
                    # user.add_respect()

                def no_user_error(user):
                    user.add_msg(JIMResponse(NOT_ADDED, 'такого пользователя не существует'))
                    # user.add_respect()

                # def user_offline_error(user):
                #     for_send.setdefault(user, [])
                #     for_send[user].append(JIMResponse(GONE))
                #

                    # user.add_respect()

                for sckt in r:
                    try:
                        msg = self.receive(sckt)
                    except ConnectionResetError:
                        user = self.get_user_by_socket(sckt)
                        self.clients.remove(user)
                        user.stop()
                    else:
                        user = self.get_user_by_socket(sckt)
                        if isinstance(msg, JIMMessage):
                            receiver = self.get_user(msg.receiver)
                            sender = self.get_user(msg.user_name)

                            if receiver:

                                sender.add_msg(JIMResponse(SENDED))
                                # sender.add_respect()
                                receiver.add_msg(msg)
                                # receiver.add_respect()
                                # if self.clients[msg.receiver] in w:
                                #     ok(user)
                                #     for_send.setdefault(self.clients[msg.receiver], [])
                                #     for_send[self.clients[msg.receiver]].append(msg)
                                # else:
                                #     print('Чтото неведомое')
                            elif msg.receiver.startswith('#'):
                                room = str(msg.receiver[1:])
                                room = self.get_chat(room)
                                if room:
                                    if sender in room.users:
                                        room.add_message(msg)
                                        sender.add_msg(JIMResponse(SENDED))
                                        room.done(sender)
                                        # sender.del_msg(msg)
                                    else:
                                        sender.add_msg(JIMResponse(CONFLICT, 'вы не состоите в этом чате'))
                                else:
                                    sender.add_msg(JIMResponse(NOT_FOUND, 'такого чата не существует'))
                            elif msg.receiver.startswith('<server_chat.Chat object at'):
                                room = str(msg.receiver)
                                room = self.get_chat(room)
                                if room:
                                    if sender in room.users:
                                        room.add_message(msg)
                                        sender.add_msg(JIMResponse(SENDED))
                                        room.done(sender)
                                        # sender.del_msg(msg)
                                    else:
                                        sender.add_msg(JIMResponse(CONFLICT, 'вы не состоите в этом чате'))
                                else:
                                    sender.add_msg(JIMResponse(NOT_FOUND, 'такого чата не существует'))


                            else:
                                if self.db.exists_user(msg.receiver):
                                    sender.add_msg(JIMResponse(NOT_SENDED, 'пользователь оффлайн'))
                                    # sender.add_respect()
                                else:
                                    sender.add_msg(JIMResponse(NOT_SENDED, 'такого пользователя не существует'))
                                    # sender.add_respect()



                        elif isinstance(msg, JIMAddContact):
                            owner = self.db.select_user_id(msg.user_name)
                            contact = self.db.select_user_id(msg.contact)
                            user = self.get_user(msg.user_name)

                            def ok(user):
                                user.add_msg(JIMResponse(ADDED, quantity=contact))
                            if owner and contact:
                                self.db.add_contact(owner, contact, ok, contact_exists_error, no_user_error, user)
                            else:
                                no_user_error(user)

                        elif isinstance(msg, JIMGetContacts):
                            contacts = self.db.get_contact_list(msg.user_name)
                            user = self.get_user(msg.user_name)
                            if contacts:
                                user.add_msg(JIMResponse(ACCEPTED, quantity=len(contacts)))
                                # user.add_respect()
                                # msg = self.receive(user.sckt)
                                # if isinstance(msg, JIMRespect):
                                #     user.add_msg(JIMResponse(OK))
                                    # user.add_respect()
                                for contact in contacts:
                                    user.add_msg(JIMContactList(contact.User.name, contact.User.nickname, contact.User.id))
                                    # user.add_respect()
                                    # msg = self.receive(user.sckt)
                                    # if isinstance(msg, JIMRespect):
                                    #     user.add_msg(OK)
                                    #     user.add_respect()
                                    #     continue
                                    # else:
                                    #     break
                            else:
                                user.add_msg(JIMResponse(NOT_FOUND, 'у вас нет сохранённых контактов'))
                                # user.add_respect()
                        elif isinstance(msg, JIMGetUsers):
                            chat_name = msg.room
                            chat = self.get_chat(chat_name)
                            contacts = chat.get_users_list()
                            my_id = self.db.select_user_id(user.name)
                            if contacts:
                                user.add_msg(JIMResponse(ACCEPT, quantity=(len(contacts) - 1)))
                                # user.add_respect()
                                # msg = self.receive(user.sckt)
                                # if isinstance(msg, JIMRespect):
                                #     user.add_msg(JIMResponse(OK))
                                    # user.add_respect()
                                for contact in contacts:
                                    user_id = self.db.select_user_id(contact)
                                    if user_id == my_id:
                                        continue
                                    user.add_msg(JIMResponse(ACCEPT, chat_name, user_id))
                                    # user.add_respect()
                                    # msg = self.receive(user.sckt)
                                    # if isinstance(msg, JIMRespect):
                                    #     user.add_msg(OK)
                                    #     user.add_respect()
                                    #     continue
                                    # else:
                                    #     break
                            else:
                                user.add_msg(JIMResponse(NOT_FOUND, 'у вас нет сохранённых контактов'))
                                # user.add_respect()

                        elif isinstance(msg, JIMDelContact):
                            user = self.get_user(msg.user_name)
                            self.db.delete_contact(msg.user_name, msg.contact)
                            user.add_msg(JIMResponse(DELETED))

                        elif isinstance(msg, JIMResponse):
                            if msg.code == INVITED:
                                chat = self.get_chat(msg.message)
                                chat.add_user(user)
                                id = self.db.select_user_id(user.name)
                                print('id = ' + str(id))
                                new_msg = JIMResponse(INVITED, chat.name, id)
                                chat.add_message(new_msg)
                                chat.done(user)

                        elif isinstance(msg, JIMCreateChat):
                            sender = self.get_user(msg.user_name)
                            if msg.room:
                                if msg.room not in self.get_chat_list():
                                    chat = Chat(msg.room)
                                    user = self.get_user(msg.user_name)
                                    chat.add_user(user)
                                    self.chats.append(chat)
                                # ok(user)
                                    sender.add_msg(JIMResponse(CREATED))
                                    # sender.add_respect()
                                else:
                                    sender.add_msg(JIMResponse(CONFLICT, 'такой чат уже существует'))
                                    # sender.add_respect()
                            else:
                                chat = Chat()
                                chat.add_user(sender)
                                self.chats.append(chat)
                                sender.add_msg(JIMResponse(CREATED, chat.name))

                #
                        elif isinstance(msg, JIMJoinChat):
                            sender = self.get_user(msg.user_name)
                            if msg.room in self.get_chat_list():
                                # проверку на сущствование чата
                                chat = self.get_chat(msg.room)
                                user = self.get_user(msg.user_name)
                                if user not in chat.users:
                                    chat.add_user(user)
                            # self.chats[msg.room].add_user(msg.user_name, user)
                            # ok(user)
                                    sender.add_msg(JIMResponse(OK))
                                    # sender.add_respect()
                                else:
                                    sender.add_msg(JIMResponse(CONFLICT, 'вы уже состоите в этом чате'))
                                    # sender.add_respect()
                            else:
                                sender.add_msg(JIMResponse(NOT_FOUND, 'такого чата не существует'))
                                # sender.add_respect()

                        elif isinstance(msg, JIMInviteChat):
                            receiver = self.get_user(msg.contact)
                            if receiver:
                                receiver.add_msg(msg)
                            else:
                                sender = self.get_user(msg.user_name)
                                sender.add_msg(JIMResponse(NOT_SENDED, 'пользователь оффлайн'))

                        elif isinstance(msg, JIMLeaveChat):
                            user = self.get_user(msg.user_name)
                            if msg.room in self.get_chat_list():
                                chat = self.get_chat(msg.room)
                                if user in chat.users:
                                    chat.del_user(user)
                                    user.add_msg(JIMResponse(OK))
                                    # user.add_respect()
                                else:
                                    user.add_msg(JIMResponse(CONFLICT, 'вы не состоите в данном чате'))
                                    # user.add_respect()
                            else:
                                user.add_msg(JIMResponse(NOT_FOUND, 'такого чата не существует'))
                                # user.add_respect()

                #
                # for chat in self.chats.values():
                #     for_send_from_chats = chat.done()
                #     if r:
                #         for user in w:
                #             if user in for_send_from_chats:
                #                 for msg in for_send_from_chats[user]:
                #                     try:
                #                         self.send(user, msg)
                #                     except ConnectionResetError:
                #                         key = None
                #                         for k, v in self.clients.items():
                #                             if v == user:
                #                                 key = k
                #                         self.clients.pop(key)
                #
                # if r:
                #     for user in w:
                #         if user in for_send:
                #             for msg in for_send[user]:
                #                 try:
                #                     self.send(user, msg)
                #                 except ConnectionResetError:
                #                     key = None
                #                     for k, v in self.clients.items():
                #                         if v == user:
                #                             key = k
                #                     self.clients.pop(key)
            # self.chat_send()
            # self.really_send()
            # self.t2.join()
            # self.join()
            self.clear()






server = Server()
server.start()
# server.t2.start()
# server.t1.start()
# server.t2.start()
