from json import dumps, loads
import time
from sys import argv
from socketserver import BaseRequestHandler, TCPServer
import jimprot


class BaseMessageHandler(BaseRequestHandler):

    def handle(self):
        recv = self.request.recv(640)
        recv = loads(recv.decode('ascii'))
        if recv['action'] == 'presence':
            answer = jimprot.JIMAnswer(100).answer
            answer = answer.encode('ascii')
            self.request.send(answer)

serv = TCPServer(('', 7777), BaseMessageHandler)
print('Поехали')
serv.serve_forever()
