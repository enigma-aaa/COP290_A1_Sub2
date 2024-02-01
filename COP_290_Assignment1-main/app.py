from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import RangeTool,PanTool,WheelZoomTool,HoverTool,BoxZoomTool
#have to check TapTool
from bokeh.models import TapTool,WheelPanTool,SaveTool,ZoomInTool,ZoomOutTool,ResetTool
from bokeh.layouts import column,layout,gridplot
import pandas as pd
import stockData
import numpy as np
# import sys
import math
import os
import colorGenerator
# inf = sys.maxsize
inf = math.inf
excel_file_path = 'MCAP31122023.xlsx'
pickel_file_path = 'Data_folder/AllStocks.pkl'
# all_stocks_df = pd.read_excel(excel_file_path)
all_stocks_df = pd.read_pickle(pickel_file_path)
all_stocks_df['marketCap'] = all_stocks_df['marketCap']/10000000
all_stocks_df['marketCap'] =all_stocks_df['marketCap'].round(2)
all_stocks_df['new_col'] = np.where(all_stocks_df['industryKey'] != '' , all_stocks_df['industryKey'] , all_stocks_df['industry'])
all_stocks_df = all_stocks_df.drop(columns=['industryKey' , 'industry'])
all_stocks_df = all_stocks_df.rename(columns={'new_col' : 'industryKey'})
all_stocks_df = all_stocks_df[all_stocks_df.eq(0).sum(axis=1) <= 4]
all_stocks_df['industryKey'] = all_stocks_df['industryKey'].replace({'specialty-chemicals':'Specialty Chemicals' , 'auto-parts' : 'Auto Parts' , 'drug-manufacturers-specialty-generic':'Drug Manufacturers—Specialty & Generic' , 
                                      'specialty-industrial-machinery':'Specialty Industrial Machinery' ,'steel' : 'Steel' ,'information-technology-services' :'Information Technology Services' , 
                                      'credit-services' :'Credit Services' ,'packaged-foods' :'Packaged Foods' , 'real-estate-development' :'Real Estate—Development' , 'agricultural-inputs' :'Agricultural Inputs' ,
                                        'furnishings-fixtures-appliances' :'Furnishings, Fixtures & Appliances' ,'textile-manufacturing' :'Textile Manufacturing' , 'asset-management' : 'Asset Management',
                                        'chemicals' : 'Chemicals' , 'auto-manufacturers' : 'Auto Manufacturers' , 'auto-truck-dealerships' : 'Auto & Truck Dealerships' ,'farm-heavy-construction-machinery' : 'Farm & Heavy Construction Machinery',
                                        'internet-content-information' : 'Internet Content & Information' ,'engineering-construction' : 'Engineering & Construction' ,'food-distribution' : 'Food Distribution' ,
                                        'entertainment' : 'Entertainment' ,   'tools-accessories' : 'Tools & Accesories','capital-markets' : 'Capital Markets' , 'banks-regional' :'Banks—Regional' ,
                                         'real-estate-diversified' : 'Real Estate—Diversified', 'building-products-equipment' : 'Building Products & Equipment' , 'building-materials' : 'Building Materials' ,
                                         'packaging-containers' : 'Packaging & Containers' ,'electrical-equipment-parts' : 'Electrical Equipment & Parts' ,'apparel-manufacturing' : 'Apparel Manufacturing' , 'apparel-retail':'Apparel Retail' ,
                                         'paper-paper-products' : 'Paper & Paper Products' , 'drug-manufacturers-general' : 'Drug Manufacturers—General','farm-products':'Farm Products','software-application' : 'Software—Application' , 'software-infrastructure':'Software—Infrastructure',
                                         'other-industrial-metals-mining':'Other Industrial Metals & Mining','metal-fabrication':'Metal Fabrication' ,'confectioners':'Confectioners','integrated-freight-logistics':'Integrated Freight & Logistics',
                                         'lodging':'Lodging','luxury-goods':'Luxury Goods','education-training-services':'Education & Training Services','financial-conglomerates':'Financial Conglomerates','conglomerates':'Conglomerates',
                                         'business-equipment-supplies':'Business Equipment & Supplies',  'specialty-business-services':'Specialty Business Services','communication-equipment':'Communication Equipment','medical-instruments-supplies':'Medical Instruments & Supplies' , 'medical-care-facilities':'Medical Care Facilities',
                                         'publishing':'Publishing','household-personal-products':'Household & Personal Products','oil-gas-refining-marketing':'Oil & Gas Refining & Marketing','footwear-accessories':'Footwear & Accessories','aerospace-defense':'Aerospace & Defense','utilities-independent-power-producers':'Utilities—Independent Power Producers',
                                         'utilities-regulated-gas':'Utilities—Regulated Gas','utilities-renewable':'Utilities—Renewable','utilities-regulated-electric':'Utilities—Regulated Electric','mortgage-finance':'Mortgage Finance','telecom-services':'Telecom Services','biotechnology':'Biotechnology','Tools & Accesories':'Tools & Accessories',
                                         'beverages-wineries-distilleries':'Beverages—Wineries & Distilleries','beverages-brewers':'Beverages—Brewers'})
