
def strategy(data):
    step = 1
    k = ((data[i + step] - data[i]) / data[i] for i in range(0, len(data) - step))

    buy_index = None
    sell_index = None

    increase_threshold = 0.1
    for i in range(len(k)):
        if k[i] > increase_threshold and buy_index is None:
            buy_index = i
            break

    sell_index = buy_index + 7
    income = data[sell_index] - data[buy_index]
    print("净收入：", income)

