import tkinter as tk
from tkinter import filedialog
import Plot
import ExcelLoader
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Application:
    def __init__(self):
        self.app = tk.Tk()
        self.create()

    def create(self):
        self.app.title("Trade")
        # 创建按钮
        self.button = tk.Button(self.app, text="选择文件", command=self.open_file_dialog)
        self.button.pack()
        # 创建矩形区域并在矩形区域上绘制曲线
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.app)
        self.canvas.get_tk_widget().pack()

    # 创建按钮点击事件
    def open_file_dialog(self):
        # 打开文件选择对话框
        self.file_path = filedialog.askopenfilename()
        print("选择的文件:", self.file_path)
        self.loader = ExcelLoader.myExcelLoader(self.file_path)
        self.draw_canvas()

    def run(self):
        self.app.mainloop()
        self.draw_canvas()

    def draw_canvas(self):
        data = self.loader.get_data()
        self.axes.clear()
        self.axes.plot(data.iloc[:, 0], data.iloc[:, 1])
        self.canvas.draw()