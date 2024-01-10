charge_rate = 0.025 # 手续费

def slope_in_directly_out(data, init_capital, buy_slope):
    interval = 8 # interval天后卖出
    step = 1 # 每天计算一次涨跌
    capital = init_capital

    k_dict = {}
    k_filtered_dict = {}

    k_dict = {i : (data[i] - data[i - step]) / data[i] for i in range(step, len(data))} # 差分斜率
    k_filtered_dict = {i : k_dict[i] for i in k_dict if k_dict[i] > buy_slope} # 符合条件的斜率

    bought_index = []
    for n in range(step, len(data)): 
        need_sell = False
        if (n - interval) > 0 and (n - interval) in bought_index:
            need_sell = True
        if need_sell:
            capital += data[n] * (1 - charge_rate)

        need_buy = False
        if (n + interval) < len(data) and n in k_filtered_dict:
            need_buy = True
        if need_buy:
            if capital - data[n] > 0:
                capital -= data[n]
                bought_index.append(n)

        print("第{}天，涨幅：{:.4f}，本金：{:.2f}，{} {}".format(n, k_dict[n], capital, "卖出" if need_sell else " ", "买入" if need_buy else ""))

    print("净收入：", capital - init_capital)

    buy_index_list = bought_index
    sell_index_list = [x + interval for x in bought_index]

    return (capital, buy_index_list, sell_index_list)

def slope(data, init_capital, buy_slope, sell_slope):
    interval = 8 # interval天后卖出
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
        if (n - interval) > 0 and (n - interval) in bought_index and n in k_to_sell_dict:
            need_sell = True
        if need_sell:
            capital += data[n] * (1 - charge_rate)
            stock_count -= 1

        need_buy = False
        if (n + interval) < len(data) and n in k_to_buy_dict:
            need_buy = True
        if need_buy:
            if capital - data[n] > 0:
                capital -= data[n]
                stock_count += 1
                bought_index.append(n)

        print("第{}天，涨幅：{:.4f}，本金：{:.2f}，{} {}".format(n, k_dict[n], capital, "卖出" if need_sell else " ", "买入" if need_buy else ""))

    print("库存价值：{}".format(stock_count * data[len(data) - 1]))

    buy_index_list = bought_index
    sell_index_list = [x + interval for x in bought_index]

    return (capital, buy_index_list, sell_index_list)

def EMA(data, init_capital, window = 20):
    pass

def SMA(data, init_capital, window = 20):
    ma = []
    for i in range(len(data)):
        if i < window:
            ma.append(0)
        else:
            ma.append(sum(data[i-window:i]) / window)
    
    capital = init_capital
    cd_interval = 80 # interval天后才可卖出

    buy_index_list = []
    buying_index_list = []
    sell_index_list = []
    for i in range(len(data)):
        if i < window:
            pass
        else:
            if data[i] > ma[i]:  # 当价格突破 MA_window 时买入
                if capital - data[i] > 0:
                    capital -= data[i]
                    buy_index_list.append(i)
                    buying_index_list.append(i)
            elif data[i] < ma[i]:  # 当价格跌破 MA_window 时卖出
                for index, bought_day in enumerate(buying_index_list):
                    if (i - bought_day) > cd_interval:
                        del buying_index_list[index]
                        capital += data[i] * (1 - charge_rate)
                        sell_index_list.append(i)

    print("库存价值：{}".format(len(buying_index_list) * data[len(data) - 1]))
    return (capital, buy_index_list, sell_index_list, ma)