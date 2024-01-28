from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import RangeTool,PanTool,WheelZoomTool,HoverTool
from bokeh.layouts import column,layout
import pandas as pd
import stockData
# import sys
import math
import colorGenerator
# inf = sys.maxsize
inf = math.inf
excel_file_path = 'MCAP31122023.xlsx'
pickel_file_path = 'Data_folder/AllStocks.pkl'
# all_stocks_df = pd.read_excel(excel_file_path)
all_stocks_df = pd.read_pickle(pickel_file_path)
# print(all_stocks_df)
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

filtered_df = pd.DataFrame()
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
class User(db.Model):
    #by defualt table name lowercase class name#
    #explicit definiton __tablename__ = #
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

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



@app.route('/')
def index():
    return render_template('login.html')
#understand what get and post is
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        userExist = User.query.filter_by(username=username).first()
        if userExist:
            #check to check if username already exists to fix it up
            flash('Username already exists choose different username')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))


def drawOpenGraph(symbolName,plot,df):
    color = colorGenerator.genColor()
    plot.line(df['Datetime'],df['Open'],legend_label=symbolName+" Open",line_width=2,color = color)
#code for drawing the close prices of the stock available in the dataframe
def drawCloseGraph(symbolName,plot,df):
    color = colorGenerator.genColor()
    plot.line(df['Datetime'],df['Close'],legend_label=symbolName+" Close",line_width=2,color=color)
#code for drawing the high prices
def drawHighGraph(symbolName,plot,df):
    color = colorGenerator.genColor()
    plot.line(df['Datetime'],df['High'],legend_label=symbolName+" High",line_width=2,color=color)
#code for drawing the low prices
def drawLowGraph(symbolName,plot,df):
    color = colorGenerator.genColor()
    plot.line(df['Datetime'],df['Low'],legend_label=symbolName+" Low",line_width=2,color=color)
#code for drawing a combined candle stick graph to consisting of 
#high low prices as segments
#the blocks represent opening and closing prices
def drawCombinedGraph(symbolName,plot,df,timeInterval):
    #this draws the segemnt from the opening to the closing price
    color = colorGenerator.genColor()
    plot.segment(df.Datetime,df.High,df.Datetime,df.Low,color=color,legend_label=symbolName+" Combined")
    #different plots for open price above close price and 
    #close price above open price
    #boolean arrs to show whether opening price is above or below closing price
    barWidth = timeInterval/2
    priceInc = df.Close > df.Open 
    priceDec = df.Open > df.Close 
    #add legend lable here later perhaps?
    plot.vbar(df.Datetime[priceDec],barWidth,df.Open[priceDec],df.Close[priceDec],color="#eb3c40")
    plot.vbar(df.Datetime[priceInc],barWidth,df.Open[priceInc],df.Close[priceInc],color="#0000ff",
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
    panTool = PanTool(dimensions = 'width')
    wheelZoomTool = WheelZoomTool()
    hoverTool = HoverTool(
        tooltips = [('date','$x{%F}'),('price','$y{(0.00 a)}')],
        formatters={'$x':'datetime'}
    )
    tools = [panTool,wheelZoomTool,hoverTool]

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

        for elm in graphCont:
            if graphCont[elm] :
                match elm:
                    case 'OPEN':
                        drawOpenGraph(symbolName,plot,df)
                        drawOpenGraph(symbolName,rangePlot,df)
                    case 'CLOSE':
                        drawCloseGraph(symbolName,plot,df)
                        drawCloseGraph(symbolName,rangePlot,df)
                    case 'HIGH':
                        drawHighGraph(symbolName,plot,df)
                        drawHighGraph(symbolName,rangePlot,df)
                    case 'LOW':
                        drawLowGraph(symbolName,plot,df)
                        drawLowGraph(symbolName,rangePlot,df)
                    case 'COMBINED':
                        drawCombinedGraph(symbolName,plot,df,timeInterval)
                        drawCombinedGraph(symbolName,rangePlot,df,timeInterval)

    total = column(plot,rangePlot,sizing_mode="stretch_both")
    script,div = components(total)
        
    #modifying div generated by bokeh library so that we can add the styling from our css file
    div = div[:-7] + ' class="GraphDiv" ></div>'
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
    if 'user_id' in session:
        dataFrameDict = getStockDataFrameInfo()
        script1,div1 = drawCurGraphAndTable(dataFrameDict)
        padCurStockInfo(curStockInfo)
        return render_template('welcome.html', username=session['username'],
        stockList=stockList,script=script1,div=div1,curStockInfo=curStockInfo , 
        curGraphSelection=curGraphSelection ,
        selected_duration = selected_duration,dataFrameDict=dataFrameDict , 
        currentlySelected = currentlySelected , mode=mode)
    else:
        return redirect(url_for('index'))
@app.route('/sort_page')
def sort_page():
    print('gonna render')
    print(filtered_df)
    print(*filtered_df_columns)
    return render_template('sort.html' , stockList = stockList ,filtered_df = filtered_df ,filtered_df_columns = filtered_df_columns )
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
    print("came here")
    print(mode)
    return redirect(url_for('dashboard'))

@app.route('/closeStock' , methods=['POST'])
def closeStock() :
    to_close = request.form.get('closedStock')
    global curGraphSelection
    global stockList
    del curGraphSelection[to_close]
    stockList.remove(to_close)
    print(*stockList)
    print(to_close)
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
    global filter_lims
    l_lims = request.form.getlist('l_lim[]')
    m_lims = request.form.getlist('m_lim[]')
    i = 0 
    for x in filter_lims :
        if l_lims[i] != '' :
            filter_lims[x][0] = int(l_lims[i])
        else :
            filter_lims[x][0] = 0
        if m_lims[i] != '' :
            filter_lims[x][1] = int(m_lims[i])
        else :
            filter_lims[x][1] = inf
        i+=1 
    print(filter_lims)
    print('calling function')
    perform_filtering()
    print('done')
    return(redirect(url_for('sort_page')))
def perform_filtering():
    global filtered_df , filtered_df_columns
    print('inside perform_filtering')
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
    filtered_df_columns = filtered_df.columns
    fi
    print('lessgo')
    return 

if __name__ == '__main__':
#helps ensure we don't have to restart derver on chaning code
    app.run(debug=True)
