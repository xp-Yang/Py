import pandas as pd

# 使用 pandas 读取 Excel 文件
class myExcelLoader:
    def __init__(self, file_str):
        df = pd.read_excel(file_str, header=7)
        df['Date'] = pd.to_datetime(df.iloc[:, 0])
        df.set_index('Date', inplace=True)
        df_daily = df.resample('D').first()
        #df_daily = df_daily.drop(df_daily.columns[0], axis=1)

        self._excel = df
        self._excel_daily = df_daily
        #print(df_daily)
        #print(df_daily.iloc[:,0])

    # daily excel
    def get_excel(self):
        return self._excel_daily
    
    # original excel
    def get_original_excel(self):
        return self._excel
    
if __name__ == "__main__":
    #__loader = myExcelLoader('resource/M9 刺刀-日线.xlsx')
    __loader = myExcelLoader('resource/蝴蝶刀_渐变之色 (崭新出厂)BUFF近1年-总览.xlsx')