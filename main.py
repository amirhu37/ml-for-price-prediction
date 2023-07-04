# -----------   Document    --------------------------------
"""
homo Homini Lupos

"""
import logging
import os
import traceback
from datetime import datetime
from os.path import exists
from time import sleep
from typing import  Literal


import MetaTrader5 as mt5

import funcs
import TradeToolKit as kit
# -----------   Imports     --------------------------------
from funcs import  trade

print(__doc__)
# --------------INPUTS-----------------------
logo: Literal['XAUUSD', "GBPUSD", "EURUSD"] = input("Enter Symbol: ").upper()
Time: Literal['5m', "15m", "30m", "1h"] = input('Time Frame: ')
Volume: float = 0.01

kill_time: str = "19:30"


Model_addrs = "Models\\prime\\MLPClassifier  96.52%.h5"

Scale_Addrs = "Models\prime\scaler.pkl"

Mean_Addrs = "Models\\prime\\mean.npy"

Std_Addrs = "Models\\prime\\std.npy"


# --------- Market Varibles-------------------
SL_rate: int = 10
TP_rate: int = 5

SL: Literal['step', 'str', 'amount', "candle" ] = "step"
TP: Literal['step', 'str', 'amount', "candle" ] = "step"

# --------------- General Variables --------------------

ma_1_len: int = 5
ma_2_len: int = 10


regiluzer: dict = {
    "1m":  ['00', '01', '02', '03', '04', '05',
            '06', '07', '08', '09', '10', '11',
            '12', '13', '14', '15', '16', '17',
            '18', '19', '20', '21', '22', '23',
            '24', '25', '26', '27', '28', '29',
            '30', '31', '32', '33', '34', '35',
            '36', '37', '38', '39', '40', '41',
            '42', '43', '44', '45', '46', '47',
            '48', '49', '50', '51', '52', '53',
            '54', '55', '56', '57', '58', '59'],

    "5m": ["00", "05", "10", "15", "20", "25",
           "30", "35", "40", "45", "50", "55"],

    "15m": ["00", "15", "30", "45"],

    "30m": ["30", "00"],

    "1h": ["00"],
    "4h": ['00']}


Time_dct: dict = {
    "1m": 2,
    "3m": 5,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
}

columns = ['time', 'Open', 'pivot', 'ma 1', 'ma 2', 'symbol',
           'volume', 'order', 'stoploss', 'takeprofit', 'comment']


# ---------     Make Log File -----------------
os.system("if exist Logs\ (echo None) else (mkdir Logs\)")
if not exists(f"Logs\{datetime.now().strftime('%Y-%m-%d')}.csv"):
    with open(f"Logs\{datetime.now().strftime('%Y-%m-%d')}.csv", 'w') as file:
        file.write(','.join(columns))
        file.write('\n')

LOG_FORMAT = "%(message)s"
logging.basicConfig(format=LOG_FORMAT,
                    level=logging.INFO,
                    filename=f"Logs\{datetime.now().strftime('%Y-%m-%d')}.csv",
                    filemode="a",)
logger = logging.getLogger(__name__)
# --------------- Data Processing ----------------


def updator(Output: dict):
    price_now = kit.Symbol_data(logo, Time, 1, 'c', True)[0]
    open_price = Output["price_open"] = mt5.positions_get(symbol=logo)[
        0]._asdict()['price_open']

    if Output['type'] == "buy":
        if (price_now > open_price):
            updator = kit.update_sl(logo)
    elif Output['type'] == "sell":
        if (price_now < open_price):
            updator = kit.update_sl(logo)
    if updator == "Request executed":
        counter += 1
        if counter >= 3:
            tp_up = kit.update_tp(logo)
            counter = 3
            print(f"tp updated: {tp_up} ")


def main():
    app = trade(symbol=logo,
                time_frame=Time,
                volume=Volume,
   )

    time_stamp  : str  = datetime.now().strftime("%H:%M")

    data = [
        kit.Symbol_data(logo, Time, 1, 'o', False)[0],
        round(funcs.pivot_point(logo, Time)[0], 2),
        round(funcs.moving_avg(logo, Time,ma_1_len, "c", 'sma'), 2),
        round(funcs.moving_avg(logo, Time,ma_2_len, "c", 'sma'), 2),

    ]
    print(data)
    scaling = app.standarding( scale_addrs=Scale_Addrs,
                                mean_addrs=Mean_Addrs,
                                std_adrs=Std_Addrs,
                                array= data)
    
    predict = app.predictor(   model_addres=Model_addrs,          
                            order_dict={
                                        1: "buy",
                                        2: "sell",
                                        0: "hold"},
                            isNueran=False,
                            data=scaling)
    
    print(f"{time_stamp} --> {predict}")
    
    if predict in ["buy", "sell"]:
        print(predict)
        if not mt5.positions_get(symbol=logo):
            request, result = app.send_order(
                position=predict,
                sl_type=SL,
                tp_type=TP,
                sl_rate=SL_rate,
                tp_rate=TP_rate,
                Comment="class")

            total = {
                "time": time_stamp,
                "price": request['price'],
                "Open": data[0],
                "pivot": data[1],
                "ma 1": data[2],
                "ma 2": data[3],

                "symbol": logo,
                "volume": Volume,
                'order':  predict,
                "stoploss": request['sl'],
                "takeprofit": request['tp'],
                "comment": result['comment']}

            journal = app.journal(total)
            logger.info(",".join(str(value) for value in journal.values()))
            return {"price_open": data[0], 'type': predict, "comment": result['comment']}
        else:
            return {"price_open": 0.0, 'type': predict, "comment": "Already exist"}

    else:
        return {"price_open": 0.0, 'type': predict, "comment": "No oreder"}


# print(main  ())
###         EXECUTE      ###
counter = 0
if __name__ == '__main__':
    while True:
        # break
        try:

            if datetime.now().strftime('%M') in regiluzer[Time]:
                try:
                    os.system('cls')
                    out = main()
                    print(out)
                    sleep(Time_dct[Time] * 60)
                    funcs.close_by_time(logo, False)
                    funcs.kill_app(kill_time)
                except Exception as e:
                    print(f"""Exception Error: \n {e}
                                {traceback.print_exc()}""")

                if mt5.positions_get(symbol=logo):
                    try:
                        updator(Output=out)
                    except:
                        sleep(1)

            else:
                os.system('cls')
                print(f"""
                        wait to be regulize
                        {logo} {Volume}  {Time} \n
                        {datetime.now().strftime('%H:%M:%S')}""")
                sleep(1)
                funcs.kill_app(kill_time)
        except Exception as e:
            print(f"""Exception Error: \n {e}
                    {traceback.print_exc()}""")
            sleep(1)
            continue
