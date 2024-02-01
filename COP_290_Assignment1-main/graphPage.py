import graph
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
@app.route('/dashboard') 
def dashboard():
    global dataFrameDict
    if 'user_id' in session:
        try:
            dataFrameDict = getStockDataFrameInfo()
        except Exception as e:
            # print("curGraphSelection is:")
            # print(curGraphSelection)
            raise e
        script1,div1 = graph.drawCurGraphAndTable(dataFrameDict,curGraphSelection)
        padCurStockInfo(curStockInfo)
        print("here are stocks in history")
        for stocks in stocks_in_history:
            print(stocks.stock_name)
        return render_template('welcome.html', username=session['username'],
        stockList=stockList,script=script1,div=div1,curStockInfo=curStockInfo , 
        curGraphSelection=curGraphSelection ,
        selected_duration = selected_duration,dataFrameDict=dataFrameDict , 
        currentlySelected = currentlySelected , mode=mode)
    else:
        return redirect(url_for('index'))