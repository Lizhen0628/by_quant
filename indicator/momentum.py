from ta.wrapper import RSIIndicator
from pandas import DataFrame

def rsi(data_pd:DataFrame) -> DataFrame:

    inst = RSIIndicator(data_pd['close'])

    data_pd['rsi'] = round(inst.rsi(),3)

    return data_pd