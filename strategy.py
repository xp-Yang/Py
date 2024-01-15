from enum import Enum
import backtesting as bt
import copy

## 一个回测策略可能是多个回测算法的组合

class StrategyType(Enum):
    SlopeIn = 1
    SlopeInOut = 2
    SMA = 3
    EMA = 4

# 策略的输入参数
class StrategyConfig:
    def __init__(self, period = 20, buy_slope = 0.01, buy_slope_span = 3, sell_slope = 0.01, sell_slope_span = 3):
        self.period = period
        
        self.buy_slope = buy_slope
        self.buy_slope_span = buy_slope_span
        self.sell_slope = sell_slope
        self.sell_slope_span = sell_slope_span

# 策略的输出
class StrategyOutput:
    def __init__(self, capital = 0, stock_count = 0, buy_index_list = [], sell_index_list = [], curve = []):
        self.capital = capital
        self.stock_count = stock_count
        self.buy_index_list = buy_index_list
        self.sell_index_list = sell_index_list
        self.curve = curve
        pass

class Strategy:
    def __init__(self, strategy_type, init_capital, price_list):
        self.type = strategy_type
        self.init_capital = init_capital
        self.price_list = price_list
        self.config = StrategyConfig()
        self.output = StrategyOutput()

    def set_init_capital(self, init_capital):
        self.init_capital = init_capital

    def set_price_list(self, price_list):
        self.price_list = price_list

    def set_strategy_config(self, strategy_config):
        self.config = strategy_config

    # 返回最佳参数和该参数下的最佳收益率
    def find_best_strategy_config(self):
        sttg_cfg = StrategyConfig()
        if self.type == StrategyType.SMA or self.type == StrategyType.EMA:
            best_return_rate = -1
            best_sttg_cfg = None
            best_sttg_output = None
            for i in range(1, len(self.price_list)):
                sttg_cfg.period = i
                sttg_output = self.calc_strategy_result(sttg_cfg)
                total_profit = sttg_output.capital - self.init_capital + sttg_output.stock_count * self.price_list[len(self.price_list)-1]
                return_rate =  total_profit / self.init_capital
                if return_rate > best_return_rate:
                    best_return_rate = return_rate
                    best_sttg_cfg = copy.copy(sttg_cfg)
                    best_sttg_output = sttg_output
        
        self.config = best_sttg_cfg
        self.output = best_sttg_output
        return (best_sttg_cfg, best_return_rate)

    # 统一回测算法输出的数据结构为StrategyOutput
    def calc_strategy_result(self, strategy_config):
        sttg_cfg = strategy_config
        out = None
        if self.type == StrategyType.SlopeIn:
            out = bt.slope_in_directly_out(self.price_list, self.init_capital, sttg_cfg.buy_slope, sttg_cfg.buy_slope_span)
        if self.type == StrategyType.SlopeInOut:
            out = bt.slope_in_slope_out(self.price_list, self.init_capital, sttg_cfg.buy_slope, sttg_cfg.sell_slope)
        if self.type == StrategyType.SMA:
            out = bt.SMA(self.price_list, self.init_capital, sttg_cfg.period)
        if self.type == StrategyType.EMA:
            out = bt.EMA(self.price_list, self.init_capital, sttg_cfg.period)
        return StrategyOutput(out[0], out[1], out[2], out[3], out[4])