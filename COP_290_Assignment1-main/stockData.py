#from pandas_datareader import data as pdr 
import pandas as pd
import yfinance as yf 
#period is of the form 1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max
#interval of data 1m 2m 5m 15m 30m 60m 90m 1h 1d 5d 1wk 1mo 3mo
#1m data only for last 7days less than 1day data for last 60 days
#actions also downloads stock dividends and stock splits events
def getData(symbolName,period,interval):
    symbolName = symbolName + ".NS"
    symbolTicker = yf.Ticker(symbolName)
    symbolHistory  = symbolTicker.history(period=period,interval=interval)
    symbolHistory.reset_index(inplace=True) 
    #print("Columns in df are:")
    #for col in symbolHistory:
        #print("col is:",col)
    #print("df is:")
    #print(symbolHistory)
    symbolHistory['Datetime'] = pd.to_datetime(symbolHistory['Datetime'])
    return symbolHistory
def getDailyData(symbolName):
    return getData(symbolName,'1d','1m')
def get5dayData(symbolName):
    return getData(symbolName,'5d','1m')
def getMonthlyData(symbolName):
    return getData(symbolName,'1mo','1h')
def getYearData(symbolName):
    #hourly data also available for upto 2 years
    return getData(symbolName,'1y','1d')
def getDecadeData(symbolName):
    return getData(symbolName,'10y','1d')
def getMaxData(symbolName):
    #returns all the data available
    return getData(symbolName,'max','1d')
def getInfo(symbolName):
    symbolName = symbolName + ".NS"
    symbolTicker = yf.Ticker(symbolName)
    symbolInfo = symbolTicker.info 
    return symbolInfo