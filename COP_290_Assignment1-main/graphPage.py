import math 
import graph
import stockData
import colorGenerator
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_file
import pandas as pd
#list of all variables corresponding to graph state
#list of stocks currently displayed on the left side of the website
stockList = ["SBIN","ONGC","TATASTEEL"]
curStockInfo = {}
mode = 'Mode1'
selected_duration = '1_day'
currentlySelected = ""
inf = math.inf
df_temp = pd.read_csv('./Data_folder/NSE_Stock_List.csv')
stocks_symbols_for_suggestion = df_temp['Symbol'].tolist()
dataFrameDict = {}
curGraphSelection = {
    'SBIN':{
        'graphDuration':'1_day' ,
        'color':{
            "HIGH":colorGenerator.genColor(),
            "LOW":colorGenerator.genColor(),
            "OPEN":colorGenerator.genColor(),
            "CLOSE":colorGenerator.genColor(),
            "COMBINED":colorGenerator.genColor()
        },
        'graphCont':{
            "HIGH" : True ,
            "LOW" : False,
            "OPEN" : False ,
            "CLOSE" : False ,
            "COMBINED" : False
        }
    },
    'ONGC':{
        'graphDuration':'1_day',
        'color':{
            "HIGH":colorGenerator.genColor(),
            "LOW":colorGenerator.genColor(),
            "OPEN":colorGenerator.genColor(),
            "CLOSE":colorGenerator.genColor(),
            "COMBINED":colorGenerator.genColor()
        },
        'graphCont':{
            "HIGH":False,
            "LOW":False,
            "OPEN":False,
            "CLOSE":False,
            "COMBINED":False
        }
    },
    'TATASTEEL':{
        'graphDuration':'1_day',
        'color':{
            "HIGH":colorGenerator.genColor(),
            "LOW":colorGenerator.genColor(),
            "OPEN":colorGenerator.genColor(),
            "CLOSE":colorGenerator.genColor(),
            "COMBINED":colorGenerator.genColor()
        },
        'graphCont':{
            "HIGH":False,
            "LOW":False,
            "OPEN":False,
            "CLOSE":False,
            "COMBINED":False
        }
    }
}
#helper function which looks at all the stock names in our curGraph selection dictionary and 
#is supposed to get the data corresponding to the data frames and all the time frames
#like daily monthly and store it in the dataFrameDict which is refrenced in the render_tempalte() function
def getStockDataFrameInfo():
    dataFrameDict = {}
    for symbolName in curGraphSelection:
        curDict = curGraphSelection[symbolName]
        duration_req = curDict['graphDuration']
        df = stockData.controltime(symbolName,duration_req)
        dataFrameDict[symbolName] = df
    return dataFrameDict

#lloks at the requested data to draw in the data frmae dictionary and draws 
#the corresponding graphs of the symbolName such as HIGH,LOW,COMBINED
#requested for SBIN then draws that



#this function takes in curStockInfo and replaces all missing values with N/A
def padCurStockInfo(curStockInfo):
    keys = ['longName','open','previousClose','currentPrice','dayHigh'
            ,'dayLow','fiftyTwoWeekLow','fiftyTwoWeekHigh','trailingPE',
            'forwardPE','marketCap','forwardEps','trailingEps','bookValue',
            'dividendYield','returnOnEquity']
    for key in keys:
        if key not in curStockInfo:
            curStockInfo[key] = 'N/A'
def dashboard(session,stocks_in_history):
    global dataFrameDict
    if 'user_id' in session:
        try:
            dataFrameDict = getStockDataFrameInfo()
        except Exception as e:
            raise e
        script1,div1 = graph.drawCurGraphAndTable(dataFrameDict,curGraphSelection)
        padCurStockInfo(curStockInfo)
        return render_template('welcome.html', username=session['username'],
        stockList=stockList,script=script1,div=div1,curStockInfo=curStockInfo , 
        curGraphSelection=curGraphSelection ,
        selected_duration = selected_duration,dataFrameDict=dataFrameDict , 
        currentlySelected = currentlySelected , mode=mode ,stocks_symbols_for_suggestion=stocks_symbols_for_suggestion)
    else:
        return redirect(url_for('index'))


def updateList():
    stockName = request.form['search_bar']
    if stockName not in stockList:
        if(not stockData.stockIsValid(stockName)):
            flash(stockName+ " is invalid please check")
            return redirect(url_for('dashboard'))
        stockList.append(stockName)
        curGraphSelection[stockName] = {
        'graphDuration':'1_day',
        'color':{
            "HIGH":colorGenerator.genColor(),
            "LOW":colorGenerator.genColor(),
            "OPEN":colorGenerator.genColor(),
            "CLOSE":colorGenerator.genColor(),
            "COMBINED":colorGenerator.genColor()
        },
        'graphCont':{
                "HIGH":False,
                "LOW":False,
                "OPEN":False,
                "CLOSE":False,
                "COMBINED":False
            }
        }
    return redirect(url_for('dashboard'))
 
#select stock function adds the stock symbol currently selected to the dictionary of graphs we want to draw
def stockselected ():
    global curStockInfo
    global currentlySelected
    stockName = request.form.get('selectedStock')
    #in our current assumption when we clicked a selected stock we deselect it and 
    #remove it fromt the list of graphs we are drawing
    if stockName.endswith('Cross'):
        stockName = stockName[:-5]
        if currentlySelected == stockName:
            currentlySelected = ''
        stockList.remove(stockName)
        del curGraphSelection[stockName]
    else:
        if stockName != currentlySelected:
            currentlySelected = stockName
            curStockInfo = stockData.getInfo(stockName)
    return redirect(url_for('dashboard'))

#havent understood this one yet have to understand this one properly
def process_duration_fun() :
    global selected_duration
    initial = 0
    selected_duration = request.form.get('duration')
    for x in curGraphSelection :
        curGraphSelection[x]['graphDuration'] = selected_duration
    return redirect(url_for('dashboard'))

def process_graph_options() :
    global curGraphSelection
    list_of_graphs = request.form.getlist("graph_options[]")
    graphTypeDict = curGraphSelection[currentlySelected]['graphCont']
    for key in graphTypeDict:
        graphTypeDict[key] = False
    for elm in list_of_graphs:
        graphTypeDict[elm] = True
    return redirect(url_for('dashboard'))

def closeStock() :
    to_close = request.form.get('closedStock')
    global curGraphSelection
    global stockList
    del curGraphSelection[to_close]
    stockList.remove(to_close)
    return redirect(url_for('dashboard'))

def process_mode_change() :
    global mode
    mode = request.form.get('graph-mode')
    return redirect(url_for('dashboard'))

def getStockList():
    return stockList

def downloadTable():
    symbolName = request.form.get('DownloadButton')
    tableDataDuration = curGraphSelection[symbolName]['graphDuration']
    folderName = "./TableData/"
    fileName = symbolName+"_"+tableDataDuration+".csv"
    relPath = folderName + fileName
    curDf = dataFrameDict[symbolName]
    curDf.to_csv(relPath)
    #uploads = os.path.join(current_app.root_path,app.config['UPLOAD_FOLDER'])
    return send_file(relPath,as_attachment=True)

def getCurGraphSelection():
    return curGraphSelection