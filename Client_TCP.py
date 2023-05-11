from netifaces import interfaces, ifaddresses, AF_INET
from tkinter import messagebox
from UI_Dooz import *
import threading
import socket
import pickle
import time


class Wait_For_Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            self.payam = time.ctime()
            self.massage = s.recv(4096)
            try:
                self.payam = pickle.loads(self.massage)
            except EOFError:
                self.raise_exception()
                New_Sock.close()
                break

            if(self.payam.split()[0] == 'BeReady'):
                p, self.P2_IP, self.P2_Port, self.name, self.dest_IP, self.dest_port = self.payam.split()
                messagebox.askquestion("Check", "do you want to Play with " + self.name, icon ='info')
                if 'yes':
                        self.New_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.New_Sock.connect((self.dest_IP, int(self.dest_port)))
                        self.New_Sock.send(pickle.dumps(num))
                        Game = Competition(num, self.name, self.New_Sock, self.name)
                        Game.start()
                else:
                        s.send(pickle.dumps('no'))

            if(self.payam.split()[0] == 'new'):
                massage = s.recv(4096)
                ActiveNodes = pickle.loads(massage)
                addr = (self.payam.split()[1], int(self.payam.split()[2]), self.payam.split()[3])
                items = ShowActiveNodes(ActiveNodes, addr, s)
                items.start()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
                             
class Competition(threading.Thread):
    def __init__(self, P1, P2, Sock, Turn):
        threading.Thread.__init__(self)
        self.Player_One = P1
        self.Player_Two = P2
        self.Sock = Sock
        self.Turn = Turn
		
    def run(self):

        TTT = Socket_TTT(self.Player_One, self.Player_Two, self.Sock, self.Turn)
        TTT.start()

        while True:
            self.data = time.ctime()
            massage = self.Sock.recv(4096)

            try:
                data = pickle.loads(massage)
            except EOFError:
                self.Sock.close()
                self.raise_exception()
                break

            if(data == 'finish'):
                TTT.finish()
                self.Sock.close()
                self.raise_exception()
                break

            TTT.set_with_code(int(data))

        self.Sock.close()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
    
num = input()

with socket.socket() as c:
    c.bind(('',0))
    port_ = c.getsockname()[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		

port = 1234
ip = '172.20.41.7'

s.connect((ip, port))
thread = Wait_For_Server()
thread.start()
hostname=socket.gethostname()

for ifaceName in interfaces():
    addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
    if ifaceName == 'wlp0s20f3':
        IPAddr = addresses[0]
        break
    elif ifaceName == 'ens33':
        IPAddr = addresses[0]

print("Your Computer Name is:"+hostname)
print("Your Computer IP Address is:"+IPAddr)

payam = num + ' ' + IPAddr + ' ' + str(port_)
s.send(pickle.dumps(payam))
page = FirstPage(s, thread, num)
page.start()

New_Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
print ("Socket successfully created")


New_Sock.bind((IPAddr, port_))

print ("From Player: socket binded to %s" %(port_))

New_Sock.listen(5)
print ("socket is listening")

while True:
    try:
        c, addr = New_Sock.accept()
    except KeyboardInterrupt:
        break
    massage = c.recv(4096)
    name = pickle.loads(massage)
    print ('Got connection from >> ',  port_)
    Game = Competition(num, name, c, num)
    Game.start()

New_Sock.close()