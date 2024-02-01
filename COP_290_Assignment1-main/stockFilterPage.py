import math 
from flask import Flask, render_template, request, redirect, url_for, flash, session
from filterStocks import allIndustriesList,companies_to_remove,initStockInfo,perform_filtering
import pandas as pd
import graphPage
inf = math.inf
##All variables corresponding to dataframe filtering
all_stocks_df = initStockInfo()
sort_state= {
    'Symbol' : 0,
    'Industry'  :0 ,
    'Sector'  :0 ,
    'Prev. Close'  :0 ,
    'Open'  :0 ,
    'Low'  :0 ,
    'High'  :0 ,
    'Price'  :0 ,
    'Volume'  :0 ,
    'PE'  :0 ,
    'Market Cap(in Cr)'  :0 ,
}
filter_lims = {
    'vol' : [0 , inf] ,
    'pe_rat' : [0 ,  inf] ,
    'marketCap' : [0,inf] ,
    'price' : [0,inf]  
}
stocks_in_history = []
stocks_in_fav = []
stocks_in_history_symbols=[]
stocks_in_fav_symbols=[]
Industries_filter = ['Specialty Chemicals' , 'Textile Manufacturing' , 'Auto Parts' , 'Drug Manufacturers—Specialty & Generic' , 'Engineering & Construction' , 'Steel' , 'Specialty Industrial Machinery' , 'Information Technology Services' , 'Capital Markets' , 'Credit Services' , 'Others' , 'All']
filtered_df = pd.DataFrame()
filtered_df_columns = []
checked_filter_boxes = ['No' for i in range(0,12)]

def sort_page():
    return render_template('sort.html' , stockList = graphPage.stockList ,filtered_df = filtered_df ,
            filtered_df_columns = filtered_df_columns , checked_filter_boxes=checked_filter_boxes , 
            Industries_filter=Industries_filter ,filter_lims=filter_lims)

def storehist() :
    if 'user_id' in session: 
        user_id = session['user_id']
        user = User.query.get(user_id)
        db.session.query(Stock_History).delete()
        stocks_viewed = list(graphPage.getCurGraphSelection().keys())
        for stock_name in stocks_viewed :
            view_history = Stock_History(stock_name=stock_name ,viewer=user)
            db.session.add(view_history)
        db.session.commit()
    return (redirect(url_for('dashboard')))

def set_to_fav() :
    if 'user_id' in session :
        global stocks_in_fav
        global stocks_in_fav_symbols
        user_id = session['user_id']
        user = User.query.get(user_id)
        db.session.query(Favourites_History).delete()
        stocks_viewed = list(graphPage.getCurGraphSelection().keys())
        for fav_name in stocks_viewed :
            fav_stock = Favourites_History(fav_name=fav_name,fav_user=user)
            db.session.add(fav_stock)
        db.session.commit()
        username = session['username']
        user = User.query.filter_by(username=username).first()
        stocks_in_fav = user.favourites_history
        for x in stocks_in_fav :
            stocks_in_fav_symbols.append(x.fav_name)
    return(redirect(url_for('dashboard')))

def process_filters() :
    global filter_lims , checked_filter_boxes
    global filtered_df,filtered_df_columns

    l_lims = request.form.getlist('l_lim[]')
    m_lims = request.form.getlist('m_lim[]')
    list_check_status = request.form.getlist('checked_filter_boxes[]')
    list_check_status = [int(x) for x in list_check_status]
    for i in range(0,12) :
        if i in list_check_status :
            checked_filter_boxes[i] = 'yes'
        else :
            checked_filter_boxes[i] = 'no'
    
    i = 0 
    for x in filter_lims :
        if l_lims[i] != '' :
            filter_lims[x][0] = float(l_lims[i])
        else :
            filter_lims[x][0] = 0
        if m_lims[i] != '' :
            filter_lims[x][1] = float(m_lims[i])
        else :
            filter_lims[x][1] = inf
        i+=1 
    (filtered_df,filtered_df_columns)  = perform_filtering(all_stocks_df,filter_lims,checked_filter_boxes,Industries_filter)
    return(redirect(url_for('sort_page')))

def sort_filters() :
    global sort_state  , filtered_df
    to_change = request.form.get('sort')
    sort_state[to_change] = (sort_state[to_change]+1)%3
    if sort_state[to_change] == 1 :
        filtered_df =  filtered_df.sort_values(by=to_change)
    elif sort_state[to_change] == 2 :
        filtered_df = filtered_df.sort_values(by=to_change , ascending=False)
    else :
        filtered_df = filtered_df.sort_values(by='Industry')
    return (redirect(url_for('sort_page')))

def setStockInHistory(curList):
    global stocks_in_history
    stocks_in_history = curList
def getStockInHistory():
    return stocks_in_history
def getStockInHistorySymbol():
    return stocks_in_history_symbols
def getStocksInFavSymbols():
    return stocks_in_fav_symbols
def setStockInFav(curList):
    global stocks_in_fav
    stocks_in_fav = curList
def getStockInFav():
    return stocks_in_fav
def addStockSymbolInHistory(elm):
    stocks_in_history_symbols.append(elm)
def addStockSymbolInFav(elm):
    stocks_in_fav_symbols.append(elm)