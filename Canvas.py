import matplotlib
import matplotlib.style as plstyle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ExcelLoader
import time

plstyle.use('fast')
matplotlib.use('Agg')
plt.ioff()

class myCanvas:
    def __init__(self, tk_master):
        self.__figure = plt.figure(figsize=(8, 6), dpi=100)
        self.__axes = self.__figure.add_subplot(111)
        self.tkCanvas = FigureCanvasTkAgg(self.__figure, master=tk_master)

    def get(self):
        return self.tkCanvas

    def draw_points(self, x_list, y_list, style='g.'):
        self.__axes.plot(x_list, y_list, style, markersize=3)
        self.tkCanvas.draw()

    def draw_curve(self, x_list, y_list, lines_style='-'):
        self.__axes.set_xticks([])
        self.__axes.set_xticklabels([])
        self.__axes.plot(x_list, y_list, linestyle=lines_style)
        self.tkCanvas.draw()

    def clear(self):
        self.__axes.clear()
        self.tkCanvas.draw()




    def __draw(self, data):
        plt.plot(data.iloc[:, 0], data.iloc[:, 1])
        plt.xticks([])
        plt.gca().set_xticklabels([])
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('')
        plt.show()

if __name__ == "__main__":
    start_time = time.perf_counter()
    loader = ExcelLoader.myExcelLoader('resource/蝴蝶刀_渐变之色 (崭新出厂)BUFF近1年-总览.xlsx')
    data = loader.get_data_frame()
    myCanvas(None).__draw(data)
    end_time = time.perf_counter()
    print("plotting done, execution time: {:.3f} s".format(end_time - start_time))