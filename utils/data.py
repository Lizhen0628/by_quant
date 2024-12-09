
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm
from .data_path import DAILY_DIR
from .adjustment import process_forward


def get_daily_data(symbol:str):
    # 本地数据
    local_pd = get_local_daily_data()
    

    # 在线数据


    # 合并数据


    # 保存本地

    return local_pd


def get_local_daily_data(data_file = DAILY_DIR / "k_daily_all.csv") -> DataFrame:
    """获取本地日K数据"""
    if data_file.exists():
        data_pd = pd.read_csv(data_file)
        data_pd['datetime'] = pd.to_datetime(data_pd['datetime'], format="ISO8601")
        return data_pd

    # 按照年度合并所有日K数据
    datas = []
    for year in range(2024, 1989, -1):
        data_year_file = DAILY_DIR / f'k_daily_{year}.csv'
        if not data_year_file.exists():
            continue
        temp_pd = pd.read_csv(data_year_file)
        datas.append(temp_pd)
    data_pd = pd.concat(datas)
    
    columns = ['id', 'settelementPrice', 'openInterest']
    for col in columns:
        if col in data_pd.columns:
            data_pd.drop(columns=col, inplace=True)

    data_pd['datetime'] = pd.to_datetime(data_pd['datetime'], format="ISO8601")
    data_pd.to_csv(data_file,index=False)
    return data_pd

def select_data(data_pd, adjustment_pd, symbol):
    data_pd = data_pd[data_pd['symbol'] == symbol]
    adjustment_pd = adjustment_pd[adjustment_pd['symbol'] == symbol]
    return data_pd, adjustment_pd

def get_local_forward_daily_data(forward_file = DAILY_DIR / "forward" / "forward_daily.csv"):
    """获取前复权处理后的所有日K数据"""
    if forward_file.exists():
        data_pd = pd.read_csv(forward_file)
        data_pd['datetime'] = pd.to_datetime(data_pd['datetime'], format="ISO8601")
        return data_pd
    
    forward_file.parent.mkdir(parents=True, exist_ok=True)

    # 复权数据
    adjustment_file = DAILY_DIR / 'stock_adjustments.csv'
    adjustment_pd = pd.read_csv(adjustment_file)
    adjustment_pd['datetime'] = pd.to_datetime(adjustment_pd['datetime'], format="ISO8601")
    # 日K数据
    daily_file = DAILY_DIR / "k_daily_all.csv"
    data_pd = get_local_daily_data(daily_file)

    # 所有股票代码
    symbols = data_pd['symbol'].unique().tolist()

    datas = []
    # 计算复权必须按照股票纬度来处理
    for symbol in tqdm(symbols,desc="日K复权数据处理..."):
        symbol_pd,adjustment_symbol_pd = select_data(data_pd, adjustment_pd, symbol)
        forward_pd = process_forward(symbol_pd, adjustment_symbol_pd)
        datas.append(forward_pd)
    
    data_pd = pd.concat(datas)

    data_pd.to_csv(forward_file,index=False)
    return data_pd