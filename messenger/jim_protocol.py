import time
import json
import sys
import traceback

ENCODING = 'utf-8'

BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400
SERVER_ERROR = 500
FORBIDDEN = 403
GONE = 410
NOT_FOUND = 404
CONFLICT = 409
CREATED = 201
ADDED = 203
SENDED = 204
NOT_ADDED = 405
NOT_SENDED = 406
MESSAGE_SIZE = 1024
DELETED = 205
INVITED = 206
ACCEPT = 207
NOT_CREATED = 411
DELETE_CHAT = 412
DELETED_CHAT = 413

class JIM:
    def __init__(self, action, user_name=None):
        self.action = action
        self.user_name = user_name
        self.time = int(time.time())
        if self.user_name:
            self.msg = {
                'action': self.action,
                'time': self.time,
                'user': self.user_name
            }
        else:
            self.msg = {
                'action': action,
                'time': self.time
            }

    def is_empty(self):
        for string in self.msg.values():
            if not string:
                return True

    def packing(self):
        msg = json.dumps(self.msg)
        msg = msg.encode(ENCODING)
        lenght = len(msg)
        dev = MESSAGE_SIZE - lenght
        msg = msg + dev * chr(7).encode(ENCODING)
        return msg

    def unpacking(some_bytes):
        # try:
        end = 0
        for n, c in enumerate(some_bytes):
            if c == 7:
                end = n
                break
        msg = some_bytes[:end].decode(ENCODING)
        msg = json.loads(msg)
        try:
            action = msg['action']
        except KeyError:
            code = msg['response']
            try:
                message = msg['message']
                quantity = msg['quantity']
                return JIMResponse(code, message, quantity)
            except KeyError:
                try:
                    message = msg['message']
                    return JIMResponse(code, message)
                except KeyError:
                    try:
                        quantity = msg['quantity']
                        return JIMResponse(code, quantity=quantity)
                    except KeyError:
                        return JIMResponse(code)
        else:
            if action == 'presence':
                user_name = msg['user']
                return JIMPresence(user_name)
            elif action == 'get_users':
                user_name = msg['user']
                room = msg['room']
                return JIMGetUsers(user_name, room)
            elif action == 'size':
                user_name = msg['user']
                size = msg['size']
                return JIMSize(user_name, size)
            elif action == 'respect':
                user_name = msg['user']
                return JIMRespect(user_name)
            elif action == 'msg':
                user_name = msg['user']
                receiver = msg['to']
                message = msg['message']
                return JIMMessage(user_name, receiver, message)
            elif action == 'add_contact':
                user_name = msg['user']
                contact = msg['user_id']
                return JIMAddContact(user_name, contact)
            elif action == 'del_contact':
                user_name = msg['user']
                contact = msg['user_id']
                return JIMDelContact(user_name, contact)
            elif action == 'get_contacts':
                user_name = msg['user']
                return JIMGetContacts(user_name)
            elif action == 'contact_list':
                user_name = msg['user']
                user_nickname = msg['user_nickname']
                user_id = msg['user_id']
                return JIMContactList(user_name, user_nickname, user_id)
            elif action == 'create':
                user_name = msg['user']
                try:
                    room_name = msg['room']
                except KeyError:
                    return JIMCreateChat(user_name)
                else:
                    return JIMCreateChat(user_name, room_name)
            elif msg['action'] == 'join':
                user_name = msg['user']
                room_name = msg['room']
                return JIMJoinChat(user_name, room_name)
            elif action == 'leave':
                user_name = msg['user']
                room_name = msg['room']
                return JIMLeaveChat(user_name, room_name)
            elif action == 'invite':
                user = msg['user']
                contact = msg['contact']
                room = msg['room']
                return JIMInviteChat(user, contact, room)
        # except KeyError:



        # except Exception as e:
        #     with open('log.txt', 'a') as log:
        #         traceback.print_exc(file=log)


class JIMPresence(JIM):
    def __init__(self, user_name):
        action = 'presence'
        super().__init__(action, user_name)

class JIMRespect(JIM):
    def __init__(self, user_name):
        action = 'respect'
        super().__init__(action, user_name)

class JIMMessage(JIM):
    def __init__(self, user_name, receiver, msg):
        action = 'msg'
        self.receiver = receiver
        self.message = msg
        super().__init__(action, user_name)
        self.msg['to'] = self.receiver
        self.msg['message'] = self.message


class JIMCreateChat(JIM):
    def __init__(self, user, room_name=None):
        action = 'create'
        self.room = room_name
        super().__init__(action, user)
        if self.room:
            self.msg['room'] = self.room


class JIMJoinChat(JIM):
    def __init__(self, user, room_name):
        action = 'join'
        self.room = room_name
        super().__init__(action, user)
        self.msg['room'] = self.room

class JIMInviteChat(JIM):
    def __init__(self, user, contact, room):
        action = 'invite'
        self.room = room
        self.contact = contact
        super().__init__(action, user)
        self.msg['room'] = self.room
        self.msg['contact'] = self.contact

class JIMLeaveChat(JIM):
    def __init__(self, user, room_name):
        action = 'leave'
        self.room = room_name
        super().__init__(action, user)
        self.msg['room'] = self.room



class JIMAddContact(JIM):
    def __init__(self, user_name, contact):
        action = 'add_contact'
        self.contact = contact
        super().__init__(action, user_name)
        self.msg['user_id'] = contact


class JIMDelContact(JIM):
    def __init__(self, user_name, contact):
        action = 'del_contact'
        self.contact = contact
        super().__init__(action, user_name)
        self.msg['user_id'] = contact

class JIMGetContacts(JIM):
    def __init__(self, user_name):
        action = 'get_contacts'
        super().__init__(action, user_name)

class JIMContactList(JIM):
    def __init__(self, user_name, user_nickname, user_id):
        action = 'contact_list'
        self.user_id = user_id
        self.user_nickname = user_nickname
        super().__init__(action, user_name)
        self.msg['user_nickname'] = user_nickname
        self.msg['user_id'] = user_id

class JIMGetUsers(JIM):
    def __init__(self, user_name, room):
        action = 'get_users'
        self.room = room
        super().__init__(action, user_name)
        self.msg['room'] = self.room

class JIMResponse(JIM):
    def __init__(self, code, msg=None, quantity=None):
        self.code = code
        self.message = msg
        self.quantity = quantity
        if self.message and self.quantity:
            self.msg = {
                'response': self.code,
                'time': int(time.time()),
                'message': self.message,
                'quantity': self.quantity
            }
        elif self.message and not self.quantity:
            self.msg = {
                'response': self.code,
                'time': int(time.time()),
                'message': self.message
            }
        elif self.quantity and not self.message:
            self.msg = {
                'response': self.code,
                'time': int(time.time()),
                'quantity': self.quantity
            }
        else:
            self.msg = {
                'response': self.code,
                'time': int(time.time())
            }

class JIMSize(JIM):
    def __init__(self, username, size):
        action = 'size'
        self.size = size
        self.user_name = username
        super().__init__(action, self.user_name)
        self.msg['size'] = size

