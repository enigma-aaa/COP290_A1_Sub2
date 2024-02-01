#from pandas_datareader import data as pdr 
import pandas as pd
import yfinance as yf 
import stockInfoEff
#period is of the form 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max
#interval of data 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo
#1m data only for last 7days less than 1day data for last 60 days
#actions also downloads stock dividends and stock splits events
#assumes without .NS

#index names have counter intuitive symbols which do not
#follow the .NS convention hence we use the following dict
indexNameSymbols = {
    'NIFTY 50' : "^NSEI",
    'NIFTY NEXT 50':"^NSMIDCP",
    'NIFTY 100':"^CNX100",
    'NIFTY 200':"^CNX200",
    'NIFTY 500':"^CRSLDX",
    'NIFTY MIDCAP 50':"^NSEMDCP50",
    'NIFTY MIDCAP 100':"NIFTY_MIDCAP_100.NS",
    'NIFTY SMALLCAP 100':"^CNXSC",
    'INDIA VIX':"^INDIAVIX",
    'NIFTY MIDCAP 150': "NIFTYMIDCAP150.NS",
    'NIFTY BANK': '^NSEBANK',
    'NIFTY IT': '^CNXIT'
}
def stockIsValid(symbolName):
    if stockInfoEff.symbolInNSElist(symbolName):
        print("symbolName:",symbolName,"is valid")
        return True 
    if symbolName in indexNameSymbols:
        return True
    curDf= None
    try:
        symbolName = symbolName + ".NS"
        curDf = yf.Ticker(symbolName).history(period='1d',interval='1m')
    except e:
        print("symbolName",symbolName , "is invalid")
        return False
    if not curDf.empty:
        return True
    return False
def getData(symbolName,period,interval):
    if symbolName in indexNameSymbols:
        symbolName = indexNameSymbols[symbolName]
    else:
        symbolName = symbolName + ".NS"
    try:
        symbolTicker = yf.Ticker(symbolName)
        symbolHistory  = symbolTicker.history(period=period,interval=interval)
        symbolHistory.reset_index(inplace=True) 
    except e:
        print("Error with symbolName:",symbolName)
        print(e)
    # print("called with interval =",interval)
    # print("Columns in df are:")
    # for col in symbolHistory:
        # print("col is:",col)
    # print("df is:")
    # print(symbolHistory)

    if interval == '1d' :
        symbolHistory['Date'] = pd.to_datetime(symbolHistory['Date'])
        symbolHistory.rename(columns={'Date' : 'Datetime'} ,inplace=True)
    else :
        symbolHistory['Datetime'] = pd.to_datetime(symbolHistory['Datetime'])
    return symbolHistory
def getDailyData(symbolName):
    return getData(symbolName,'1d','1m')
def getWeekData(symbolName):
    return getData(symbolName,'7d','1m')
def getMonthlyData(symbolName):
    return getData(symbolName,'1mo','1h')
def getYearData(symbolName):
    #hourly data also available for upto 2 years
    return getData(symbolName,'1y','1d')
def get5Data(symbolName):
    return getData(symbolName,'5y','1d')
def getMaxData(symbolName):
    #returns all the data available
    return getData(symbolName,'max','1d')
def getInfo(symbolName):
    symbolName = symbolName + ".NS"
    symbolTicker = yf.Ticker(symbolName)
    symbolInfo = symbolTicker.info
    # print(symbolInfo) 
    # print(list(symbolInfo.keys()))
    return symbolInfo
def controltime(symbolName,duration_req) :
    if(duration_req == '1_day') :
        return getDailyData(symbolName)
    elif(duration_req == '1_week') :
        return getWeekData(symbolName)
    elif(duration_req == '1_month') :
        return getMonthlyData(symbolName)
    elif(duration_req == '1_year') :
        return getYearData(symbolName)
    elif(duration_req == '5_year') :
        return get5Data(symbolName)
    elif(duration_req == 'All') :
        return getMaxData(symbolName)
    # return getDailyData(symbolName)
def getAllInfos():
    nseStockList = pd.read_csv('./Data_folder/NSE_Stock_List.csv')
    sampleDict = getInfo('SBIN')
    arrayDict = {}
    columns = []
    for key in sampleDict:
        arrayDict[key] = []
        columns.append(key)
    i = 0
    for symbol in nseStockList['Symbol']:
        try:
            curDict = getInfo(symbol)
        except e:
            continue
        for key in curDict:
            if key in arrayDict:
                arrayDict[key].append(curDict[key])
        i += 1
        print(i)
    totalData = []
    for key in sampleDict:
        totalData.append(arrayDict[key])
    df = pd.DataFrame(totalData,columns=columns)
    df.to_pickle('./Data_folder/allInfo.pkl')