import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import Plot
import ExcelLoader
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

class Logger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, message):
        self.textbox.insert(tk.END, message)

    def flush(self):
        pass

class Application:
    def __init__(self):
        self.app = tk.Tk()
        self.create()

    def create(self):
        self.app.title("Trade")

        # 创建选择文件按钮
        self.button = ttk.Button(self.app, text="选择文件", command=self.open_file_dialog)
        self.button.pack()

        # 创建Frame用以布局
        content_frame = ttk.Frame(self.app)
        content_frame.pack(fill=tk.BOTH, expand=True)

        content_left_frame = ttk.Frame(content_frame)
        content_left_frame.pack(side="left", fill=tk.BOTH, expand=True)

        content_right_frame = ttk.Frame(content_frame)
        content_right_frame.pack(side="right", fill=tk.BOTH, expand=True)

        # 创建step控件
            # 创建Label
        self.step_text_label = tk.Label(content_left_frame, text="Step:")
        self.step_text_label.pack(side="top", anchor='nw')
            # 创建Spinbox
        self.step = 1
        self.step_spinbox_value = tk.IntVar(value = self.step)
        self.step_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=100, increment = 1, textvariable=self.step_spinbox_value, command=self.step_spinbox_cb)
        self.step_spinbox.pack(side="top", anchor='nw')

        # 创建increase_threshold控件
            # 创建Label
        self.increase_text_label = tk.Label(content_left_frame, text="涨幅阈值:")
        self.increase_text_label.pack(side="top", anchor='nw')
            # 创建Spinbox
        self.increase_threshold = 0.01
        self.increase_spinbox_value = tk.DoubleVar(value = self.increase_threshold)
        self.increase_spinbox = ttk.Spinbox(content_left_frame, from_=0, to=1, increment = 0.01, textvariable=self.increase_spinbox_value, command=self.increase_spinbox_cb)
        self.increase_spinbox.pack(side="top", anchor='nw')

        # 创建本金控件
            # 创建Label
        self.capital_text_label = tk.Label(content_left_frame, text="本金:")
        self.capital_text_label.pack(side="top", anchor='nw')
            # 创建Spinbox
        self.init_capital = 20000
        self.capital_spinbox_value = tk.IntVar(value = self.init_capital)
        self.capital_spinbox = ttk.Spinbox(content_left_frame, increment = 5000, textvariable=self.capital_spinbox_value, command=self.capital_spinbox_cb)
        self.capital_spinbox.pack(side="top", anchor='nw')

        # 创建日志区域
            # 创建Label
        log_label = tk.Label(content_left_frame, text="Log:")
        log_label.pack(side="top", anchor='nw')
            # 创建log区域
        log = tk.Text(content_left_frame, width = 30, height = 10)
        log.pack(side="top", anchor='nw', fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 重定向 print 输出到日志文本框
        sys.stdout = Logger(log)

        # 创建矩形区域并在矩形区域上绘制曲线
        self.figure = plt.figure(figsize=(10, 8), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=content_right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self):
        self.app.mainloop()

    def update(self):
        # update strategy outoput
        self.buy_index_list = []
        self.sell_index_list = []
        data = self.loader.get_data()
        self.strategy(data.iloc[:, 1])
        # update canvas
        self.axes.clear()
        self.axes.plot(data.iloc[:, 0], data.iloc[:, 1])
        for i, value in enumerate(self.buy_index_list):
            self.axes.plot(self.buy_index_list[i], data.iloc[:, 1][self.buy_index_list[i]], 'g.')
            self.axes.plot(self.sell_index_list[i], data.iloc[:, 1][self.sell_index_list[i]], 'r.')
        self.canvas.draw()

    # 创建按钮点击事件
    def open_file_dialog(self):
        # 打开文件选择对话框
        self.file_path = filedialog.askopenfilename()
        print("选择的文件:", self.file_path)
        self.loader = ExcelLoader.myExcelLoader(self.file_path)
        self.update()

    def step_spinbox_cb(self):
        self.step = int(self.step_spinbox_value.get())
        self.update()

    def increase_spinbox_cb(self):
        self.increase_threshold = float(self.increase_spinbox_value.get())
        self.update()

    def capital_spinbox_cb(self):
        self.init_capital = int(self.capital_spinbox_value.get())
        self.update()

    def strategy(self, data):
        capital = self.init_capital
        interval = 8 # interval天后卖出
        
        k_dict = {}
        k_filtered_dict = {}

        k_dict = {i : (data[i] - data[i - self.step]) / data[i] for i in range(self.step, len(data))} # 差分斜率
        k_filtered_dict = {i : k_dict[i] for i in k_dict if k_dict[i] > self.increase_threshold} # 符合条件的斜率

        bought_index = []
        for n in range(self.step, len(data)): 
            need_sell = False
            if (n - interval) > 0 and (n - interval) in bought_index:
                need_sell = True
            if need_sell:
                capital += data[n]

            need_buy = False
            if (n + interval) < len(data) and n in k_filtered_dict:
                need_buy = True
            if need_buy:
                if capital - data[n] > 0:
                    capital -= data[n]
                    bought_index.append(n)

            print("第{}天，涨幅：{:.4f}，本金：{:.2f}，{} {}".format(n, k_dict[n], capital, "卖出" if need_sell else " ", "买入" if need_buy else ""))

        print("净收入：", capital - self.init_capital)
        
        self.buy_index_list = bought_index
        self.sell_index_list = [x + interval for x in bought_index]
