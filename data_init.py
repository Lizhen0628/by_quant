

import pandas as pd

from utils import get_forward_daily_data


def data_init():
    # 1. 前复权数据处理
    get_forward_daily_data()


if __name__ == '__main__':
    get_forward_daily_data()