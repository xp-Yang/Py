import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
import matplotlib
import matplotlib.style as plstyle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import sys
import backtesting as bt
import ExcelLoader
import time

root = None

class Logger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, message):
        self.textbox.insert(tk.END, message)
        self.textbox.see(tk.END)

    def flush(self):
        pass

class Application:
    def __init__(self):
        self.plot_thread = None
        self.strategy_result = ()
        self.step = 3
        self.increase_threshold = 0.003
        self.rolling_window = 20
        self.init_capital = 10000000

        self.create()

    def create(self):
        global root

        root = tk.Tk()
        root.title("Trade")

        # 创建选择文件按钮
        button = ttk.Button(root, text="选择文件", command=self.open_file_dialog)
        button.pack()

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
        self.step_spinbox_value = tk.IntVar(value = self.step)
        step_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=100, increment = 1, textvariable=self.step_spinbox_value, command=self.step_spinbox_cb)
        step_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建increase_threshold控件
            # 创建Label
        increase_text_label = tk.Label(content_left_frame, text="涨幅阈值:")
        increase_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.increase_spinbox_value = tk.DoubleVar(value = self.increase_threshold)
        increase_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=1, increment = 0.001, textvariable=self.increase_spinbox_value, command=self.increase_spinbox_cb)
        increase_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建ma滑动窗口slider控件
                    # 创建Label
        rolling_window_text_label = tk.Label(content_left_frame, text="MA滑动窗口:")
        rolling_window_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.rolling_window_spinbox_value = tk.IntVar(value=self.rolling_window)
        rolling_window_spinbox = ttk.Spinbox(content_left_frame, from_=1, to=999, increment = 1, textvariable=self.rolling_window_spinbox_value, command=self.rolling_window_spinbox_cb)
        rolling_window_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建本金控件
            # 创建Label
        capital_text_label = tk.Label(content_left_frame, text="本金:")
        capital_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.capital_spinbox_value = tk.IntVar(value = self.init_capital)
        capital_spinbox = ttk.Spinbox(content_left_frame, increment = 5000, textvariable=self.capital_spinbox_value, command=self.capital_spinbox_cb)
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
        plstyle.use('fast')
        matplotlib.use('Agg')
        plt.ioff()
        figure = plt.figure(figsize=(8, 6), dpi=100)
        self.axes = figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(figure, master=content_right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self):
        global root
        root.mainloop()

    def update_strategy_output(self, refresh_cvs=True):
        prices = self.loader.get_column(1)
        #res = bt.slope_in_directly_out(prices, self.init_capital, self.increase_threshold, self.step)
        #res = bt.slope(prices, self.init_capital, self.increase_threshold, 0)
        res = bt.SMA(prices, self.init_capital, self.rolling_window)
        self.strategy_result = res

        new_capital = res[0]
        stock_count = res[3]

        total_profit = new_capital - self.init_capital + stock_count * prices[len(prices)-1]
        print("------------", "滑动窗口： ", self.rolling_window, "------------")
        print("净收入：{}".format(total_profit))
        print("库存价值：{}".format(stock_count * prices[len(prices)-1]))
        print("大盘指数：{:.3f}%".format(100 * (prices[len(prices)-1] - prices[0]) / prices[0]))
        print("收益率：{:.3f}%".format(100 * total_profit / self.init_capital))

        if refresh_cvs:
            self.refresh_canvas()

        return total_profit / self.init_capital

    def update_canvas(self):
        print("\nstart plotting")

        start_time = time.perf_counter()

        #times = self.loader.get_column(0)
        prices = self.loader.get_column(1)
        times = range(len(prices))

        res = self.strategy_result
        if len(res) == 0:
            return

        buy_index_list = res[1]
        sell_index_list = res[2]
        ma_prices = res[4] if len(res) >=5 else prices

        self.axes.clear()

        self.axes.set_xticks([])
        self.axes.set_xticklabels([])
        self.axes.plot(times, prices)
        self.axes.plot(times, ma_prices, '--')
        buy_points_times = [times[x] for x in buy_index_list]
        buy_points_prices = [prices[x] for x in buy_index_list]
        self.axes.plot(buy_points_times, buy_points_prices, 'g.', markersize=3)
        sell_points_times = [times[x] for x in sell_index_list]
        sell_points_prices = [prices[x] for x in sell_index_list]
        self.axes.plot(sell_points_times, sell_points_prices, 'r.', markersize=3)
        self.canvas.draw()

        end_time = time.perf_counter()

        print("plotting done, execution time: {:.3f} s\n".format(end_time - start_time))


    # 创建按钮点击事件
    def open_file_dialog(self):
        # 打开文件选择对话框
        self.file_path = filedialog.askopenfilename()
        print("选择的文件:", self.file_path)
        self.loader = ExcelLoader.myExcelLoader(self.file_path)
        #self.update_strategy_output()
        self.find_best_strategy_config()

    def step_spinbox_cb(self):
        self.step = int(self.step_spinbox_value.get())
        self.update_strategy_output()

    def increase_spinbox_cb(self):
        self.increase_threshold = float(self.increase_spinbox_value.get())
        self.update_strategy_output()

    def capital_spinbox_cb(self):
        self.init_capital = int(self.capital_spinbox_value.get())
        self.update_strategy_output()

    def rolling_window_spinbox_cb(self):
        self.rolling_window = int(self.rolling_window_spinbox_value.get())
        self.update_strategy_output()

    def refresh_canvas(self):
        # 创建并启动线程
        # 如果线程已经在运行，则忽略启动请求
        if self.plot_thread and self.plot_thread.is_alive():
            print("is plotting!")
        else:
            self.plot_thread = threading.Thread(target=self.update_canvas)
            self.plot_thread.start()

    def find_best_strategy_config(self):
        # 创建并启动线程
        # 如果线程已经在运行，则忽略启动请求
        best_return_rate = 0
        best_rolling_window = 0
        for i in range(1, 101):
            self.rolling_window = i
            return_rate = self.update_strategy_output(False)
            if return_rate > best_return_rate:
                best_rolling_window = self.rolling_window
                best_return_rate = return_rate
        self.rolling_window = best_rolling_window
        self.rolling_window_spinbox_value.set(self.rolling_window)
        print("----------------------------------------")
        print("最佳滑窗：{}, 最佳收益率：{:.3f}%".format(best_rolling_window, best_return_rate * 100))
        print("----------------------------------------")
        self.refresh_canvas()

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