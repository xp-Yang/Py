import matplotlib.pyplot as plt

class myPlot:
    def __init__(self, data):
        self._data = data
    def draw(self):
        plt.plot(self._data.iloc[:, 0], self._data.iloc[:, 1])
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('AWP')
        plt.show()
