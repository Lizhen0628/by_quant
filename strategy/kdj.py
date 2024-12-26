import numpy as np




def kdj_over_boughtsold_strategy(ctx):
    """策略:kdj超买超卖
    当%K值大于80时，市场可能处于超买状态；当%K值小于20时，市场可能处于超卖状态。
    
    该策略缺点：k值可能很长时间没有超过80,导致持仓太久，硬扛亏损
    """
    if ctx.bars < 20:
        return
    
    pos = ctx.long_pos()
    k = ctx.kdj_k

    # 超买超卖信号
    overbought = k[-1] > 80
    oversold = k[-1] < 20

    # k 值大于80 抛空
    if pos and overbought :
        ctx.sell_shares = pos.shares
    # k值小于20 做多两成仓位
    elif oversold:
        ctx.buy_shares = ctx.calc_target_shares(0.2)
    


def kdj_golden_death_cross(ctx):
    """策略：kdj金叉死叉
    金叉：当K值从下向上穿过D线时，表示可能形成买入信号。
    死叉：当K值从上向下穿过D线时，表示可能形成卖出信号。
    """

    if ctx.bars < 20:
        return 
    pos = ctx.long_pos()
    k = ctx.kdj_k
    d = ctx.kdj_d
    # 金叉死叉信号
    golden_cross = (k[-2] <= d[-2]) and (k[-1] > d[-1])
    death_cross = (k[-2] >= d[-2]) and (k[-1] < d[-1])

    # 金叉,做多
    if golden_cross:
        # print(ctx.date[-1], "long", f"{ctx.kdj_k[-2],} <= {ctx.kdj_d[-2]} and {ctx.kdj_k[-1]} >= {ctx.kdj_d[-1]}" ,)
        # 做多两成仓位
        ctx.buy_shares = ctx.calc_target_shares(0.2)
    
    # 死叉，抛空
    elif pos and death_cross:
        # print(ctx.date[-1], "short", f"{ctx.kdj_k[-2],} >= {ctx.kdj_d[-2]} and {ctx.kdj_k[-1]} <= {ctx.kdj_d[-1]}" ,)
        ctx.sell_shares = pos.shares



def kdj_divergence_strategy(ctx):
    """策略: KDJ 背离策略
    顶背离（Bullish Divergence）：价格创新高但%K值没有创新高。
    底背离（Bearish Divergence）：价格创新低但%K值没有创新低。
    
    该策略缺点：需要合理的窗口大小来检测背离。
    """
    pos = ctx.long_pos()
    
    if ctx.bars < 20:
        return
    
    # 定义一个窗口大小，用于检测背离
    window_size = 10
    
    # 获取最近窗口内的价格和K值数据
    prices = ctx.close[-window_size:]
    k = ctx.kdj_k[-window_size:]
    
    # 检测顶背离（Bullish Divergence）
    if pos is None:
        # 找到价格的最高点和对应的K值
        max_price_index = prices.argmax()
        max_price = prices[max_price_index]
        max_k_value = k[max_price_index]
        
        # 检查是否有更高的价格但K值没有创新高
        if all(prices[i] < max_price for i in range(window_size) if i != max_price_index):
            if any(k[i] > max_k_value for i in range(window_size) if i != max_price_index):
                # print(ctx.date[-1], "Bullish Divergence", f"Price: {max_price}, K: {max_k_value}")
                # 做多两成仓位
                ctx.buy_shares = ctx.calc_target_shares(0.2)
    
    # 检测底背离（Bearish Divergence）
    if pos:
        # 找到价格的最低点和对应的K值
        min_price_index = prices.argmin()
        min_price = prices[min_price_index]
        min_k_value = k[min_price_index]
        
        # 检查是否有更低的价格但K值没有创新低
        if all(prices[i] > min_price for i in range(window_size) if i != min_price_index):
            if any(k[i] < min_k_value for i in range(window_size) if i != min_price_index):
                # print(ctx.date[-1], "Bearish Divergence", f"Price: {min_price}, K: {min_k_value}")
                # 卖出所有仓位
                ctx.sell_shares = pos.shares




def kdj_signals(ctx):
    
    # 假设 ctx 包含 k, d, j 值以及价格数据
    k = ctx.kdj_k
    d = ctx.kdj_d
    price = ctx.close
    
    # 超买超卖信号
    overbought = k[-1] > 80
    oversold = k[-1] < 20
    
    # 金叉死叉信号
    golden_cross = (k[-2] <= d[-2]) and (k[-1] > d[-1])
    death_cross = (k[-2] >= d[-2]) and (k[-1] < d[-1])
    
    # 背离策略
    window_size = 14  # 窗口大小可以根据需要调整
    
    if len(price) >= window_size:
        prices = price[-window_size:]
        ks = k[-window_size:]
        
        # 顶背离检测
        max_price_index = np.argmax(prices)
        max_k_index = np.argmax(ks)
        bullish_divergence = (max_price_index == len(prices) - 1 and max_price_index != max_k_index)
        
        # 底背离检测
        min_price_index = np.argmin(prices)
        min_k_index = np.argmin(ks)
        bearish_divergence = (min_price_index == len(prices) - 1 and min_price_index != min_k_index)
    else:
        bullish_divergence = False
        bearish_divergence = False
    
    return {
        'overbought': overbought,
        'oversold': oversold,
        'golden_cross': golden_cross,
        'death_cross': death_cross,
        'bullish_divergence': bullish_divergence,
        'bearish_divergence': bearish_divergence
    }



def combined_strategy(ctx):
    if ctx.bars < 20:
        return
    
    signals = kdj_signals(ctx)
    
    overbought = signals['overbought']
    oversold = signals['oversold']
    golden_cross = signals['golden_cross']
    death_cross = signals['death_cross']
    bullish_divergence = signals['bullish_divergence']
    bearish_divergence = signals['bearish_divergence']
    
    # 获取当前持仓
    position = ctx.long_pos()
    
    # 初始仓位大小
    base_shares = ctx.calc_target_shares(0.2)  # 假设 calc_target_shares 计算目标仓位
    
    # 超买超卖优先级最高
    if position and overbought:
        # print(ctx.date[-1], "Overbought, Selling")
        ctx.sell_shares = position.shares
        return
    
    if oversold:
        # print(ctx.date[-1], "Oversold, Buying")
        ctx.buy_shares = base_shares
        return
    
    # 结合金叉死叉和背离策略
    buy_signals = [golden_cross, bullish_divergence]
    sell_signals = [death_cross, bearish_divergence]
    
    num_buy_signals = sum(buy_signals)
    num_sell_signals = sum(sell_signals)
    
    if num_buy_signals >= 1:
        # print(ctx.date[-1], "Multiple Buy Signals, Buying")
        ctx.buy_shares = base_shares * (num_buy_signals + 1)
    elif position and  num_sell_signals >= 1:
        # print(ctx.date[-1], "Multiple Sell Signals, Selling")
        ctx.sell_shares = position.shares