# pd.set_option('display.max_rows',None)
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
stocks_in_history = []
stocks_in_fav = []
stocks_in_history_symbols=[]
stocks_in_fav_symbols=[]
#companies_to_remove = ['ACL' , 'RAJMET' , 'GEPIL' , 'OSWALGREEN' , 'SOTL' , 'WABAG' , 'AVG' , 'BMETRICS' ,'JINDWORLD' , 'ROHLTD' , 'FMNL' , 'ASTEC' , 'SHRENIK' , 'AILIMITED' , 'AMNPLST' , 'SHIVALIK' , 'SERVOTECH' , 'BANARISUG' , '3PLAND' , 'AARTECH' , 'PLADAINFO' ,'STERTOOLS' , 'SATINDLTD' , 'AGRITECH' , 'INDOBORAX' , 'INOXGREEN']
companies_to_remove = ['ACL' , 'RAJMET' , 'GEPIL' , 'OSWALGREEN' , 'SOTL' , 'WABAG' , 'AVG'  ,'JINDWORLD' , 'ROHLTD' , 'FMNL' , 'ASTEC' , 'SHRENIK', 'AMNPLST' , 'SHIVALIK' , 'SERVOTECH' , 'BANARISUG' , '3PLAND' , 'AARTECH' , 'PLADAINFO' ,'STERTOOLS' , 'SATINDLTD' , 'AGRITECH' , 'INDOBORAX' , 'INOXGREEN']
# print(all_stocks_df['industryKey'].value_counts())
# all_stocks_df = all_stocks_df[all_stocks_df['symbol'] != companies_to_remove]
# print(all_stocks_df)
all_stocks_df = all_stocks_df.drop(companies_to_remove)
# pd.reset_option('display.max_rows')/
# print(all_stocks_df)
registerErrorMsg = ""
allIndustriesList = all_stocks_df['industryKey'].unique().tolist()
checked_filter_boxes = ['No' for i in range(0,12)]

# print('size' , all_stocks_df.shape)
# all_stocks_symbol_list = all_stocks_df['Symbol']
initial = 1
app = Flask(__name__)
#change secret key later
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
mode = 'Mode1'
filtered_df_columns = []
selected_duration = '1_day'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
#list of stocks currently displayed on the left side of the website
stockList = ["SBIN","ONGC","TATASTEEL"]
curStockInfo = {}
#this shouldn't be a list currently as a list this is representing the lost of grpahs currently beong drawn
#this information is implicitly stored in the curGraphSelection anyways if there graphCont dictionary has all 
#false then we don't need to draw it 
#what we want selectedStockList to be like last selected this should only show one selected stock
#we will use htis to decide what information we are showing on the side
selectedStocksList = []
last_selected = 'SBIN'

