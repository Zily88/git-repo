from socket import socket, AF_INET, SOCK_STREAM
from jim_protocol import JIM, JIMPresence, JIMMessage, JIMResponse, OK, JIMAddContact, JIMDelContact, WRONG_REQUEST, FORBIDDEN, GONE, NOT_FOUND, CONFLICT, JIMCreateChat, JIMLeaveChat, JIMJoinChat, CREATED, JIMGetContacts, ACCEPTED, JIMContactList, JIMRespect, ADDED, MESSAGE_SIZE, SENDED, NOT_ADDED, NOT_SENDED, DELETED, JIMInviteChat, INVITED, JIMGetUsers, ACCEPT
from threading import Thread
from queue import Queue
from client_db import ClientDB
from GUI import MainWindow, NotMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import time




class Client:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.sckt = socket(AF_INET, SOCK_STREAM)
        self.queue = Queue()
        self.added_queue = Queue()
        self.sended_queue = Queue()
        self.deleted_queue = Queue()
        self.created_queue = Queue()
        self.sended = False
        self.main_window = MainWindow()
        self.receive = Receive(self)
        self.processing = Processing(self)
        self.receive.mysignal_recv.connect(self.show, QtCore.Qt.QueuedConnection)
        self.processing.mysignal_invite.connect(self.send_agreement, QtCore.Qt.QueuedConnection)
        self.contact_model = QtGui.QStandardItemModel()
        self.message_model = QtGui.QStandardItemModel()
        # self.processing.mysignal_contact.connect(self.model_add, QtCore.Qt.QueuedConnection)
        self.processing.mysignal_message.connect(self.message, QtCore.Qt.QueuedConnection)
        self.main_window.ui.pushButton_2.clicked.connect(self.add_contact)
        self.main_window.ui.pushButton.clicked.connect(self.send_message)
        self.contact = None
        # self.processing.mysignal_history.connect(self.add_history, QtCore.Qt.QueuedConnection)
        # self.message_list = []
        # self.message_model.setStringList(self.message_list)
        # self.send_mute = QtCore.QMutex
        self.chat_model = QtGui.QStandardItemModel()
        self.main_window.ui.listView_2.clicked.connect(self.select_contact)
        self.main_window.ui.listView_2.customContextMenuRequested.connect(self.context_menu)
        self.delete_action = QtWidgets.QAction(self.main_window.tr('Удалить'), self.main_window)
        self.delete_action.triggered.connect(self.del_action)
        self.create_chat_action = QtWidgets.QAction(self.main_window.tr('Создать групповую беседу'), self.main_window)
        self.create_chat_action.triggered.connect(self.create_chat)
        self.main_window.ui.listView_3.setModel(self.chat_model)
        self.main_window.ui.listView_3.setWordWrap(True)
        self.main_window.ui.listView_3.customContextMenuRequested.connect(self.second_context_menu)
        self.invite_action = QtWidgets.QAction(self.main_window.tr('Пригласить в чат'), self.main_window)
        self.invite_action.triggered.connect(self.invite_chat)
        self.leave_action = QtWidgets.QAction(self.main_window.tr('Покинуть чат'), self.main_window)
        self.leave_action.triggered.connect(self.leave_chat)
        self.listik = NotMainWindow()
        self.listik.ui.listView_2.setModel(self.contact_model)
        # self.listik.setWindowModality(QtCore.Qt.ApplicationModal)
        self.contact_for_invite = None
        self.listik.ui.pushButton.clicked.connect(self.button_invite)
        self.listik.hide()
        self.chat_name = None
        self.processing.mysignal_users.connect(self.add_chat)
        self.main_window.ui.listView_3.clicked.connect(self.select_chat)


    def button_invite(self):
        self.listik.hide()
        contact = self.listik.ui.listView_2.selectedIndexes()[0]
        self.contact_for_invite = self.contact_model.data(contact)
        self.sckt.send(JIMInviteChat(self.user_name, self.contact_for_invite,
                                     self.chat_name).packing())



    def context_menu(self, pos):
        menu = QtWidgets.QMenu(self.main_window)
        menu.addAction(self.delete_action)
        menu.addAction(self.create_chat_action)
        menu.exec_(self.main_window.ui.listView_2.mapToGlobal(pos))

    def second_context_menu(self, pos):
        menu = QtWidgets.QMenu(self.main_window)
        menu.addAction(self.invite_action)
        menu.addAction(self.leave_action)
        menu.exec_(self.main_window.ui.listView_3.mapToGlobal(pos))

    def leave_chat(self):
        pass

    def invite_chat(self):
        chat = self.main_window.ui.listView_3.selectedIndexes()[0]
        row = chat.row()
        self.chat_name = self.chat_model.data(chat, role=33)
        self.listik.show()

    def del_action(self):
        contact = self.main_window.ui.listView_2.selectedIndexes()[0]
        row = contact.row()
        self.contact = self.contact_model.data(contact)
        print(self.contact)
        msg = JIMDelContact(self.user_name, self.contact)
        self.sckt.send(msg.packing())
        resp = self.deleted_queue.get()
        if resp == "DELETED":
            self.db.del_messages(self.contact)
            self.db.del_contact(msg.contact)
            self.contact_model.removeRow(row)

        else:
            print('Как это!?!')

    def name(self):
        name, ok = QtWidgets.QInputDialog.getText(self.main_window,
                                                  'СКУПЕ', 'Введите имя')
        if ok:
            self.user_name = name
            self.db = ClientDB(self.user_name)

    def send_agreement(self, contact, room):
        print('invited!!!')
        dialog = QtWidgets.QMessageBox.question(self.main_window, 'СКУРЕ',
                                                '{} хочет добавить вас в групповую беседу'.format(contact),
                                                )
        # print(dialog)
        # print(type(dialog))
        if dialog == 16384:
            print('Yes')
            msg = JIMResponse(INVITED, room)
            self.sckt.send(msg.packing())
            icon = 'chat.png'
            chat_item = QtGui.QStandardItem(QtGui.QIcon(icon), '*')
            chat_item.setData(room, role=33)
            self.chat_model.appendRow(chat_item)
            self.db.add_contact(0, room, room)
            self.sckt.send(JIMGetUsers(self.user_name, room).packing())
        elif dialog == 65536:
            print('No')

    def add_contact(self):
        contact = self.main_window.ui.lineEdit_2.text()
        msg = JIMAddContact(self.user_name, contact).packing()
        self.sckt.send(msg)
        print('before resp')
        resp = self.added_queue.get()
        print('after resp')
        if resp == 'ADDED':
            id = self.added_queue.get()
            self.db.add_contact(id, contact, contact)
            self.model_add(contact)
        elif resp == 'NOPE!':
            pass

    def vk(self, contact):
        self.contact = contact

    def select_chat(self, contact):
        self.message_model.clear()
        print(contact)
        name = self.chat_model.data(contact, role=33)
        print(name)
        self.contact = name
        self.get_good_messages()
        self.main_window.ui.listView.setModel(self.message_model)

    def select_contact(self, contact):
        self.message_model.clear()
        print(contact)
        print('123')
        name = self.contact_model.data(contact)
        self.contact = name
        print(self.contact)
        # id = self.db.select_user_id('timmy')
        # print(id)
        # id = self.db.select_user_id(self.receiver)
        self.get_good_messages()
        self.main_window.ui.listView.setModel(self.message_model)
        # lst = []
        # lst.extend(messages)
        # print(lst)
        # self.message_model.setStringList(lst)


        # pass

    def combo_vombo(self, contact):
        pass
        # if self.Right:
        #     print('Right click')
        # else:
        #     print('Left click')

    def message(self, sender,  receiver, message, time, receiv):
        if receiver.startswith('<server_chat.Chat object at'):
            new_message = sender + ': ' + message
            self.db.add_mesage(receiver, new_message, time, receiv)
        else:
            self.db.add_mesage(sender, message, time, receiv)
        # pass

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

    def create_chat(self):
        contact = self.main_window.ui.listView_2.selectedIndexes()[0]
        row = contact.row()
        self.contact = self.contact_model.data(contact)
        msg = JIMCreateChat(self.user_name)
        self.sckt.send(msg.packing())
        resp = self.created_queue.get()
        if resp == 'CREATED':
            chat_name = self.created_queue.get()
            print('create_chat: chat_name: {}'.format(chat_name))
            icon = 'chat.png'
            chat_item = QtGui.QStandardItem(QtGui.QIcon(icon), '*')
            chat_item.setData(chat_name, role=33)
            self.db.add_contact(0, chat_name, chat_name)
            self.chat_model.appendRow(chat_item)
            self.sckt.send(JIMInviteChat(self.user_name, self.contact, chat_name).packing())

    def add_chat(self, room, user):
        print('add_chat user: ' + str(user))
        print('add_chat room: ' + room)
        if isinstance(user, int):
            new_user = self.db.select_user_name(user)
        else:
            new_user = user
        print(new_user)
        chats = self.get_all_items(self.chat_model)
        my_chat = None
        for chat in chats:
            if chat.data(33) == room:
                my_chat = chat
                break
        # item = QtGui.QStandardItem(user)
        # my_chat.appendRow(item)
        users = my_chat.text()
        print('users of my_chat: ' + users)
        print('new_user for my_chat' + new_user)
        if users == '*':
            my_chat.setText(new_user)
        else:
            new_users = users + '\n' + new_user
            my_chat.setText(new_users)
        # for ch in self.chat_model:
        #     print(ch)
        # item = QtGui.QStandardItem(user)
        # chat.appendRow(item)

    def join_chat(self, room):
        msg = JIMJoinChat(self.user_name, room).packing()
        self.sckt.send(msg)

    def get_all_items(self, model):
        count = 0
        lst = []
        while True:
            print(model.item(count))
            if model.item(count):
                lst.append(model.item(count))
                count += 1
            else:
                break
        return lst

    # def leave_chat(self, room):
    #     msg = JIMLeaveChat(self.user_name, room).packing()
    #     self.sckt.send(msg)

    def send_message(self):
        message = self.main_window.ui.lineEdit.text()
        msg = JIMMessage(self.user_name, self.contact, message)
        self.sckt.send(msg.packing())
        resp = self.sended_queue.get()
        if resp == 'SENDED':
            self.add_message(msg.receiver, msg.message, msg.time, False)
            # print('SENDED')
            # self.db.add_mesage(msg.receiver, msg.message, msg.time, False)
            # print('db.add_message()')
            # good_time = time.localtime(msg.time)
            # print('good_time()')
            # result_time = time.strftime('%d%b%H%M%S', good_time)
            # print('result_time')
            # lst = self.message_model.stringList()
            # print('model list')
            # lst.append(result_time)
            # print('append time')
            # lst.append(msg.message)
            # print('apend msg')
        elif resp == 'NOPE!':
            pass


    def add_message(self, receiver, message, msgtime, not_sender):
        print('SENDED')
        self.db.add_mesage(receiver, message, msgtime, not_sender)
        print('db.add_message()')
        good_time = time.localtime(msgtime)
        print('good_time()')
        result_time = time.strftime('%d %b %H:%M:%S', good_time)
        # result_time = '{} {} {} {} {}'.format(good_time[2], good_time[1], good_time[3], good_time[4], good_time[5])
        item = QtGui.QStandardItem()
        item.setText(result_time)
        item.setSelectable(False)
        item.setEditable(False)
        if not_sender:
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            item.setBackground(QtGui.QColor('#E4FDF2'))
        else:
            item.setTextAlignment(QtCore.Qt.AlignRight)
            item.setBackground(QtGui.QColor('#C5F3FF'))
        self.message_model.appendRow(item)
        item = QtGui.QStandardItem()
        item.setText(message)
        item.setSelectable(False)
        item.setEditable(False)
        if not_sender:
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            item.setBackground(QtGui.QColor('#E4FDF2'))
        else:
            item.setTextAlignment(QtCore.Qt.AlignRight)
            item.setBackground(QtGui.QColor('#C5F3FF'))
        self.message_model.appendRow(item)
        # print('result_time')
        # lst = self.message_model.stringList()
        # print('model list')
        # lst.append(result_time)
        # print('append time')
        # lst.append(message)
        # print('apend msg')
        # self.message_model.setStringList(lst)


    # def processing(self):
    #     pass
        # self.get_contacts()
        # resp = self.queue.get()
        # if resp == 'OK':
        #     self.get_contacts()


            # elif isinstance(response, JIMContactList)


    def send_presence(self, user_name):
        msg = JIMPresence(user_name).packing()
        self.sckt.send(msg)

    def dialog_ok(self):
        self.user_name = self.dialog.ui.lineEdit.text()

    def model_add(self, contact):
        print('Model_add')
        # self.db.add_contact(id, contact, contact)
        icon = 'Icon.png'
        item = QtGui.QStandardItem(QtGui.QIcon(icon), contact)
        self.contact_model.appendRow(item)
        self.contact_model.sort(QtCore.Qt.AscendingOrder)

        # index = self.model.indexFromItem(item)
        # print(index)


    def gui_contacts(self):
        lst = self.db.get_contacts()
        for contact in lst:
            icon = 'Icon.png'
            item = QtGui.QStandardItem(QtGui.QIcon(icon), contact.name)
            self.contact_model.appendRow(item)
        self.main_window.ui.listView_2.setModel(self.contact_model)
        self.contact_model.sort(QtCore.Qt.AscendingOrder)

    def get_good_messages(self):
        messages = self.db.get_messages(self.contact)
        messages.sort(key=self.sort_by_time)
        # all_messages = []
        # all_messages.extend(messages)
        # all_messages.extend(my_messages)
        # all_messages.sort(key=self.sort_by_time)
        result = []
        # print(all_messages)
        for message in messages:
            print(message)
            good_time = time.localtime(message.time)
            result_time = time.strftime('%d %b %H:%M:%S', good_time)
            # result_time = '{} {} {} {} {}'.format(good_time[2], good_time[1], good_time[3], good_time[4], good_time[5])
            # result.append(result_time)
            # result.append(message.message)
            item = QtGui.QStandardItem()
            item.setText(result_time)
            item.setSelectable(False)
            item.setEditable(False)
            if not message.receiver:
                item.setTextAlignment(QtCore.Qt.AlignRight)
                item.setBackground(QtGui.QColor('#C5F3FF'))
                self.message_model.appendRow(item)
                item = QtGui.QStandardItem()
                item.setText(message.message)
                item.setTextAlignment(QtCore.Qt.AlignRight)
                item.setSelectable(False)
                item.setEditable(False)
                item.setBackground(QtGui.QColor('#C5F3FF'))
                self.message_model.appendRow(item)
            else:
            # print(message)
            # good_time = time.localtime(message.time)
            # result_time = time.strftime('%d %b %H:%M:%S', good_time)
            # result_time = '{} {} {} {} {}'.format(good_time[2], good_time[1], good_time[3], good_time[4], good_time[5])
            # result.append(result_time)
            # result.append(message.message)
                item = QtGui.QStandardItem()
                item.setText(result_time)
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                item.setSelectable(False)
                item.setEditable(False)
                item.setBackground(QtGui.QColor('#E4FDF2'))
                self.message_model.appendRow(item)
                item = QtGui.QStandardItem()
                item.setText(message.message)
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                item.setSelectable(False)
                item.setEditable(False)
                item.setBackground(QtGui.QColor('#E4FDF2'))
                self.message_model.appendRow(item)
        # return result
        # pass

    def sort_by_time(self, message):
        return message.time


    def go(self):
        self.name()
        self.main_window.setWindowTitle(self.user_name)
        self.main_window.show()
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
        # self.queue.put(JIMResponse(OK))
        self.gui_contacts()
        self.receive.start()
        self.processing.start()
        # t1 = Thread(target=self.processing)
        # t1.start()
        # t2 = Thread(target=self.receive)
        # t2.start()








    def stop(self):
        self.sckt.close()

    def show(self, some_data):
        if isinstance(some_data, JIMResponse):
            if some_data.message and some_data.code != CREATED and some_data.code != INVITED\
                    and some_data.code != ACCEPT:
                # print(some_data.message)
                QtWidgets.QMessageBox.information(self.main_window,
                                                  'СКУРЕ', '{}'.format(some_data.message))
            elif some_data.code == INVITED:
                print(some_data)
                room = some_data.message
                print(some_data.quantity)
                name = self.db.select_user_name(some_data.quantity)
                print('Name = ' + name)
                QtWidgets.QMessageBox.information(self.main_window, 'СКУРЕ',
                                                  '{} присоединился к чату'.format(name))
                self.add_chat(room, name)

