import os
import socket
import time
import TradeToolKit as kit
from statsmodels.tsa.arima.model import ARIMA
# from main import main


class socketserver:
    def __init__(self, address='', port=9090):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address
        self.port = port
        self.sock.bind((self.address, self.port))
        self.cummdata = ''
        self.conn = None  # Initialize the connection socket

    def recvmsg(self):
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        print('Connected to', self.addr)
        self.cummdata = ''
        
        while True:
            data = self.conn.recv(10_00)
            self.cummdata += data.decode("utf-8")
            if not data:
                break
        
        needs = self.cummdata.split(',')[:4]
        return needs

    def sendmsg(self, Data):
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        
        out = self.conn.send(bytes(Data, "utf-8"))  # Use utf-8 encoding for sending data
        
        return out  # Return the number of bytes sent

    def __del__(self):
        self.sock.close()



def main ():
    msg = serv.recvmsg()
    print(msg)
    engulf = kit.Patterns(msg[0], msg[1]+ 'm').engulfing(float(msg[-1]))
    serv.sendmsg(engulf)



serv = socketserver('localhost', 9090)

while True:  
    try:
        os.system("cls")
        time.sleep(1)
        main() 
    except:
        pass  