#keeps track of which stock is selected and only that one is green
currentlySelected = ""
# filter_market_cap = "small"
# filter_avg_vol = "Any"
# filter_pe_rat = "Any"
filter_lims = {
    'vol' : [0 , inf] ,
    'pe_rat' : [0 ,  inf] ,
    'marketCap' : [0,inf] ,
    'price' : [0,inf]  
}

Industries_filter = ['Specialty Chemicals' , 'Textile Manufacturing' , 'Auto Parts' , 'Drug Manufacturers—Specialty & Generic' , 'Engineering & Construction' , 'Steel' , 'Specialty Industrial Machinery' , 'Information Technology Services' , 'Capital Markets' , 'Credit Services' , 'Others' , 'All']
filtered_df = pd.DataFrame()
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

# User Model
class Favourites_History(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    fav_name= db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class Stock_History(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(50),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class User(db.Model):
    #by defualt table name lowercase class name#
    #explicit definiton __tablename__ = #
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    stocks_history = db.relationship('Stock_History',backref='viewer',lazy=True  )
    favourites_history = db.relationship('Favourites_History',backref='fav_user',lazy=True)

# Initialize Database within Application Context

                        

with app.app_context():
    db.create_all()

#for each url diff func defined with decorator below is the root
    

# market_cap_vals = {
#     'Any' : (0, inf) ,
#     'large' : ( 2500000, inf) ,
#     'mid' : ( 850000,2500000 ) ,
#     'small' : (0,850000)
# }

# pe_rat_vals = {
#     'Any' : (0,inf) , 
#     'l5' : (0,5) ,
#     'b_5_10' : (5,10) ,
#     'b_10_20' : (10,20) ,
#     'b_20_50' : (20,50) ,
#     'g50' : (50,inf)
# }

# avg_vol_vals = {
#     'Any' : (0,inf) ,
#     'l1' : (0,100000) ,
#     'b_1_10' : (100000,1000000) ,
#     'g10' : (1000000,inf)
# }
    # for x in all_stocks_symbol_list : 

        # df = all_stocks_df[']


def checkUserAndPasswrodValid(username,password,confirmPass):
    userNameMinLen = 9
    passwordMinLen = 8
    valid = True
    userExist = User.query.filter_by(username=username).first()
    if(len(password) < passwordMinLen):
        flash('Password must be atleast 8 characters')
        valid = False
    if(len(username) < userNameMinLen):
        flash('Username must be atleast 9 characters')
        valid = False
    if userExist:
        flash('Username already exists choose different username')
        valid = False
    if password != confirmPass:
        flash('Password fields do not match please recheck')
        valid = False
    return valid
@app.route('/')
def index():
    return render_template('login.html')
#understand what get and post is
@app.route('/register', methods=['GET', 'POST'])
def register():
    global registerErrorMsg
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmPass = request.form['confirmPass']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  
        valid = checkUserAndPasswrodValid(username,password,confirmPass)
        if not valid:
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('index'))

    return render_template('register.html',registerErrorMsg = registerErrorMsg)

@app.route('/login', methods=['POST'])
def login():
    global stocks_in_history
    global stocks_in_history_symbols
    global stocks_in_fav
    global stocks_in_fav_symbols
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        stocks_in_history = user.stocks_history
        stocks_in_fav = user.favourites_history
        for x in stocks_in_history :
            stocks_in_history_symbols.append(x.stock_name)
        for x in stocks_in_fav :
            stocks_in_fav_symbols.append(x.fav_name)
        # stocks_in_history_symbols = [for x in stocks_history x.stock_name]
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))


def drawOpenGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Open'],legend_label=symbolName+" Open",line_width=2,color = color)
#code for drawing the close prices of the stock available in the dataframe
def drawCloseGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Close'],legend_label=symbolName+" Close",line_width=2,color=color)
#code for drawing the high prices
def drawHighGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['High'],legend_label=symbolName+" High",line_width=2,color=color)
#code for drawing the low prices
def drawLowGraph(symbolName,plot,df,color):
    plot.line(df['Datetime'],df['Low'],legend_label=symbolName+" Low",line_width=2,color=color)
#code for drawing a combined candle stick graph to consisting of 
#high low prices as segments
#the blocks represent opening and closing prices
def drawCombinedGraph(symbolName,plot,df,timeInterval,color):
    #this draws the segemnt from the opening to the closing price
    plot.segment(df.Datetime,df.High,df.Datetime,df.Low,color=color,legend_label=symbolName+" Combined")
    #different plots for open price above close price and 
    #close price above open price
    #boolean arrs to show whether opening price is above or below closing price
    barWidth = timeInterval/2
    priceInc = df.Close > df.Open 
    priceDec = df.Open > df.Close 
    #add legend lable here later perhaps?
    plot.vbar(df.Datetime[priceDec],barWidth,df.Open[priceDec],df.Close[priceDec],color="#eb3c40")
    plot.vbar(df.Datetime[priceInc],barWidth,df.Open[priceInc],df.Close[priceInc],color="#00ff00",
              line_color="00ffff",line_width=2)

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
def drawCurGraphAndTable(dataFrameDict):
    #creating the panTool and wheel zoom tool which is available to 
    #naigate across the graph
    #from bokeh.models import RangeTool,PanTool,WheelZoomTool,HoverTool,BoxZoomTool
    #have to check TapTool
    #from bokeh.models import TapTool,WheelPanTool,SaveTool,ZoomInTool,ZoomOutTool
    hoverTool = HoverTool(
        tooltips = [('date','$x{%F}'),('price','$y{(0.00 a)}')],
        formatters={'$x':'datetime'}
    )
    tools = [PanTool(),WheelZoomTool(),hoverTool,BoxZoomTool(),
            TapTool(),WheelPanTool(),SaveTool(),ZoomInTool(),ZoomOutTool(),ResetTool()]

    #creating the figure in which the graph is actually drawn
    plot = figure(x_axis_label="Date Time",y_axis_label="Price",
                x_axis_type="datetime",toolbar_location="right",
                tools= tools)
    #setting the main graph to stretch in both the x axis direction and y direction to 
    #fill the space alloted
    plot.sizing_mode = "stretch_both"
    
    #creating the mini graph available below the main graph which is
    #used for zooming in and out of the graph
    rangePlot = figure(height=100,x_axis_type="datetime",
                        y_axis_type=None,toolbar_location=None,
                        background_fill_color="#efefef")
    #setting the mini graph to only stretch in the x direction
    rangePlot.sizing_mode = "stretch_width"

    rangeTool = RangeTool(x_range=plot.x_range)
    rangeTool.overlay.fill_color = "navy"
    rangeTool.overlay.fill_alpha = 0.2
    #adding the rangeTool which allows us to zoom in and out of the main graph to the mini graph
    rangePlot.add_tools(rangeTool)
    rangePlot.toolbar.active_multi = 'auto'

    for symbolName in curGraphSelection:
        curDict = curGraphSelection[symbolName]
        duration_req = curDict['graphDuration']

        df = dataFrameDict[symbolName]
        timeInterval = 60*1000 
        #time interval corresponding to one min in miili seconds 
        #this is used to find the width of the bar graph 

        #time period for which graph is drawn
        timePeriod = curDict['graphDuration']
        graphCont = curDict['graphCont']
        colors = curDict['color']
        for elm in graphCont:
            if graphCont[elm] :
                match elm:
                    case 'OPEN':
                        drawOpenGraph(symbolName,plot,df,colors['OPEN'])
                        drawOpenGraph(symbolName,rangePlot,df,colors['OPEN'])
                    case 'CLOSE':
                        drawCloseGraph(symbolName,plot,df,colors['CLOSE'])
                        drawCloseGraph(symbolName,rangePlot,df,colors['CLOSE'])
                    case 'HIGH':
                        drawHighGraph(symbolName,plot,df,colors['HIGH'])
                        drawHighGraph(symbolName,rangePlot,df,colors['HIGH'])
                    case 'LOW':
                        drawLowGraph(symbolName,plot,df,colors['LOW'])
                        drawLowGraph(symbolName,rangePlot,df,colors['LOW'])
                    case 'COMBINED':
                        drawCombinedGraph(symbolName,plot,df,timeInterval,colors['COMBINED'])
                        drawCombinedGraph(symbolName,rangePlot,df,timeInterval,colors['COMBINED'])

    total = column(plot,rangePlot,sizing_mode="stretch_both")
    script,div = components(total)
        
    #modifying div generated by bokeh library so that we can add the styling from our css file
    div = div[:-7] + ' class="GraphDiv" ></div>'
    return (script,div)

