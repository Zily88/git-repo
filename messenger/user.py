from threading import Thread
from queue import Queue
from jim_protocol import JIM

class User():
    def __init__(self, name, sckt, good_func):#, serv_thread):
        self.name = name
        self.sckt = sckt
        self.thread = Thread(target=self.send)
        self.messagequeue = Queue()
        self.respectqueue = Queue()
        self.good_func = good_func
        # self.good_func = good_func
        # self.serv_thread = serv_thread

    def add_msg(self, msg):
        self.messagequeue.put(msg)

    def stop(self):
        self.messagequeue.put('STOP')

    # def del_msg(self, msg):
    #     self.msg.remove(msg)

    # def clear_msg(self):
    #     self.msg = []

    def send(self):
        while True:
            response = self.messagequeue.get()
            if isinstance(response, JIM):
                try:
                    self.sckt.send(response.packing())
                except ConnectionResetError:
                    self.good_func(self)
                    break
            elif response == 'STOP':
                break
            # else:
            #     break
            # self.msg = []
            # self.serv_thread.join()


    def is_empty(self):
        if self.messagequeue.empty():
            return True