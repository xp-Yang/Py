import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
import Canvas
import threading
import sys
import backtesting as bt
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

class Application:
    def __init__(self):
        self.plot_thread = None
        bt.result = ()
        bt.buy_slope_span = 3
        bt.buy_slope = 0.003
        bt.rolling_window = 20
        bt.init_capital = 10000000

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
        self.step_spinbox_value = tk.IntVar(value = bt.buy_slope_span)
        step_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=100, increment = 1, textvariable=self.step_spinbox_value, command=self.update_strategy_config)
        step_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建increase_threshold控件
            # 创建Label
        increase_text_label = tk.Label(content_left_frame, text="涨幅阈值:")
        increase_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.increase_spinbox_value = tk.DoubleVar(value = bt.buy_slope)
        increase_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=1, increment = 0.001, textvariable=self.increase_spinbox_value, command=self.update_strategy_config)
        increase_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建ma滑动窗口slider控件
                    # 创建Label
        rolling_window_text_label = tk.Label(content_left_frame, text="MA滑动窗口:")
        rolling_window_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.rolling_window_spinbox_value = tk.IntVar(value=bt.rolling_window)
        rolling_window_spinbox = ttk.Spinbox(content_left_frame, from_=1, to=999, increment = 1, textvariable=self.rolling_window_spinbox_value, command=self.update_strategy_config)
        rolling_window_spinbox.pack(side="top", anchor='nw', fill='x', padx=10)

        # 创建本金控件
            # 创建Label
        capital_text_label = tk.Label(content_left_frame, text="本金:")
        capital_text_label.pack(side="top", anchor='nw', padx=10)
            # 创建Spinbox
        self.capital_spinbox_value = tk.IntVar(value = bt.init_capital)
        capital_spinbox = ttk.Spinbox(content_left_frame, increment = 5000, textvariable=self.capital_spinbox_value, command=self.update_strategy_config)
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

    def update_strategy_config(self, refresh_cvs=True):
        bt.buy_slope_span = int(self.step_spinbox_value.get())
        bt.buy_slope = float(self.increase_spinbox_value.get())
        bt.init_capital = int(self.capital_spinbox_value.get())
        bt.rolling_window = int(self.rolling_window_spinbox_value.get())

        prices = self.loader.get_column(1)
        return_rate = bt.execute_strategy(prices, 'SMA')

        if refresh_cvs:
            self.refresh_canvas()

        return return_rate

    def update_canvas(self):
        #times = self.loader.get_column(0)
        prices = self.loader.get_column(1)
        times = range(len(prices))

        if len(bt.result) == 0:
            return

        buy_index_list = bt.result[1]
        sell_index_list = bt.result[2]
        ma_prices = bt.result[4] if len(bt.result) >=5 else prices

        self.canvas.clear()
        self.canvas.draw_curve(times, prices, '-')
        self.canvas.draw_curve(times, ma_prices, '--')
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

    def refresh_canvas(self):
        # 创建并启动线程
        # 如果线程已经在运行，则忽略启动请求
        if self.plot_thread and self.plot_thread.is_alive():
            print("is plotting!")
        else:
            self.plot_thread = threading.Thread(target=self.update_canvas)
            self.plot_thread.start()

    def find_best_strategy_config(self):
        # TODO 创建新线程
        best_return_rate = 0
        best_rolling_window = 0
        for i in range(1, 101):
            self.rolling_window_spinbox_value.set(i)
            return_rate = self.update_strategy_config(False)
            if return_rate > best_return_rate:
                best_rolling_window = bt.rolling_window
                best_return_rate = return_rate

        self.rolling_window_spinbox_value.set(best_rolling_window)
        bt.rolling_window = best_rolling_window
        
        print("----------------------------------------")
        print("最佳滑窗：{}, 最佳收益率：{:.3f}%".format(best_rolling_window, best_return_rate * 100))
        print("----------------------------------------")
        self.update_strategy_config()

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