def drawStockIndicesGraph():
    indices = ['NIFTY 50','NIFTY NEXT 50','NIFTY BANK','NIFTY IT']
    colors = ['#d04848','#f3b95f','#6895d2','#37b5b6']
    plotArr = []
    hoverTool = HoverTool(
        tooltips = [('date','$x{%F}'),('price','$y{(0.00 a)}')],
        formatters={'$x':'datetime'}
    )

    tools = [PanTool(),WheelZoomTool(),hoverTool,BoxZoomTool(),
            TapTool(),WheelPanTool(),SaveTool(),ZoomInTool(),ZoomOutTool(),ResetTool()]
    for i in range(len(indices)):
        symbolName = indices[i]
        curCol = colors[i]
        curDf = stockData.getDailyData(symbolName)
        print('For symbolName',symbolName)
        print("data frame is:",curDf)
        curPlot = figure(x_axis_label="Date Time",y_axis_label="Open Price",
                x_axis_type="datetime",title=symbolName,tools = tools)
        curPlot.title.align = "center"
        curPlot.title.text_font_size = "20px"
        curPlot.sizing_mode = 'stretch_width'
        drawOpenGraph(symbolName,curPlot,curDf,curCol)
        plotArr.append(curPlot)
    grid = gridplot(plotArr,ncols = 2)
    grid.sizing_mode = 'stretch_width'
    (script,div) = components(grid)
    div = div[:-7] + ' class="StockIndices" ></div>'
    return (script,div)
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
        script1,div1 = drawCurGraphAndTable(dataFrameDict)
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
@app.route('/sort_page')
def sort_page():
    # print('gonna render')
    # print(filtered_df)
    # print(*filtered_df_columns)
    return render_template('sort.html' , stockList = stockList ,filtered_df = filtered_df ,
            filtered_df_columns = filtered_df_columns , checked_filter_boxes=checked_filter_boxes , 
            Industries_filter=Industries_filter ,filter_lims=filter_lims)


# class Favourites_History(db.Model) :
#     id = db.Column(db.Integer, primary_key=True)
#     fav_name= db.Column(db.String(50),nullable=False)
#     user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

# class Stock_History(db.Model) :
#     id = db.Column(db.Integer, primary_key=True)
#     stock_name = db.Column(db.String(50),nullable=False)
#     user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

# class User(db.Model):
#     #by defualt table name lowercase class name#
#     #explicit definiton __tablename__ = #
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True, nullable=False)
#     password_hash = db.Column(db.String(200), nullable=False)
#     stocks_history = db.relationship('Stock_History',backref='viewer',lazy=True  )
#     favourites_history = db.relationship('Favourites_History',backref='fav_user',lazy=True)

@app.route('/storehist')
def storehist() :
    if 'user_id' in session: 
        user_id = session['user_id']
        user = User.query.get(user_id)
        db.session.query(Stock_History).delete()
        stocks_viewed = list(curGraphSelection.keys())
        for stock_name in stocks_viewed :
            view_history = Stock_History(stock_name=stock_name ,viewer=user)
            db.session.add(view_history)
        db.session.commit()
    return (redirect(url_for('dashboard')))
