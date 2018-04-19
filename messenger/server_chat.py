from threading import Thread
from select import select
from jim_protocol import JIM, JIMResponse, JIMMessage, OK, CREATED
from user import User

class Chat():
    def __init__(self, name=None):
        self.users = []
        if name:
            self.name = name
        else:
            self.name = str(self)
        self.message = None

    def add_user(self, user):
        self.users.append(user)

    def del_user(self, user):
        self.users.remove(user)

    def user_exists(self, user):
        if user in self.users:
            return True

    def only_one(self):
        if len(self.users) == 1:
            return True

    def get_users_list(self):
        user_list = []
        for user in self.users:
            user_list.append(user.name)
        return user_list

    def is_empty(self):
        if not self.users:
            return True

    def add_message(self, message):
        self.message = message

    def done(self, sender):
        for user in self.users:
            if user == sender:
                continue
            user.add_msg(self.message)
        self.message = None

