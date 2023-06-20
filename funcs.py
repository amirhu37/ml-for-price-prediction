from typing import Literal
import MetaTrader5 as mt5
from datetime import datetime
import joblib
import numpy as np
from TradeToolKit import kill_mt5, market_order, moving_average, Symbol_data, relative_strength_index, close_all_by_symbol, close_order, update_sl, update_tp


###         Functions      ###

def macd_ema(symbol, time_frame, short_window, long_window, signal_window=1):
    array_1 = Symbol_data(symbol, time_frame, short_window, 'o', False)
    array_2 = Symbol_data(symbol, time_frame, long_window, 'o', False)

    short_ema = calculate_ema_numpy(array_1, short_window)
    long_ema = calculate_ema_numpy(array_2, long_window)
    macd = short_ema - long_ema

    signal = calculate_ema_numpy(macd, signal_window)
    histogram = macd - signal
    return round(macd, 4)  # , signal.item(), histogram.item()


def macd_simple(logo, Time, ma_1, ma_2):
    fast = moving_average(logo, Time, ma_1, "o")[0]
    slow = moving_average(logo, Time, ma_2, "o")[0]
    return fast - slow


def hl2(symbol, time_frame, len) -> float:
    h = Symbol_data(symbol, time_frame, len, 'h')
    l = Symbol_data(symbol, time_frame, len, 'l')

    return h - l


def slope(data, window: int) -> list:

    x = np.arange(len(data))
    y = np.array(data)
    slope, _ = np.polyfit(x, y, 1)
    return slope


def calculate_ema_numpy(array, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()

    ema = np.dot(array, weights[::-1])
    return ema


def std(symbol, time_frame, window=5):
    series = Symbol_data(symbol, time_frame, window, 'o', True)
    return round(np.std(series), 4)


def mean(symbol, time_frame, window=5, ohlc= 'o'):
    series = Symbol_data(symbol, time_frame, window, ohlc, True)
    return round(np.mean(series), 4)


def percentage_changes(symbol, time_frame,) -> float:
    open = Symbol_data(symbol, time_frame, 1, 'o', True)
    close = Symbol_data(symbol, time_frame, 1, 'o', False)
    change = (close - open) / close
    return round(change[0] * 100, 4)


def body(symbol, time_frame,):
    open = Symbol_data(symbol, time_frame, 1, 'o', True)
    close = Symbol_data(symbol, time_frame, 1, 'o', False)
    change = (close - open)
    return round(change[0], 4)


def pivot_point(symbol, time_frame,):
    high = Symbol_data(symbol, time_frame, 1, 'h')
    low = Symbol_data(symbol, time_frame, 1, 'l')
    close = Symbol_data(symbol, time_frame, 1, 'c')

    pivot_point = (high + low + close) / 3

    return pivot_point


def norm(arr):
    if arr[0, 0] > 0:
        return 1
    elif arr[0, 1] > 0:
        return -1
    else:
        0


def open_pivot(logo, Time):
    Open = Symbol_data(logo, Time, 1, 'o', False)[0]
    Pivot = pivot_point(logo, Time)[0]
    return Open - Pivot


def stochastic(symbol, time_frame, n=14, k=3, d=3):
    array = Symbol_data(symbol, time_frame, n, 'o')

    lowest_low = np.min(array)
    highest_high = np.max(array)
    k_value = ((array - lowest_low) / (highest_high - lowest_low))

    d_values = np.mean(k_value[-k:])
    return k_value, d_values


def STD(series, window):
    # series_values = series.values
    rolling_std = np.std(series, axis=0, ddof=0)
    return rolling_std


# -----------  Other --------------
def close_by_time(sym: str, yes: bool):
    if yes:
        for pos in mt5.positions_get(symbol=sym):
            close_all_by_symbol(sym)


def close_for_next(yes: bool):
    return yes


def updator(logo, Time, **args):
    update = update_sl(logo, Time, False, 3) if mt5.positions_get(
        symbol=logo) else "order already dead"
    print(f"Sl updating: {update}")
    update


def kill_app(kill_time):
    if datetime.now().strftime('%H:%M') == kill_time:
        mt5.shutdown()
        exit()


class trade:
    def __init__(self, symbol : str, time_frame : str, volume : float,
                fast_ma : int, slow_ma: int, model_addres : str, isNueran : bool, 
                scale_addrs : str, mean_addrs : str, std_adrs : str, OHLC : Literal['o', 'h', 'l', 'c'],
                order_dict : dict ) -> None:
        self.symbol = symbol
        self.time_frame = time_frame
        self.volume = volume
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.model_addres = model_addres
        self.scale_addrs = scale_addrs
        self.mean_addrs = mean_addrs
        self.std_adrs = std_adrs
        self.OHLC = OHLC
        self.order_type = order_dict
        self.isNueran = isNueran

    def call_data(self, len, on) :
        date  : str  = datetime.now().strftime("%H:%M")
        Open  : float = Symbol_data(self.symbol, self.time_frame, len, on, False)
        Pivot : float = round(pivot_point(self.symbol, self.time_frame)[0], 2)
        ma_1  : float = round(moving_average(self.symbol, self.time_frame,self.fast_ma, self.OHLC)[0], 2)
        ma_2  : float = round(moving_average(self.symbol, self.time_frame,self.slow_ma, self.OHLC)[0], 2)
        
        return date, [Open, Pivot, ma_1, ma_2]

    def standarding(self, array):
        # Load the mean and std from saved files
        
        scaler = joblib.load(self.scale_addrs)
        mean = np.load(self.mean_addrs)
        std = np.load(self.std_adrs)
        scaler.mean_ = mean
        scaler.scale_ = std
        array_scaled = scaler.transform([array])

        return  array_scaled
    # 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
    def predictor(self,d ):
        
        model = joblib.load(self.model_addres)
        if self.isNueran:
            pr = np.argmax(model.predict(d)[0])
        else : 
            pr = model.predict(d)[0]
        print(pr)
        result = self.order_type[pr] 
        return  result
    

    def send_order(self,
        position : Literal['buy', "sell"],
        sl_type : str = "step" ,
        tp_type : str = "step",
        sl_rate : int = 1,
        tp_rate : int = 1,
        Comment: str = ""):
        
        request, result  = market_order(
            symbol=self.symbol,
            time_frame=self.time_frame,
            volume=self.volume,
            order_type=position,
            sl=sl_type,
            tp=tp_type,
            tp_rate= tp_rate,
            sl_rate= sl_rate,
            comment=Comment )#f"""{datetime.now().strftime("%H:%M")}""")

        return  request, result

    def regression(self, d , rate: int ):
        model = joblib.load(self.model_addres)
        pr = model.predict(d)
        pr=pr[:,0]
        d = d[0]
        
        # print(d)
        # print(pr)
        diff =   pr - d 
        diff = diff[0]

        if pr[-1] > d[-1] and diff >= rate:
            return 'buy' , diff
        elif pr[-1] < d[-1] and diff <= -rate:
            return 'sell' , diff
        else:
            return 'hold', diff

        
    def journal(self, j : dict ):

        print(f"""
              {j['time']} --> {j['symbol']}, {j['volume']}
              -------------------------------------------
              Open : { j['Open'] }
              Pivot : { j["pivot"] }
              ma 1 : { j["ma 1"] }
              ma 2 : { j["ma 2"] }
              ------------------------------
              order Type : {j['order']}
              price : {j['price']}
              StopLoss: {j['stoploss']}
              TakeProfit: {j['takeprofit']}
              result:  {j['comment']}
              """)



        return j


