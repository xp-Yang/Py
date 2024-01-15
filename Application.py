import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
import Canvas
import threading
import sys
import backtesting as bt
from strategy import Strategy
from strategy import StrategyType
from strategy import StrategyConfig
from strategy import StrategyOutput
import ExcelLoader

root = None

class Logger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, message):
        self.textbox.insert(tk.END, message)
        self.textbox.see(tk.END)

    def flush(self):
        pass

# 按钮事件：选择并加载加载excel文件，并自动执行多种策略，自动配置最佳策略参数，gui上回显最佳策略参数，用虚线画出所有策略，画出最佳策略的买入和卖出点
# 其他参数事件：从gui获取新参数，根据新的参数重新执行一遍相应策略，更新图像
    
class Application:
    def __init__(self):
        self.plot_thread = None
        self.init_strategy()
        self.create()

    def init_strategy(self):
        self.init_capital = 100000
        self.best_strategy = None
        self.sma_sttg = None
        self.ema_stth = None

    def create(self):
        global root

        root = tk.Tk()
        root.title("Trade")

        # 创建选择文件按钮
        button = ttk.Button(root, text="选择文件", command=self.open_file_dialog)
        button.pack()
        self.file_str_label = tk.Label(root, text='')
        self.file_str_label.pack()

        # 创建Frame用以布局
        content_frame = ttk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True)

        content_left_frame = ttk.Frame(content_frame)
        content_left_frame.pack(side="left", fill=tk.BOTH, expand=True)

        content_right_frame = ttk.Frame(content_frame)
        content_right_frame.pack(side="right", fill=tk.BOTH, expand=True)

        # 创建step控件
            # 创建Label
        step_text_label = tk.Label(content_left_frame, text="Step:")
        step_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.step_spinbox_value = tk.IntVar(value = 3)
        step_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=100, increment = 1, textvariable=self.step_spinbox_value, command=self.update_strategy_config)
        step_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建increase_threshold控件
            # 创建Label
        increase_text_label = tk.Label(content_left_frame, text="涨幅阈值:")
        increase_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.increase_spinbox_value = tk.DoubleVar(value = 0.01)
        increase_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=1, increment = 0.001, textvariable=self.increase_spinbox_value, command=self.update_strategy_config)
        increase_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建ma滑动窗口slider控件
                    # 创建Label
        sma_period_text_label = tk.Label(content_left_frame, text="SMA滑动窗口:")
        sma_period_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.sma_period_spinbox_value = tk.IntVar(value=20)
        sma_period_spinbox = ttk.Spinbox(content_left_frame, from_=1, to=999, increment = 1, textvariable=self.sma_period_spinbox_value, command=self.update_strategy_config)
        sma_period_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        ema_period_text_label = tk.Label(content_left_frame, text="EMA滑动窗口:")
        ema_period_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.ema_period_spinbox_value = tk.IntVar(value=20)
        ema_period_spinbox = ttk.Spinbox(content_left_frame, from_=1, to=999, increment = 1, textvariable=self.ema_period_spinbox_value, command=self.update_strategy_config)
        ema_period_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建本金控件
            # 创建Label
        capital_text_label = tk.Label(content_left_frame, text="本金:")
        capital_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.capital_spinbox_value = tk.IntVar(value = self.init_capital)
        capital_spinbox = ttk.Spinbox(content_left_frame, from_=1, to=99999999999, increment = 5000, textvariable=self.capital_spinbox_value, command=self.update_strategy_config)
        capital_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建日志区域
            # 创建Label
        log_label = tk.Label(content_left_frame, text="Log:")
        log_label.pack(side="top", anchor='nw', padx=10)
            # 创建log区域
        log = scrolledtext.ScrolledText(content_left_frame, width = 30, height = 10)
        log.pack(side="top", anchor='nw', fill=tk.BOTH, expand=True, padx=10)
        log.config(width=50)
        # 重定向 print 输出到日志文本框
        sys.stdout = Logger(log)

        # 创建刷新图像按钮
        refresh_button = ttk.Button(content_right_frame, text="刷新图像", command=self.refresh_canvas)
        refresh_button.pack(side="top", anchor='ne')

        # 创建矩形区域并在矩形区域上绘制曲线
        self.canvas = Canvas.myCanvas(content_right_frame)
        self.tkCanvas = self.canvas.get()
        self.tkCanvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self):
        global root
        root.mainloop()

    # UI驱动数据更新--控件事件
    def update_strategy_config(self):
        self.init_capital = int(self.capital_spinbox_value.get())
        int(self.step_spinbox_value.get())
        float(self.increase_spinbox_value.get())
        self.sma_sttg.config.period = int(self.sma_period_spinbox_value.get())
        self.ema_sttg.config.period = int(self.ema_period_spinbox_value.get())

        self.sma_sttg.output = self.sma_sttg.calc_strategy_result(self.sma_sttg.config)
        self.ema_sttg.output = self.ema_sttg.calc_strategy_result(self.ema_sttg.config)

        self.refresh_canvas()

    # 数据驱动UI更新--自动寻找最优参数
    def notify_gui_update(self):
        self.capital_spinbox_value.set(self.init_capital)
        self.step_spinbox_value.set(0)
        self.increase_spinbox_value.set(0)
        self.sma_period_spinbox_value.set(self.sma_sttg.config.period)
        self.ema_period_spinbox_value.set(self.ema_sttg.config.period)

        self.refresh_canvas()

    def update_canvas(self):
        #times = self.loader.get_column(0)
        prices = self.loader.get_column(1)
        times = range(len(prices))

        sma_curve = self.sma_sttg.output.curve
        ema_curve = self.ema_sttg.output.curve
        self.canvas.clear()
        self.canvas.draw_curve(times, prices, '-')
        self.canvas.draw_curve(times, sma_curve, '--')
        self.canvas.draw_curve(times, ema_curve, '--')

        buy_index_list = self.best_strategy.output.buy_index_list
        sell_index_list = self.best_strategy.output.sell_index_list
        buy_points_times = [times[x] for x in buy_index_list]
        buy_points_prices = [prices[x] for x in buy_index_list]
        self.canvas.draw_points(buy_points_times, buy_points_prices, 'g.')
        sell_points_times = [times[x] for x in sell_index_list]
        sell_points_prices = [prices[x] for x in sell_index_list]
        self.canvas.draw_points(sell_points_times, sell_points_prices, 'r.')

    # 创建按钮点击事件
    def open_file_dialog(self):
        # 打开文件选择对话框
        self.file_path = filedialog.askopenfilename()
        print("选择的文件:", self.file_path)
        self.loader = ExcelLoader.myExcelLoader(self.file_path)
        self.find_best_strategy_config()
        self.file_str_label.config(text=self.file_path)

    def refresh_canvas(self):
        # 创建并启动线程
        # 如果线程已经在运行，则忽略启动请求
        if self.plot_thread and self.plot_thread.is_alive():
            print("is plotting!")
        else:
            self.plot_thread = threading.Thread(target=self.update_canvas)
            self.plot_thread.start()

    def find_best_strategy_config(self):
        price_list = self.loader.get_column(1)

        self.sma_sttg = Strategy(StrategyType.SMA, self.init_capital, price_list)
        sma_best_cfg, sma_best_return_rate = self.sma_sttg.find_best_strategy_config()

        self.ema_sttg = Strategy(StrategyType.EMA, self.init_capital, price_list)
        ema_best_cfg, ema_best_return_rate = self.ema_sttg.find_best_strategy_config()

        if sma_best_return_rate > ema_best_return_rate:
            self.best_strategy = self.sma_sttg
        else:
            self.best_strategy = self.ema_sttg

        print("----------------------------------------")
        print("SMA最佳滑窗：{}, 最佳收益率：{:.3f}%".format(sma_best_cfg.period, sma_best_return_rate * 100))
        print("EMA最佳滑窗：{}, 最佳收益率：{:.3f}%".format(ema_best_cfg.period, ema_best_return_rate * 100))
        print("大盘指数：{:.3f}%".format(100 * (price_list[len(price_list)-1] - price_list[0]) / price_list[0]))
        print("----------------------------------------")

        self.notify_gui_update()

        #calc_thread = None
        #if calc_thread and calc_thread.is_alive():
        #    print("is calculating!")
        #else:
        #    calc_thread = threading.Thread(target=)
        #    calc_thread.start()
        #    print("start calculating")

if __name__ == "__main__":
    __app = Application()
    __app.run()