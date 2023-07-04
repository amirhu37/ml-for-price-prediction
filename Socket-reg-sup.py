import os
import socket
import time
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
import TradeToolKit as kit


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



def clac_sup(msg):
    P = ""
    sup = kit.SUPPORT_RESISTANCE(msg[0], msg[1]+ "m" , int(msg[-1])).result()
    # print("SUPs :",sup[0] + sup[1])
    for idx in (sup[0] + sup[1]):
        P += str(idx) + "_"
    # print("P ", P)
    return P

def main():
    msg = serv.recvmsg()
    # print(msg)
    Sup =  clac_sup(msg)
    reg = calc_regr(msg)
    res = reg + "_" + Sup
    # arima = calc_airma(msg)
    serv.sendmsg(res)
    # serv.sendmsg(reg)


def calc_regr(msg ):
    print(msg)
    lengh = int(msg[-1])
    print(lengh)
    data = kit.Symbol_data(msg[0], msg[1]+"m", lengh, 'o')
    X = np.array(range(len(data))).reshape(-1,1)  
    lr = LinearRegression()
    lr.fit(X, data)
    Y_pred = lr.predict(X)
    type(Y_pred)
    P = Y_pred.astype(str).item(0) + '_' + Y_pred.astype(str).item(-1)
    # print(f"reg p: {P}")
    return str(P)



def calc_airma(msg):

    model = ARIMA(msg, order=(5, 1, 0))
    model_fit = model.fit()
    predictions = model_fit.predict(start=len(msg), end=len(msg) + 20)  # Replace '10' with the desired number of forecast steps
    P = predictions.astype(str).item(0) + '_' + predictions.astype(str).item(-1)
    return str(P)


serv = socketserver('localhost', 9090)

while True:  
    try:
        os.system("cls")
        time.sleep(1)
        main() 
    except:
        pass   
