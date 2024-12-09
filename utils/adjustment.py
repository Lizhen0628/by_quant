import pandas as pd



def process_forward(symbol_pd, adjustment_pd):
    """前复权"""
    symbol_pd.set_index('datetime',inplace=True)
    adjustment_pd.set_index('datetime', inplace=True)
    def calc_front(v, d):
        return round(
            (v - d['interest'] + d['allotPrice'] * d['allotNum'])
            / (1 + d['allotNum'] + d['stockBonus'] + d['stockGift'])
            , 2
        )
    datas = []
    for qi in range(len(symbol_pd)):
        q = symbol_pd.iloc[qi]
        open = q['open']
        high = q['high']
        low = q['low']
        close = q['close']

        for di in range(len(adjustment_pd)):
            d = adjustment_pd.iloc[di]
            if d.name <= q.name:
                continue
            open = calc_front(open, d)
            high = calc_front(high, d)
            low = calc_front(low, d)
            close = calc_front(close, d)

        datas.append({
            **q,
            "datetime":q.name,
            "open":open,
            "high":high,
            "low":low,
            "close":close
        })
    return pd.DataFrame(datas)

def process_backward(symbol_pd, adjustment_pd):
    """后复权"""
    symbol_pd.set_index('datetime',inplace=True)
    adjustment_pd.set_index('datetime', inplace=True)
    def calc_front(v, d):
        return round(
            (v * (1 + d['stockGift'] + d['stockBonus'] + d['allotNum'])
            + d['interest'] - d['allotNum'] * d['allotPrice'])
            , 2
        )
    datas = []
    for qi in range(len(symbol_pd)):
        q = symbol_pd.iloc[qi]
        open = q['open']
        high = q['high']
        low = q['low']
        close = q['close']

        for di in range(len(adjustment_pd)):
            d = adjustment_pd.iloc[di]
            if d.name > q.name:
                continue
            open = calc_front(open, d)
            high = calc_front(high, d)
            low = calc_front(low, d)
            close = calc_front(close, d)
        datas.append({
            **q,
            "datetime":q.name,
            "open":open,
            "high":high,
            "low":low,
            "close":close
        })
    return pd.DataFrame(datas)

