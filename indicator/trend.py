
from pandas import DataFrame
from ta.wrapper import MACD


def macd(data_pd:DataFrame):
    inst = MACD(data_pd['close'])
    data_pd['macd'] = round(inst.macd_diff() * 2, 3)
    data_pd['macd_dea'] = round(inst.macd_signal(), 3)
    data_pd['macd_diff'] = round(inst.macd(), 3)
    return data_pd