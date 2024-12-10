# by_quant

## 介绍


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
    from utils import get_daily_data

    data_pd = get_daily_data("002385.SZ")
    ```
2. 获取前复权数据
    ```python
    from utils import get_forward_data

    data_pd = get_forward_data("002385.SZ")
    ```

3. 计算指标


4. 编写策略


5. 回测