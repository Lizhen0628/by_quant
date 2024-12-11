# by_quant

## 介绍
引用一段网友的话：

> 交易这门手艺发展了这么多年，流派可谓五花八门，有看基本面搞价值投资的，有看K线搞技术指标的，有学江恩，缠论数波浪画中枢的，有分析资金面的，分析市场情绪的，有结合原始数据做日内波段的，有恨不得把服务器架在交易所对面做高频的，有搞一箱子GPU做automl，深度学习和强化学习的，有搞对冲的，搞多因子的，搞指数增强的，有搞MOM组合管理的，有搞一堆艰深晦涩的微分方程做衍生品套利的，当然，也有靠求神拜佛和拍脑门跺地板的。每种流派都有一些人奉为圭臬，还有一批人弃如敝履，而且时不时的还会冒出几个新的流派出来，令人眼花缭乱，有些摸不到头脑。

> 不知道哪个著名的人曾说过，如果你没有自己的思想，那你的脑子注定会成为其他人思想的跑马场。上面的这一堆思想和流派，既然能够出现并且流传下来，还能够有一批拥趸和死忠，也就表明它们确实是市场的本质或者圣杯在某个维度的一个映射或投影，但也仅仅只是一个投影而已。学习它们只是为了能够从更多的角度去窥视那个交易的圣杯，进而一点点的深化，完善和验证自己的交易思想和理论体系，最终通过一个承载着自己思想体系的工具来将思想兑换成实际的收益。在这个市面上出现的每一种付费编译的或者免费开源的交易软件都是固定的，即使在不断更新迭代也只是按照开发团队的思路来进行，包括QA在内，不可能有一个软件或者项目能够满足所有可能的交易思想，自然也就无法让你自由的学习，验证，归纳和吸收这些思想中的精华。因此，如果你没有定制化的开发交易工具的能力，而只能使用现有的工具的话，你的思想和自由意志就这样被别人的工具所局限住了。

## 1. 环境安装

### 1.1 下载安装conda
[清华anacodna开源站](https://mirror.tuna.tsinghua.edu.cn/help/anaconda/)

### 1.2 配置开发环境
安装好anaconda之后，使用以下命令创建python 虚拟环境：
```bash
conda create -n quant python=3.12 -y

conda activate quant

pip install -r requirements.txt
```


## 2. 数据

### 2.1 数据准备

1. 购买数据: 
2. 将数据放在～/.quant目录下。
    - 天级更新的数据放到【包含复权数据】: `~/.quant/daily`
    - 分钟级更新的数据放到: `~/.quant/minute`

3. 密钥设置，密钥购买：

    - windows 系统：
        1. 打开“控制面板” -> “系统和安全” -> “系统”。
        2. 点击左侧的“高级系统设置”。
        3. 在弹出的窗口中点击“环境变量”按钮。
        4. 在“用户变量”或“系统变量”的部分，选择“新建”，然后输入变量名 BY_QUANT_KEY 和它的值。
        5. 应用更改并关闭所有窗口。
    - linux/macos：
        1. 通过编辑shell配置文件来永久设置环境变量。例如，在bash中，你可以在`.bash_profile` 、`.bashrc` 或 `.zshrc`文件中添加如下行：
            ```bash
            export BY_QUANT_KEY="your_api_key_here"
            ```
        2. 保存文件后，运行 `source ~/.bash_profile` 、 `source ~/.bashrc` 或 `source ~/.zshrc`使更改生效。
    - 或者将密钥写到utils/env.py 文件中：`SECRET = os.getenv("BY_QUANT_KEY",default="your_secret_key_here")`。使用密钥替换字符:your_secret_key_here


### 2.2 数据使用

1. 获取原始日K数据
    ```python
    from utils import get_daily_data,get_local_daily_data,get_local_adjustment_data

    local_daily_pd = get_local_daily_data()
    local_adjustment_pd = get_local_adjustment_data()
    data_pd, adjustment_pd = get_daily_data("002385", local_daily_pd, local_adjustment_pd)

    data_pd.tail(3)
    ```
2. 获取前复权数据
    ```python
    from utils import get_forward_data,get_local_daily_data,get_local_adjustment_data

    local_daily_pd = get_local_daily_data()
    local_adjustment_pd = get_local_adjustment_data()
    data_pd = get_forward_data("002385", local_daily_pd, local_adjustment_pd)

    data_pd.tail()
    ```
    对比股票软件上的数据，是否数据能够保持一致。
    > 同通信达股票软件数据对比，确认一致。


## 3. 计算指标
计算指标放在`indicator`目录下

示例：计算macd
```python
    from utils import get_forward_data,get_local_daily_data,get_local_adjustment_data
    from indicator import macd
    
    local_daily_pd = get_local_daily_data()
    local_adjustment_pd = get_local_adjustment_data()
    data_pd = get_forward_data("002385", local_daily_pd, local_adjustment_pd)

    # 删除停牌数据
    data_pd = data_pd[data_pd['suspendFlag'] == 0]
    data_pd.drop(columns='suspendFlag', inplace=True)

    data_pd = macd(data_pd)

    data_pd.head()
```
 > 同通信达股票软件数据对比，确认一致。


## 4. 编写策略及回测
```python
    from utils import get_forward_data,get_local_daily_data,get_local_adjustment_data
    from indicator import macd,rsi
    import pandas as pd
    import pybroker
    from pybroker import Strategy,StrategyConfig
    import matplotlib.pyplot as plt

    local_daily_pd = get_local_daily_data()
    local_adjustment_pd = get_local_adjustment_data()
    data_pd = get_forward_data("002385", local_daily_pd, local_adjustment_pd)

    # 删除停牌数据
    data_pd = data_pd[data_pd['suspendFlag'] == 0]
    data_pd.drop(columns='suspendFlag', inplace=True)

    data_pd = macd(data_pd)
    data_pd = rsi(data_pd)

    data_pd['date'] = pd.to_datetime(data_pd['datetime'])

    # 注册指标到pybroker
    pybroker.register_columns('rsi')

    # 初始化资金:50000元
    config = StrategyConfig(initial_cash=50000)

    strategy = Strategy(data_pd, '4/1/2021', '09/12/2024',config=config)


    # 定义策略
    def buy_low_sell_high_rsi(ctx):
        pos = ctx.long_pos()
        if not pos and ctx.rsi[-1] < 30:
            ctx.buy_shares = 100
        elif pos and ctx.rsi[-1] > 70:
            ctx.sell_shares = pos.shares

    # 注册策略到pybroker
    strategy.add_execution(buy_low_sell_high_rsi, ['002385.SZ'])


    # 回测
    result = strategy.backtest()

    # 绘制收益曲线
    chart = plt.subplot2grid((3, 2), (0, 0), rowspan=3, colspan=2)
    chart.plot(result.portfolio.index, result.portfolio['market_value'])

```