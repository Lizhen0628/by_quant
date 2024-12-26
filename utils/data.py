
import os
import requests
import pandas as pd
import pytz
import akshare
from tqdm import tqdm
from typing import Dict
from datetime import date,datetime,timedelta
from pandas import DataFrame
from .adjustment import process_forward
from functools import lru_cache


from .env import LOCAL_DAILY_FILE,DAILY_DIR, LOCAL_ADJUSTMENT_FILE,SECRET


@lru_cache(maxsize=10) # 数据量比较大，缓存到内存中
def get_local_daily_data(data_file = LOCAL_DAILY_FILE) -> DataFrame:
    """获取本地日K数据"""
    if data_file.exists():
        data_pd = pd.read_csv(data_file)
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

    data_pd.to_csv(data_file,index=False)
    return data_pd

@lru_cache(maxsize=10)
def get_local_adjustment_data(data_file = LOCAL_ADJUSTMENT_FILE):
    """获取本地除权数据"""
    return pd.read_csv(LOCAL_ADJUSTMENT_FILE)


def get_data_from_ak(symbol,name, max_timestamp):
    """从ak上获取最新数据"""
    code = symbol
    if '.' in symbol:
        code = symbol.split('.')[0]
    # 指定时区为东八区（Asia/Shanghai）
    timezone = pytz.timezone('Asia/Shanghai')
    start_date = date.fromtimestamp(max_timestamp / 1000 )
    start_date = start_date.strftime('%Y%m%d')

    # 当日17点之前刷数
    if datetime.now().hour > 15 and datetime.now().minute > 5:
        end_date = f"{date.today().strftime("%Y%m%d")}"
    else:
        end_date = f"{(date.today() - timedelta(1)).strftime("%Y%m%d")}"

    data_pd = akshare.stock_zh_a_hist(symbol=code, period='daily',start_date=start_date, end_date=end_date,adjust="")
    if data_pd is None or len(data_pd) == 0:
        return
    data_pd.rename(columns={"日期":"datetime", "股票代码":"symbol", "开盘":"open", "收盘":"close","最高":"high","最低":"low","成交量":"volume","成交额":"amount"},inplace=True)

    data_pd["symbol"] = symbol
    data_pd["name"] = name
    data_pd["suspendFlag"] = 0
    data_pd['amount'] = data_pd['amount'].apply(float)
    data_pd['timestamp'] = data_pd['datetime'].apply(lambda x : int(pd.Timestamp(x,tz=timezone).timestamp()) * 1000)
    data_pd['datetime'] = data_pd['datetime'].apply(lambda x : x.strftime('%Y-%m-%d %H:%M:%S'))

    data_pd['preClose'] = data_pd['close'].shift(1)
    data_pd.dropna(axis=0,inplace=True)
    data_pd = data_pd[['timestamp', 'datetime', 'symbol', 'name', 'open', 'high', 'low','close', 'preClose', 'volume', 'amount', 'suspendFlag']]
    return data_pd

def select_data(data_pd, adjustment_pd, symbol):
    data_pd = data_pd[data_pd['symbol'] == symbol]
    adjustment_pd = adjustment_pd[adjustment_pd['symbol'] == symbol]
    return data_pd, adjustment_pd

def get_local_forward_daily_data(forward_file = DAILY_DIR / "forward" / "forward_daily.csv"):
    """获取前复权处理后的所有日K数据"""
    if forward_file.exists():
        data_pd = pd.read_csv(forward_file)
        return data_pd
    
    forward_file.parent.mkdir(parents=True, exist_ok=True)

    # 复权数据
    adjustment_file = DAILY_DIR / 'stock_adjustments.csv'
    adjustment_pd = pd.read_csv(adjustment_file)
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