@app.route('/set_to_fav')
def set_to_fav() :
    if 'user_id' in session :
        global stocks_in_fav
        global stocks_in_fav_symbols
        user_id = session['user_id']
        user = User.query.get(user_id)
        db.session.query(Favourites_History).delete()
        stocks_viewed = list(curGraphSelection.keys())
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
@app.route('/login_welcome')
def login_welcome():
    (script,div) = drawStockIndicesGraph()
    print('Hereeeeeeeeeeeeeeeeeeeeeeeee')
    print(*stocks_in_fav_symbols)
    print(*stocks_in_history_symbols)
    return render_template('loginWelcome.html',script=script,div=div,stocks_in_fav=stocks_in_fav , stocks_in_history=stocks_in_history,stocks_in_history_symbols=stocks_in_history_symbols,stocks_in_fav_symbols=stocks_in_fav_symbols
                           ,username=session['username'])
@app.route('/logout')
def logout():

    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/updateList',methods=['POST'])
def updateList():
    stockName = request.form['search_bar']
    if stockName not in stockList:
        if(not stockData.stockIsValid(stockName)):
            print("symbol Name",stockName,"is invalid directly going to dashboard")
            flash(stockName+ " is invalid please check")
            return redirect(url_for('dashboard'))
        stockList.append(stockName)
        last_selected = stockList
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

@app.route('/selectAndRemoveStock',methods=['POST']) 
#select stock function adds the stock symbol currently selected to the dictionary of graphs we want to draw
def stockselected ():
    global last_selected
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

@app.route('/process_duration' , methods = ['POST'])
#havent understood this one yet have to understand this one properly
def process_duration_fun() :
    global selected_duration
    initial = 0
    selected_duration = request.form.get('duration')
    for x in curGraphSelection :
        curGraphSelection[x]['graphDuration'] = selected_duration
    return redirect(url_for('dashboard'))


@app.route('/process_graph_options' ,methods = ['POST'])
def process_graph_options() :
    global curGraphSelection
    list_of_graphs = request.form.getlist("graph_options[]")
    graphTypeDict = curGraphSelection[currentlySelected]['graphCont']
    for key in graphTypeDict:
        graphTypeDict[key] = False
    for elm in list_of_graphs:
        graphTypeDict[elm] = True
    return redirect(url_for('dashboard'))


@app.route('/process_mode_change' , methods=['POST'])
def process_mode_change() :
    global mode
    mode = request.form.get('graph-mode')
    # print("came here")
    # print(mode)

    return redirect(url_for('dashboard'))

@app.route('/closeStock' , methods=['POST'])
def closeStock() :
    to_close = request.form.get('closedStock')
    global curGraphSelection
    global stockList
    del curGraphSelection[to_close]
    stockList.remove(to_close)
    # print(*stockList)
    # print(to_close)
    return redirect(url_for('dashboard'))
# @app.route('/process_filters_market_cap' , methods=['POST'])
# def process_filter() :
#     global filter_market_cap
#     filter_market_cap = request.form.get('marketCap')
#     process_filter()
#     return(redirect(url_for('sort_page')))

# @app.route('/process_filters_pe_rat' , methods = ['POST'])
# def filter_market_pe_rat() :
#     global filter_pe_rat
#     filter_pe_rat = request.form.get('pe_ratio')
#     process_filter()
#     return(redirect(url_for('sort_page')))

# @app.route('/process_filters_vol' , methods=['POST'])
# def process_filters_vol() :
#     global filter_avg_vol 
#     filter_avg_vol = request.form.get('vol')
#     process_filter()
#     return(redirect(url_for('sort_page')))

