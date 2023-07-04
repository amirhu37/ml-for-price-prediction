from typing import Literal
import MetaTrader5 as mt5
from datetime import datetime
import joblib
import numpy as np
import TradeToolKit as kit


###         Functions      ###


def moving_avg(sym, time_frame, ma_len, ohlc: Literal['o', 'h', 'l', 'c'], ma_type: Literal['sma', 'ema']) -> float:
    data = kit.Symbol_data(sym, time_frame, ma_len, ohlc)
    if ma_type == 'sma':
        return kit.MovingAverages(data).sma
    elif ma_type == 'ema':
        return kit.MovingAverages(data).ema
    else:
        return "Invalid"


def hl2(symbol, time_frame, len) -> float:
    h = kit.kit.Symbol_data(symbol, time_frame, len, 'h')
    l = kit.kit.Symbol_data(symbol, time_frame, len, 'l')

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
    series = kit.Symbol_data(symbol, time_frame, window, 'o', True)
    return round(np.std(series), 4)


def mean(symbol, time_frame, window=5, ohlc='o'):
    series = kit.Symbol_data(symbol, time_frame, window, ohlc, True)
    return round(np.mean(series), 4)


def percentage_changes(symbol, time_frame,) -> float:
    open = kit.Symbol_data(symbol, time_frame, 1, 'o', True)
    close = kit.Symbol_data(symbol, time_frame, 1, 'o', False)
    change = (close - open) / close
    return round(change[0] * 100, 4)


def body(symbol, time_frame,):
    open = kit.Symbol_data(symbol, time_frame, 1, 'o', True)
    close = kit.Symbol_data(symbol, time_frame, 1, 'o', False)
    change = (close - open)
    return round(change[0], 4)


def pivot_point(symbol, time_frame,):
    high = kit.Symbol_data(symbol, time_frame, 1, 'h')
    low = kit.Symbol_data(symbol, time_frame, 1, 'l')
    close = kit.Symbol_data(symbol, time_frame, 1, 'c')

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
    Open = kit.Symbol_data(logo, Time, 1, 'o', False)[0]
    Pivot = pivot_point(logo, Time)[0]
    return Open - Pivot


def stochastic(symbol, time_frame, n=14, k=3, d=3):
    array = kit.Symbol_data(symbol, time_frame, n, 'o')

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
            kit.close_all_by_symbol(sym)


def close_for_next(yes: bool):
    return yes


def updator(logo, Time, **args):
    update = kit.update_sl(logo, Time, False, 3) if mt5.positions_get(
        symbol=logo) else "order already dead"
    print(f"Sl updating: {update}")
    update


def kill_app(kill_time):
    if datetime.now().strftime('%H:%M') == kill_time:
        mt5.shutdown()
        exit()


class trade:
    def __init__(self, symbol: str, time_frame: str, volume: float, ) -> None:
        self.symbol = symbol
        self.time_frame = time_frame
        self.volume = volume

    def standarding(self,
                    scale_addrs,
                    mean_addrs,
                    std_adrs,
                    array):
        # Load the mean and std from saved files

        scaler = joblib.load(scale_addrs)
        mean = np.load(mean_addrs)
        std = np.load(std_adrs)
        scaler.mean_ = mean
        scaler.scale_ = std
        array_scaled = scaler.transform([array])

        return array_scaled

    def predictor(self,
                  model_addres,
                  isNueran,
                  order_dict,
                  data):

        model = joblib.load(model_addres)
        if isNueran:
            pr = np.argmax(model.predict(data)[0])
        else:
            pr = model.predict(data)[0]
        # print(pr)
        result = order_dict[pr]
        return result

    def send_order(self,
                   position: Literal['buy', "sell"],
                   sl_type: str = "step",
                   tp_type: str = "step",
                   sl_rate: int = 1,
                   tp_rate: int = 1,
                   Comment: str = ""):

        request, result = kit.market_order(
            symbol=self.symbol,
            time_frame=self.time_frame,
            volume=self.volume,
            order_type=position,
            sl=sl_type,
            tp=tp_type,
            tp_rate=tp_rate,
            sl_rate=sl_rate,
            comment=Comment)  # f"""{datetime.now().strftime("%H:%M")}""")

        return request, result

    def regression(self, d, rate: int,
                   model_addres: str):
        model = joblib.load(model_addres)
        pr = model.predict(d)
        pr = pr[:, 0]
        d = d[0]

        # print(d)
        # print(pr)
        diff = pr - d
        diff = diff[0]

        if pr[-1] > d and diff >= rate:
            return 'buy', diff
        elif pr[-1] < d and diff <= -rate:
            return 'sell', diff
        else:
            return 'hold', diff

    def journal(self, j: dict):

        print(f"""
              {j['time']} --> {j['symbol']}, {j['volume']}
              ------------------------------
              order Type : {j['order']}
              price : {j['price']}
              StopLoss: {j['stoploss']}
              TakeProfit: {j['takeprofit']}
              result:  {j['comment']}
              """)

        return j

# while True:
#     mt5.account_info()._asdict()