import Plot
import ExcelLoader

#TODO 从gui输入excel文件
loader = ExcelLoader.myExcelLoader('AWP.xlsx')
loader.get_data()

plot = Plot.myPlot(loader.get_data())
plot.draw()



#TODO
#硬编码回测策略
#

#计算移动均线

#输出回测结果