@app.route('/process_filters' , methods=['POST'])
def process_filters() :
    # global l_lim_price,m_lim_price,l_lim_marketCap,m_lim_marketCap,l_lim_pe_rat,m_lim_pe_rat,l_lim_vol,m_lim_vol
    global filter_lims , checked_filter_boxes
    l_lims = request.form.getlist('l_lim[]')
    m_lims = request.form.getlist('m_lim[]')
    list_check_status = request.form.getlist('checked_filter_boxes[]')
    list_check_status = [int(x) for x in list_check_status]
    # print('here')
    # print(*list_check_status)
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
    perform_filtering()
    return(redirect(url_for('sort_page')))
@app.route('/downloadTable',methods=['POST'])
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
def perform_filtering():
    global filtered_df , filtered_df_columns 
    # all_stocks_df['marketCap'] = all_stocks_df['marketCap']/10000000
    condition = (
        (pd.to_numeric(all_stocks_df['volume'], errors='coerce') >= filter_lims['vol'][0]) &
        (pd.to_numeric(all_stocks_df['volume'], errors='coerce') <= filter_lims['vol'][1]) &
        (pd.to_numeric(all_stocks_df['marketCap'], errors='coerce') >= filter_lims['marketCap'][0]) &
        (pd.to_numeric(all_stocks_df['marketCap'], errors='coerce') <= filter_lims['marketCap'][1]) &
        (pd.to_numeric(all_stocks_df['currentPrice'], errors='coerce') >= filter_lims['price'][0]) &
        (pd.to_numeric(all_stocks_df['currentPrice'], errors='coerce') <= filter_lims['price'][1]) &
        (pd.to_numeric(all_stocks_df['trailingPE'], errors='coerce') >= filter_lims['pe_rat'][0]) &
        (pd.to_numeric(all_stocks_df['trailingPE'], errors='coerce') <= filter_lims['pe_rat'][1])
    )
    filtered_df = all_stocks_df[condition]
    
    filtered_df = filtered_df.reset_index().rename(columns={'index':'Symbol'})
    filtered_df = filtered_df.rename(columns={'marketCap':'Market Cap(in Cr)' , 'previousClose':'Prev. Close' , 'sector':'Sector' ,'open':'Open','dayLow':'Low','dayHigh' :'High' , 'currentPrice':'Price' , 'trailingPE' :'PE' ,'volume' :'Volume'})
    # filtered_df['Market Cap(in Cr)'] = filtered_df['Market Cap(in Cr)']/100000000
    # filtered_df['Market Cap(in Cr)'] = filtered_df['Market Cap(in Cr)'].round(2)
    # print('Here I am ')
    # for col in filtered_df :
    #     print(col)
    filtered_df['PE'] = pd.to_numeric(filtered_df['PE'], errors='coerce')
    filtered_df['PE'] = filtered_df['PE'].round(2)
    filtered_df = filtered_df.rename(columns={'industryKey' : 'Industry'})

    colums_order = ['Symbol' , 'Industry' , 'Sector' , 'Prev. Close' , 'Open' , 'Low' , 'High' , 'Price' ,'Volume' , 'PE' , 'Market Cap(in Cr)']
    filtered_df = filtered_df[colums_order]

    # print(filtered_df['PE'])
    filtered_df_columns = filtered_df.columns
    # print('lessgo')

    checked_boxes_industry_list = []
    if checked_filter_boxes[11] == 'no' :
        for i in range(0,10) :
            if checked_filter_boxes[i] == 'yes' :
                checked_boxes_industry_list.append(Industries_filter[i])
        if checked_filter_boxes[10] == 'yes' :
            for x in allIndustriesList :
                if not(x in Industries_filter) :
                    checked_boxes_industry_list.append(x)
        filtered_df = filtered_df[filtered_df['Industry'].isin(checked_boxes_industry_list)]
    return 


@app.route('/sort_filters' , methods=['POST'])
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

if __name__ == '__main__':
#helps ensure we don't have to restart derver on chaning code
    app.run(debug=True)
