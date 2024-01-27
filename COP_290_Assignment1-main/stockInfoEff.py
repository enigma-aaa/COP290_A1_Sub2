import pandas as pd 
import stockData
from concurrent.futures import ThreadPoolExecutor
df = pd.read_csv('./Data_folder/NSE_Stock_List.csv')
symbols = df['Symbol']

columnNames = ['industry','industryKey','sector'
,'sectorKey','sectorDisp','previousClose','open',
'dayLow','dayHigh','previousClose','currentPrice','volume'
,'forawrdPE','trailingPE','averageVolume']
ColumnArr = [ [] for i in range(len(arr))]
def get_stats(symbolName):
    info = stockData.getInfo(symbolName)
    for i in range(len(arr)):
        elm = arr[i]
        ColumnArr[i].append(info[elm])

with ThreadPoolExecutor() as executor:
    executor.map(get_stats,ticker_list)

df = pd.DataFrame(data = ColumnArr,index = symbols,columns = columnNames)
df.to_pickle('./Data_folder/AllStocks.pkl')