import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 创建主界面
root = tk.Tk()

# 设置窗口标题
root.title("主界面")

# 创建按钮点击事件
def open_file_dialog():
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename()
    print("选择的文件:", file_path)

# 创建按钮
button = tk.Button(root, text="选择文件", command=open_file_dialog)
button.pack()

# 创建矩形区域
figure = plt.figure(figsize=(5, 4), dpi=100)
axes = figure.add_subplot(111)
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]
axes.plot(x, y)

# 在矩形区域上绘制曲线
canvas = FigureCanvasTkAgg(figure, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# 运行主界面
root.mainloop()