def request_market_daily_online(symbol, max_timestamp):
    """在线获取日K行情数据"""
    start_date = start_date = f"{(date.fromtimestamp(max_timestamp / 1000) + timedelta(1)).isoformat()} 00:00:00"
     # 当日17点之前刷数
    if datetime.now().hour > 17 :
        end_date = f"{date.today().isoformat()} 00:00:00"
    else:
        end_date = f"{(date.today() - timedelta(1)).isoformat()} 00:00:00"
    if start_date > end_date:
        return
    json_data = {
        "secret": SECRET,
        "symbol": symbol,
        "startTime": start_date,
        "endTime": end_date,
        "frequency": "1d"
    }
    response = requests.post("https://api.geeksphere.online/admin-api/stock/market/get",json=json_data)
    if response.status_code == 200:
        datas = response.json()['data']
        return pd.DataFrame(datas)
    print(response)

def request_market_adjustment_online(symbol, max_timestamp):
    """在线获取除权信息"""

    start_date = start_date = f"{(date.fromtimestamp(max_timestamp / 1000) + timedelta(1)).isoformat()} 00:00:00"
     # 当日17点之前刷数
    if datetime.now().hour > 17 :
        end_date = f"{date.today().isoformat()} 00:00:00"
    else:
        end_date = f"{(date.today() - timedelta(1)).isoformat()} 00:00:00"
    if start_date > end_date:
        return
    json_data = {
        "secret": SECRET,
        "symbol": symbol,
        "startTime": start_date,
        "endTime": end_date,
    }

    response = requests.post("https://api.geeksphere.online/admin-api/stock/info/adjustment", json=json_data)
    if response.status_code == 200:
        datas = response.json()['data']
        return pd.DataFrame(datas)
    return response

def correct_symbol(symbol, data_pd):
    if '.' in symbol:
        return symbol
    
    return data_pd[data_pd['symbol'].str.contains(symbol)]['symbol'].unique()[0]


def get_daily_data(symbol:str):
    """ 自动获取本地和在线数据 
        @param symbol: 股票代码【002385.SZ】
        @param local_daily_pd: 本地日K数据
        @param local_adjustment_pd: 本地除权数据
        @return (日线数据、 除权数据)
    """

    # 1. 获取本地日K数据 和 除权数据
    local_daily_pd = get_local_daily_data()
    local_adjustment_pd = get_local_adjustment_data()
    symbol = correct_symbol(symbol, local_daily_pd)
    local_symbol_daily_pd = local_daily_pd[local_daily_pd['symbol'] == symbol]
    name = local_symbol_daily_pd['name'].iloc[0]
    local_symbol_adjustment_pd = local_adjustment_pd[local_adjustment_pd['symbol'] == symbol]

    
    if SECRET == "" or SECRET == "your_secret_key_here":
        return local_symbol_daily_pd, local_symbol_adjustment_pd
    
    # 2. 获取在线数据
    # 请求在线数据
    max_timestamp = local_symbol_daily_pd['timestamp'].max()
    online_symbol_daily_pd = get_data_from_ak(symbol=symbol, name=name,max_timestamp=max_timestamp)
    if online_symbol_daily_pd is None or len(online_symbol_daily_pd) == 0:
        online_symbol_daily_pd = request_market_daily_online(symbol,max_timestamp)

    # 除权数据
    online_symbol_adjustment_pd = request_market_adjustment_online(symbol, max_timestamp)

    # 3. 将在线数据保存到本地
    daily_pd = pd.concat([local_daily_pd, online_symbol_daily_pd])
    adjustment_pd = pd.concat([local_adjustment_pd, online_symbol_adjustment_pd])
    daily_pd.to_csv(LOCAL_DAILY_FILE, index=False)
    adjustment_pd.to_csv(LOCAL_ADJUSTMENT_FILE, index=False)

    # 4. 返回结果
    return pd.concat([local_symbol_daily_pd, online_symbol_daily_pd]), pd.concat([local_symbol_adjustment_pd, online_symbol_adjustment_pd])


def get_forward_data(symbol:str):
    """获取前复权后到数据"""
    # 补全在线数据
    daily_pd, adjustment_pd = get_daily_data(symbol)
    # 计算前复权价格
    forward_pd = process_forward(daily_pd, adjustment_pd)
    if 'preClose' in forward_pd.columns:
        forward_pd.drop(columns='preClose', inplace=True)
    forward_pd.sort_values(by="datetime",inplace=True)
    return forward_pd