class Receive(QtCore.QThread):
    mysignal_recv = QtCore.pyqtSignal(JIM)
    def __init__(self, client, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.client = client
    def run(self):
        while True:
            msg = self.client.sckt.recv(MESSAGE_SIZE)
            msg = JIM.unpacking(msg)
            self.mysignal_recv.emit(msg)
            # self.client.show(msg)
            self.client.queue.put(msg)

class Processing(QtCore.QThread):
    mysignal_invite = QtCore.pyqtSignal(str, str)
    mysignal_message = QtCore.pyqtSignal(str, str,str, int, bool)
    mysignal_users = QtCore.pyqtSignal(str, int)
    def __init__(self, client, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.client = client
    def run(self):
        while True:
            # print('до залипания')

            # НЕ ЗАБЫТЬ ПРО ТАЙМАУТ!!!
            print('before queue')

            response = self.client.queue.get()

            # self.queue.task_done()
            # print('после разлипания')
            if isinstance(response, JIMResponse):
                if response.code == OK:
                    print('resp was OK')
                    # msg = input()
                    # if msg:
                    #     msg = msg.split()
                    #     command = msg[0]
                    #     msg = msg[1:]
                    #     print(str(command))
                    #     print(len(str(command)))
                    #     print(str(msg))
                    #     print(len(str(msg)))
                    #     if len(str(command)) > 15:
                    #         print('Такого пользователя не существует')
                    #         self.client.queue.put(JIMResponse(OK))
                    #         continue
                    #     # print(msg)
                    #     # print(str(msg))
                    #     # print(len(str(msg)))
                    #     if len(str(msg)) > MESSAGE_SIZE - 101:
                    #         print('Слишком длинное сообщение')
                    #         self.client.queue.put(JIMResponse(OK))
                    #         continue
                    #     message = ''
                    #     for i in msg:
                    #         message = message + i + ' '
                    #     message = message[:-1]
                    #     # print(len(message))
                    #     if command == 'add':
                    #         self.client.add_contact(message)
                    #     elif command == 'del':
                    #         print('удаляем')
                    #         self.client.queue.put(JIMResponse(OK))
                    #     elif command == 'get':
                    #         # self.get_contacts()
                    #         contacts = self.client.db.get_contacts()
                    #         for contact in contacts:
                    #             print(contact.nick)
                    #         self.client.queue.put(JIMResponse(OK))
                    #     elif command == 'create':
                    #         self.client.create_chat(message)
                    #     elif command == 'join':
                    #         self.client.join_chat(message)
                    #     elif command == 'leave':
                    #         self.client.leave_chat(message)
                    #     else:
                    #         self.client.send_message(command, message)
                    # else:
                    #     self.client.queue.put(JIMResponse(OK))

                elif response.code == ADDED:
                    # self.client.db.add_contact(response.quantity, response.message, response.message)
                    # self.mysignal_contact.emit(response.quantity, response.message)
                    print("ADDED")
                    self.client.added_queue.put('ADDED')
                    self.client.added_queue.put(response.quantity)
                elif response.code == NOT_ADDED:
                    print('NOT_ADDED')
                    self.client.added_queue.put('NOPE!')
                elif response.code == SENDED:
                    # self.client.db.add_contact(response.quantity, response.message, response.message)
                    # self.mysignal_contact.emit(response.quantity, response.message)
                    print("SENDED")
                    self.client.sended_queue.put('SENDED')
                elif response.code == NOT_SENDED:
                    self.client.sended_queue.put('NOPE!')
                elif response.code == ACCEPTED:
                    for _ in range(response.quantity):
                        contact = self.client.queue.get()
                        self.client.db.add_contact(contact.user_id, contact.user_name, contact.user_nickname)
                    self.client.queue.put(JIMResponse(OK))
                elif response.code == DELETED:
                    self.client.deleted_queue.put('DELETED')
                elif response.code == NOT_FOUND:
                    self.client.queue.put(JIMResponse(OK))
                elif response.code == GONE:
                    self.client.queue.put(JIMResponse(OK))
                elif response.code == CONFLICT:
                    self.client.queue.put(JIMResponse(OK))
                elif response.code == CREATED:
                    self.client.created_queue.put('CREATED')
                    self.client.created_queue.put(response.message)
                elif response.code == ACCEPT:
                    for _ in range(response.quantity):
                        print('первый пошёл')
                        msg = self.client.queue.get()
                        print(msg.message, msg.quantity)
                        self.mysignal_users.emit(msg.message, msg.quantity)


            elif isinstance(response, JIMMessage):
                self.mysignal_message.emit(response.user_name, response.receiver,
                                           response.message, response.time, True)

            elif isinstance(response, JIMInviteChat):
                self.mysignal_invite.emit(response.user_name, response.room)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    client = Client('localhost', 7777)
    client.go()
    sys.exit(app.exec_())
