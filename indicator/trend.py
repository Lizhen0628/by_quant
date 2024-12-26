
from pandas import DataFrame
from ta.wrapper import MACD

from utils.calculate import EMA, RD


def MACD(CLOSE,SHORT=12,LONG=26,M=9):
    """
    """      
    # EMA的关系，S取120日，和雪球小数点2位相同
    DIF = EMA(CLOSE,SHORT)-EMA(CLOSE,LONG);  
    DEA = EMA(DIF,M);      
    MACD=(DIF-DEA)*2
    return RD(DIF),RD(DEA),RD(MACD)