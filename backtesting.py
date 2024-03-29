##回测算法合集，一个回测策略可能是多个回测算法的组合
##要求输入的data：一个list，索引i代表第i天，data[i]代表第i天的收盘价
##输出：本金剩余量，还未卖出的库存数量，买入天数索引，卖出天数索引，[ma list]

charge_rate = 0.025 #手续费
cd_interval = 8 #交易冷却时间

def slope_in_directly_out(data, init_capital, buy_slope, buy_slope_span = 3):
    global cd_interval
    
    capital = init_capital

    k_dict = {}
    k_filtered_dict = {}

    k_dict = {i : (data[i] - data[i - buy_slope_span]) / data[i] for i in range(buy_slope_span, len(data))} # 差分斜率
    k_filtered_dict = {i : k_dict[i] for i in k_dict if k_dict[i] > buy_slope} # 符合条件的斜率

    buy_index_list = []
    for n in range(buy_slope_span, len(data)): 
        need_sell = False
        if (n - cd_interval) > 0 and (n - cd_interval) in buy_index_list:
            need_sell = True
        if need_sell:
            capital += data[n] * (1 - charge_rate)

        need_buy = False
        if (n + cd_interval) < len(data) and n in k_filtered_dict:
            need_buy = True
        if need_buy:
            if capital - data[n] > 0:
                capital -= data[n]
                buy_index_list.append(n)

        #print("第{}天，涨幅：{:.4f}，本金：{:.2f}，{} {}".format(n, k_dict[n], capital, "卖出" if need_sell else " ", "买入" if need_buy else ""))

    print("净收入：", capital - init_capital)

    sell_index_list = [x + cd_interval for x in buy_index_list]

    return (capital, 0, buy_index_list, sell_index_list, [])

def slope_in_slope_out(data, init_capital, buy_slope, sell_slope):
    global cd_interval

    step = 1 # 每天计算一次涨跌
    capital = init_capital

    k_dict = {}
    k_to_buy_dict = {}
    k_to_sell_dict = {}

    k_dict = {i : (data[i] - data[i - step]) / data[i] for i in range(step, len(data))} # 差分斜率
    k_to_buy_dict = {i : k_dict[i] for i in k_dict if k_dict[i] > buy_slope}
    k_to_sell_dict = {i : k_dict[i] for i in k_dict if k_dict[i] < sell_slope}

    bought_index = []
    stock_count = 0 # 库存
    for n in range(step, len(data)): 
        need_sell = False
        if (n - cd_interval) > 0 and (n - cd_interval) in bought_index and n in k_to_sell_dict:
            need_sell = True
        if need_sell:
            capital += data[n] * (1 - charge_rate)
            stock_count -= 1

        need_buy = False
        if (n + cd_interval) < len(data) and n in k_to_buy_dict:
            need_buy = True
        if need_buy:
            if capital - data[n] > 0:
                capital -= data[n]
                stock_count += 1
                bought_index.append(n)

        print("第{}天，涨幅：{:.4f}，本金：{:.2f}，{} {}".format(n, k_dict[n], capital, "卖出" if need_sell else " ", "买入" if need_buy else ""))

    buy_index_list = bought_index
    sell_index_list = [x + cd_interval for x in bought_index]

    return (capital, stock_count, buy_index_list, sell_index_list, [])

def calc_sma(data, window):
    ma = []
    for i in range(len(data)):
        if i < (window - 1):
            ma.append(data[0])
        else:
            ma.append(sum(data[(i + 1 - window) : (i + 1)]) / window)
    return ma

def calc_sma_pd(data, rolling_window):
    return data.rolling(window=rolling_window).mean()

def calc_ema_(data, rolling_window, n, multiplier):
    if(n < 1):
        return data[0]
    return (multiplier * data[n] + (1 - multiplier) * calc_ema_(data, rolling_window, n - 1, multiplier))

def EMA(data, init_capital, window = 20):
    global cd_interval

    multiplier = 2 / (window + 1)
    ma = data.ewm(alpha=multiplier, adjust=False).mean()

    capital = init_capital

    buy_index_list = []
    buying_index_list = []
    sell_index_list = []
    for i in range(len(data)):
        if i < window:
            pass
        else:
            if data[i] > ma[i]:  # 当价格突破 MA 时买入
                if capital - data[i] > 0:
                    capital -= data[i]
                    buy_index_list.append(i)
                    buying_index_list.append(i)
            elif data[i] < ma[i]:  # 当价格跌破 MA 时卖出
                for index, bought_day in enumerate(buying_index_list):
                    if (i - bought_day) > cd_interval:
                        del buying_index_list[index]
                        capital += data[i] * (1 - charge_rate)
                        sell_index_list.append(i)

    stock_count = len(buying_index_list)
    return (capital, stock_count, buy_index_list, sell_index_list, ma)

def SMA(data, init_capital, window = 20):
    global cd_interval

    ma = calc_sma(data, window)
    
    capital = init_capital

    buy_index_list = []
    buying_index_list = []
    sell_index_list = []
    for i in range(len(data)):
        if i < window:
            pass
        else:
            if data[i] > ma[i]:  # 当价格突破 MA 时买入
                if capital - data[i] > 0:
                    capital -= data[i]
                    buy_index_list.append(i)
                    buying_index_list.append(i)
            elif data[i] < ma[i]:  # 当价格跌破 MA 时卖出
                for index, bought_day in enumerate(buying_index_list):
                    if (i - bought_day) > cd_interval:
                        del buying_index_list[index]
                        capital += data[i] * (1 - charge_rate)
                        sell_index_list.append(i)

    stock_count = len(buying_index_list)
    return (capital, stock_count, buy_index_list, sell_index_list, ma)