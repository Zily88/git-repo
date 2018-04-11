from socket import socket, AF_INET, SOCK_STREAM
from jim_protocol import JIM, JIMPresence, JIMMessage, JIMResponse, OK, JIMAddContact, JIMDelContact, WRONG_REQUEST, FORBIDDEN, GONE, NOT_FOUND, CONFLICT, JIMCreateChat, JIMLeaveChat, JIMJoinChat, CREATED, JIMGetContacts, ACCEPTED, JIMContactList, JIMRespect, ADDED, MESSAGE_SIZE, SENDED
from threading import Thread
from queue import Queue
from client_db import ClientDB


class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.sckt = socket(AF_INET, SOCK_STREAM)
        self.queue = Queue()
        self.sended = False

    def name(self):
        self.user_name = input('Введите имя (не длиннее 15 символов): ')
        if self.user_name:
            if len(self.user_name) < 16:
                self.db = ClientDB(self.user_name)
                return
            else:
                print('Слишком длинное имя')
                self.name()
        else:
            self.name()

    def add_contact(self, contact):
        msg = JIMAddContact(self.user_name, contact).packing()
        self.sckt.send(msg)

    def get_contacts(self):
        msg = JIMGetContacts(self.user_name).packing()
        self.sckt.send(msg)
        msg = self.sckt.recv(MESSAGE_SIZE)
        msg = JIM.unpacking(msg)
        if msg.code == ACCEPTED:
            for _ in range(msg.quantity):
                msg = self.sckt.recv(MESSAGE_SIZE)
                msg = JIM.unpacking(msg)
                self.db.add_contact(msg.user_id, msg.user_name, msg.user_nickname)
        else:
            self.show(msg)

    # def get_cont_db(self):
    #     self.db.get_contacts()

    def create_chat(self, room):
        msg = JIMCreateChat(self.user_name, room).packing()
        self.sckt.send(msg)

    def join_chat(self, room):
        msg = JIMJoinChat(self.user_name, room).packing()
        self.sckt.send(msg)

    def leave_chat(self, room):
        msg = JIMLeaveChat(self.user_name, room).packing()
        self.sckt.send(msg)

    def send_message(self, receiver, message):
        msg = JIMMessage(self.user_name, receiver, message).packing()
        self.sckt.send(msg)

    def processing(self):
        # self.get_contacts()
        # resp = self.queue.get()
        # if resp == 'OK':
        #     self.get_contacts()
        while True:
            # print('до залипания')

            # НЕ ЗАБЫТЬ ПРО ТАЙМАУТ!!!

            response = self.queue.get()

            # self.queue.task_done()
            # print('после разлипания')
            if isinstance(response, JIMResponse):
                if response.code == OK or response.code == SENDED:
                    print('resp was OK')
                    msg = input()
                    if msg:
                        msg = msg.split()
                        command = msg[0]
                        msg = msg[1:]
                        print(str(command))
                        print(len(str(command)))
                        print(str(msg))
                        print(len(str(msg)))
                        if len(str(command)) > 15:
                            print('Такого пользователя не существует')
                            self.queue.put(JIMResponse(OK))
                            continue
                        # print(msg)
                        # print(str(msg))
                        # print(len(str(msg)))
                        if len(str(msg)) > MESSAGE_SIZE - 101:
                            print('Слишком длинное сообщение')
                            self.queue.put(JIMResponse(OK))
                            continue
                        message = ''
                        for i in msg:
                            message = message + i + ' '
                        message = message[:-1]
                        # print(len(message))
                        if command == 'add':
                            self.add_contact(message)
                        elif command == 'del':
                            print('удаляем')
                            self.queue.put(JIMResponse(OK))
                        elif command == 'get':
                            # self.get_contacts()
                            contacts = self.db.get_contacts()
                            for contact in contacts:
                                print(contact.nick)
                            self.queue.put(JIMResponse(OK))
                        elif command == 'create':
                            self.create_chat(message)
                        elif command == 'join':
                            self.join_chat(message)
                        elif command == 'leave':
                            self.leave_chat(message)
                        else:
                            self.send_message(command, message)
                    else:
                        self.queue.put(JIMResponse(OK))

                elif response.code == ADDED:
                    self.db.add_contact(response.quantity, response.message, response.message)
                    # self.get_contacts()
                    self.queue.put(JIMResponse(OK))
                elif response.code == ACCEPTED:
                    for _ in range(response.quantity):
                        contact = self.queue.get()
                        self.db.add_contact(contact.user_id, contact.user_name, contact.user_nickname)
                    self.queue.put(JIMResponse(OK))
                elif response.code == NOT_FOUND:
                    self.queue.put(JIMResponse(OK))
                elif response.code == GONE:
                    self.queue.put(JIMResponse(OK))
                elif response.code == CONFLICT:
                    self.queue.put(JIMResponse(OK))
                elif response.code == CREATED:
                    self.queue.put(JIMResponse(OK))

            # elif isinstance(response, JIMContactList)


    def send_presence(self, user_name):
        msg = JIMPresence(user_name).packing()
        self.sckt.send(msg)

    def go(self):
        self.name()
        self.sckt.connect((self.addr, self.port))
        self.send_presence(self.user_name)
        msg = self.sckt.recv(MESSAGE_SIZE)
        msg = JIM.unpacking(msg)
        self.show(msg)
        # resp = self.queue.get()
        # if resp == 'OK':
        self.db.start()
        #     self.get_contacts()
        self.get_contacts()
        self.queue.put(JIMResponse(OK))
        t1 = Thread(target=self.processing)
        t1.start()
        # t2 = Thread(target=self.receive)
        # t2.start()
        while True:
            msg = self.sckt.recv(MESSAGE_SIZE)
            msg = JIM.unpacking(msg)
            self.show(msg)
            self.queue.put(msg)





    def stop(self):
        self.sckt.close()

    def show(self, some_data):
        if isinstance(some_data, JIMMessage):
            message = some_data.message
            room = some_data.receiver
            sender = some_data.user_name
            if room.startswith('#'):
                print(room + ' ---> ' + sender + ': ' + message)
            else:
                print(sender + ': ' + message)
        elif isinstance(some_data, JIMResponse):
            if some_data.message:
                print(some_data.message)

    def receive(self):
        pass
    #     while True:
    #         msg = self.sckt.recv(1024)
    #         msg = JIM.unpacking(msg)
    #         self.sckt.send(JIMRespect(self.user_name).packing())
    #         if self.sended:
    #             self.queue.put(msg2)
    #         self.sended = True
    #         msg2 = msg
            # if isinstance(msg, JIM):
            #     self.sckt.send(JIMRespect(self.user_name).packing())
            # self.show(msg)
            # msg2 = self.sckt.recv(1024)
            # msg2 = JIM.unpacking(msg2)
            # if not isinstance(msg2, JIMResponse):
            #     break
            # if isinstance(msg, JIMResponse):
            #     if msg.code == OK:
            #         self.sckt.send(JIMRespect(self.user_name).packing())
            #         msg = self.sckt.recv(1024)
            #         msg = JIM.unpacking(msg)
            #         if isinstance(msg, JIMResponse) and msg.code == OK:
            #             self.queue.put('OK')
                    # print('put OK')
                    # self.sckt.sendall(JIMRespect(self.user_name).packing())
                # elif msg.code == ADDED:
                #     self.get_contacts()
                # elif msg.code == NOT_FOUND:
                #     self.sckt.send(JIMRespect(self.user_name).packing())
                #     msg = self.sckt.recv(1024)
                #     msg = JIM.unpacking(msg)
                #     if isinstance(msg, JIMResponse) and msg.code == OK:
                #         self.queue.put('NOT_FOUND')
                    # self.sckt.sendall(JIMRespect(self.user_name).packing())
                # elif msg.code == GONE:
                #     self.sckt.send(JIMRespect(self.user_name).packing())
                #     msg = self.sckt.recv(1024)
                #     msg = JIM.unpacking(msg)
                #     if isinstance(msg, JIMResponse) and msg.code == OK:
                #         self.queue.put('GONE')
                    # self.sckt.sendall(JIMRespect(self.user_name).packing())
                # elif msg.code == CONFLICT:
                #     self.sckt.send(JIMRespect(self.user_name).packing())
                #     msg = self.sckt.recv(1024)
                #     msg = JIM.unpacking(msg)
                #     if isinstance(msg, JIMResponse) and msg.code == OK:
                #         self.queue.put('CONFLICT')
                    # self.sckt.sendall(JIMRespect(self.user_name).packing())
                # elif msg.code == CREATED:
                #     self.sckt.send(JIMRespect(self.user_name).packing())
                #     msg = self.sckt.recv(1024)
                #     msg = JIM.unpacking(msg)
                #     if isinstance(msg, JIMResponse) and msg.code == OK:
                #         self.queue.put('CREATED')
                    # self.sckt.sendall(JIMRespect(self.user_name).packing())
                # elif msg.code == ACCEPTED:
                #     self.sckt.send(JIMRespect(self.user_name).packing())
                #     msg2 = self.sckt.recv(1024)
                #     msg2 = JIM.unpacking(msg2)
                #     if isinstance(msg2, JIMResponse) and msg2.code == OK:
                #         for _ in range(msg.quantity):
                #             print('ACCEPTED')
                #             msg = self.sckt.recv(1024)
                #             msg = JIM.unpacking(msg)
                #             if isinstance(msg, JIMContactList):
                #                 id = msg.user_id
                #                 name = msg.user_name
                #                 nick = msg.user_nickname
                #                 self.db.add_contact(id, name ,nick)
                #                 self.sckt.send(JIMRespect(self.user_name).packing())
                #                 msg = self.sckt.recv(1024)
                #                 msg = JIM.unpacking(msg)
                #                 if isinstance(msg, JIMResponse) and msg.code == OK:
                #                     continue
                #                 else:
                #                     break
                #     self.queue.put('OK')
            # elif isinstance(msg, JIMMessage):
            #     self.sckt.sendall(JIMRespect(self.user_name).packing())

if __name__ == '__main__':
    client = Client('localhost', 7777)
    client.go()
