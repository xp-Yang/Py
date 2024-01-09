import pandas as pd

# 使用 pandas 读取 Excel 文件
class myExcelLoader:
    def __init__(self, file_str):
        self._data = pd.read_excel(file_str)
    
    def get_data(self):
        return self._data