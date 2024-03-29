import pandas as pd 
import stockData
import time
from concurrent.futures import ThreadPoolExecutor
df = pd.read_csv('./Data_folder/NSE_Stock_List.csv')
symbols = df['Symbol']
columnNames = ['industryKey','industry','sector','previousClose','open',
'dayLow','dayHigh','previousClose','currentPrice','volume'
,'trailingPE', 'marketCap']
defaultVal = ['','','',0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
ColumnArr = [ [] for i in range(len(columnNames))]
def symbolInNSElist(symbolName):
    if symbolName in symbols:
        return True 
    return False
def get_stats(symbolName):
    info = stockData.getInfo(symbolName)
    for i in range(len(columnNames)):
        elm = columnNames[i]
        if elm in info:
            ColumnArr[i].append(info[elm])
        else:
            ColumnArr[i].append(defaultVal[i])
def getAllInfos():
    startTime = time.time()
    #for symbolName in symbols:
    #    get_stats(symbolName)
    with ThreadPoolExecutor() as executor:
        executor.map(get_stats,symbols)
    endTime = time.time()

    dataFrameDict = {}
    for i in range(len(columnNames)):
        dataFrameDict[columnNames[i]] = ColumnArr[i]
    df = pd.DataFrame(dataFrameDict,index = symbols)
    #df = pd.DataFrame(data = ColumnArr,index = symbols,columns = columnNames)
    df.to_pickle('./Data_folder/AllStocks.pkl')
    df.to_csv('./Data_folder/AllStocksTemp.csv')