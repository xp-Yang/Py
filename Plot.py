import matplotlib.pyplot as plt
import ExcelLoader
import time

class myPlot:
    def __init__(self, data):
        self._data = data
    def draw(self):
        plt.plot(self._data.iloc[:, 0], self._data.iloc[:, 1])
        plt.xticks([])
        plt.gca().set_xticklabels([])
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('')
        plt.show()

start_time = time.perf_counter()
loader = ExcelLoader.myExcelLoader('resource/蝴蝶刀_渐变之色 (崭新出厂)BUFF近1年-总览.xlsx')
data = loader.get_data()
my_plot = myPlot(data)
my_plot.draw()
end_time = time.perf_counter()
print("plotting done, execution time: {:.3f} s".format(end_time - start_time))