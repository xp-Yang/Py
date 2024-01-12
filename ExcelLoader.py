import pandas as pd

# 使用 pandas 读取 Excel 文件
class myExcelLoader:
    def __init__(self, file_str):
        # 另一种方式
        #df = pd.read_excel(file_str, header=6, index_col=0, parse_dates=True)
        #df_daily = df.resample('D').first()
    
        df = pd.read_excel(file_str, header=6)
        df['Date'] = pd.to_datetime(df.iloc[:, 0])
        df.set_index('Date', inplace=True)
        df_daily = df.resample('D').first()
        df_daily.set_index(pd.RangeIndex(start=0, stop=df_daily.shape[0], step=1), inplace=True)

        self._excel = df
        self._excel_daily = df_daily

    # daily
    def get_data_frame(self):
        return self._excel_daily
    
    # original
    def get_original_data_frame(self):
        return self._excel
    
    def get_column(self, index):
        return self.get_data_frame().iloc[:, index]
    
if __name__ == "__main__":
    #__loader = myExcelLoader('resource/M9 刺刀-日线.xlsx')
    __loader = myExcelLoader('resource/蝴蝶刀_渐变之色 (崭新出厂)BUFF近1年-总览.xlsx')
    #__loader = myExcelLoader('resource/【2022年里约热内卢锦标赛炙热沙城 II 纪念包】BUFF近1年-总览.xlsx')
    
    print(__loader.get_data_frame())
    print(__loader.get_column(1))