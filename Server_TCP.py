from netifaces import interfaces, ifaddresses, AF_INET
import threading
import socket
import ctypes
import pickle
import time


class Players_Handling(threading.Thread):
    def __init__(self, New_Sock, addr, name, server_ip, server_port):
        threading.Thread.__init__(self)
        self.server_port = server_port
        self.New_Sock = New_Sock
        self.server_ip = server_ip
        self.name = name
        self.addr = addr

    def run(self):
        try:
            while True:    
                self.data = time.ctime()

                self.massage = self.New_Sock.recv(4096)

                try:
                    self.data = pickle.loads(self.massage)
                except EOFError:
                    self.New_Sock.close()
                    self.raise_exception()
                    ActiveNodes.remove(self.addr + (self.name,))
                    del Threads_Handel[self.addr + (self.name,)]
                    break

                if(self.data == "Exit"):
                    self.New_Sock.close()
                    self.raise_exception()
                    ActiveNodes.remove(self.addr + (self.name,))
                    del Threads_Handel[self.addr + (self.name,)]
                    break


                if(self.data == "no"):
                    pass
                
                if(self.data.split()[0] == "select"):
                    Threads_Handel[(self.data.split()[1], int(self.data.split()[2]), self.data.split()[3])].send('BeReady ' + self.addr[0] + ' ' + str(self.addr[1]) + ' ' + self.name + ' ' + self.server_ip + ' ' + str(self.server_port))


                if(self.data == "NewGame"):
                    self.send('new ' + self.addr[0] + ' ' + str(self.addr[1]) + ' ' + self.name)
                    time.sleep(1)
                    self.send(ActiveNodes)
            
            self.New_Sock.close()

        except KeyboardInterrupt:
            self.New_Sock.close()
            self.raise_exception()
            ActiveNodes.remove(self.addr + (self.name,))
            del Threads_Handel[self.addr + (self.name,)]

    def send(self, payam):
        self.New_Sock.send(pickle.dumps(payam))

    def __str__(self) -> str:
        return self.name

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
        

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
print ("Socket successfully created")

port = 1234

ActiveNodes = []
Threads_Handel = dict()

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

s.bind((IPAddr, port))

print ("socket binded to %s" %(port))

s.listen(5)
print ("socket is listening")

while True:
    try:
        c, addr = s.accept()
    except KeyboardInterrupt:
        break
    massage = c.recv(4096)
    data = pickle.loads(massage)
    name, ip, port = data.split()
    ActiveNodes.append(addr + (name,))
    Threads_Handel[addr + (name,)] = Players_Handling(c, addr, name, ip, int(port))
    Threads_Handel[addr + (name,)].start()
    print ('Got connection from >> ',  port)

s.close()