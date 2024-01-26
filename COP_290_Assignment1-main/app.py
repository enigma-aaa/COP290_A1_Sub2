from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import RangeTool,PanTool,WheelZoomTool
from bokeh.layouts import column,layout
import pandas as pd
import stockData
print("It came hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
initial = 1
app = Flask(__name__)
#change secret key later
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database Configuration
# if initial == 1 :
selected_duration = '1_day'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
stockList = ["SBIN","ONGC","TATASTEEL"]
curStockInfo = {}
selectedStocksList = []
selected_graphs = {
    "HIGH" : True ,
    "LOW" : False,
    "OPEN" : False ,
    "CLOSE" : False ,
    "COMBINED" : False
}
last_selected = 'SBIN'
#should contain an array of dict's with each dict of the form
#{
#    'SBIN':{
#        'graphDuration':['DAILY'],
#        'graphCont':['OPEN','CLOSE','HIGH','LOW','COMBINED']
#    }
#}
curGraphSelection = {
    'SBIN':{
        'graphDuration':'1_day' ,
        'graphCont':{
    "HIGH" : True ,
    "LOW" : False,
    "OPEN" : False ,
    "CLOSE" : False ,
    "COMBINED" : False
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
@app.route('/')
def index():
    return render_template('login.html')
#understand what get and post is
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #have to add check for unique password
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        userExist = User.query.filter_by(username=username).first()
        if userExist:
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

#should contain an array of dict's with each dict of the form
#{
#    'SBIN':{
#        'graphDuration':['DAILY'],
#        'graphCont':['OPEN','CLOSE','HIGH','LOW','COMBINED']
#    }
#
def drawOpenGraph(symbolName,plot,df):
    plot.line(df['Datetime'],df['Open'],legend_label=symbolName+" Open",line_width=2)
def drawCloseGraph(symbolName,plot,df):
    plot.line(df['Datetime'],df['Close'],legend_label=symbolName+" Close",line_width=2)
def drawHighGraph(symbolName,plot,df):
    plot.line(df['Datetime'],df['High'],legend_label=symbolName+" High",line_width=2)
def drawLowGraph(symbolName,plot,df):
    plot.line(df['Datetime'],df['Low'],legend_label=symbolName+" Low",line_width=2)
def drawCombinedGraph(symbolName,plot,df,timeInterval):
    plot.segment(df.Datetime,df.High,df.Datetime,df.Low,color="black")
    #different plots for open above close and 
    #close above open
    #boolean arrs to show whether opening price
    # is above or below closing price
    barWidth = timeInterval/2
    priceInc = df.Close > df.Open 
    priceDec = df.Open > df.Close 
    #add legend lable here later perhaps?
    plot.vbar(df.Datetime[priceDec],barWidth,df.Open[priceDec],df.Close[priceDec],color="#eb3c40")
    plot.vbar(df.Datetime[priceInc],barWidth,df.Open[priceInc],df.Close[priceInc],color="#0000ff",
              line_color="00ffff",line_width=2)
#should contain an array of dict's with each dict of the form
#{
#    'SBIN':{
#        'graphDuration':['DAILY'],
#        'graphCont':['OPEN','CLOSE','HIGH','LOW','COMBINED']
#    }
#}
#draws the current graph and generates the data required for the table
def getStockDataFrameInfo():
    global curStockInfo
    dataFrameDict = {}
    for symbolName in curGraphSelection:
        curDict = curGraphSelection[symbolName]
        duration_req = curDict['graphDuration']
        # print(duration_req + "hhhhhhhhhhhhhh")
        df = stockData.controltime(symbolName,duration_req)
        curStockInfo = stockData.getInfo(symbolName)
        dataFrameDict[symbolName] = df
    #print('data frame dict is:')
    #print(dataFrameDict)
    return dataFrameDict
def drawCurGraphAndTable(dataFrameDict):
    global curStockInfo
    panTool = PanTool(dimensions = 'width')
    wheelZoomTool = WheelZoomTool()
    tools = [panTool,wheelZoomTool]
    plot = figure(x_axis_label="Date Time",y_axis_label="Price",
                x_axis_type="datetime",toolbar_location="right",
                tools= tools)
    plot.sizing_mode = "stretch_both"

    rangePlot = figure(height=100,x_axis_type="datetime",
                        y_axis_type=None,toolbar_location=None,
                        background_fill_color="#efefef")
    rangePlot.sizing_mode = "stretch_width"
        
    rangeTool = RangeTool(x_range=plot.x_range)
    rangeTool.overlay.fill_color = "navy"
    rangeTool.overlay.fill_alpha = 0.2
    rangePlot.add_tools(rangeTool)
    rangePlot.toolbar.active_multi = 'auto'
    #dataFrameDict = {}
    for symbolName in curGraphSelection:
        #print(symbolName)
        curDict = curGraphSelection[symbolName]
        duration_req = curDict['graphDuration']
        # print(duration_req + "hhhhhhhhhhhhhh")
        df = dataFrameDict[symbolName]
        curStockInfo = stockData.getInfo(symbolName)
        #time interval defiend here too
        #for daily one min interval in milli seconds
        timeInterval = 60*1000
        timePeriod = curDict['graphDuration']
        graphCont = curDict['graphCont']
        
        #rangePlot.toolbar.active_multi = rangeTool
        #print(graphCont)
        #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
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

        #print("help is")
        #print(help(rangePlot.toolbar))

    total = column(plot,rangePlot,sizing_mode="stretch_both")
    script,div = components(total)
        
    # print("original div was:")
    # print(div)
    div = div[:-7] + ' class="GraphDiv" ></div>'
    return (script,div)
    # print("original div was:")
    # print(div)
    div = div[:-7] + ' class="GraphDiv" ></div>'
    return (script,div,dataFrameDict)

@app.route('/dashboard') 
def dashboard():
    if 'user_id' in session:
        #x = [1,2,3,4,5]
        #y = [6,7,2,4,5]
        #df = pd.read_pickle('./Data_folder/SBIN.pkl')
        #print("data frame is:")
        #print(df)
        #p1 = figure(title="Simple Example",x_axis_label='x',y_axis_label='y',x_axis_type="datetime",toolbar_location="right")
        #df['DATE'] = pd.to_datetime(df['DATE'])
        #p1.line(df['DATE'],df['CLOSE'],legend_label="Stock Close",line_width=2)
        #p1.line(df['DATE'],df['HIGH'],legend_label="Stock High",line_width=2)

        dataFrameDict = getStockDataFrameInfo()
        script1,div1 = drawCurGraphAndTable(dataFrameDict)
        #print("Script is:")
        #print(script1)
        #print("div is:")
        #print(div1)
        #print("curStockInfo is:")
        #print(curStockInfo)
        return render_template('welcome.html', username=session['username'],
        stockList=stockList,script=script1,div=div1,curStockInfo=curStockInfo , 
        curGraphSelection=curGraphSelection ,
        selected_duration = selected_duration,dataFrameDict=dataFrameDict , selected_graphs=selected_graphs )
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/updateList',methods=['POST'])
def updateList():
    stockName = request.form['search_bar']
    if stockName not in stockList:
        stockList.append(stockName)
    return redirect(url_for('dashboard'))

@app.route('/selectStock',methods=['POST']) 
def stockselected ():
    global last_selected
    stockName = request.form.get('selectedStock')

    if stockName in curGraphSelection : 
        del curGraphSelection[stockName]
    else : 
        curGraphSelection[stockName] = {
            'graphDuration' :'1_day',
            'graphCont' : ['HIGH']
        }
    if len(list(curGraphSelection.keys())) >=1 : 
        last_selected = list(curGraphSelection.keys())[-1]
    else :
        last_selected = ''
    return redirect(url_for('dashboard'))
@app.route('/process_duration' , methods = ['POST'])
def process_duration_fun() :
    # global initial
    global selected_duration
    initial = 0
    selected_duration = request.form.get('duration')
    # print(selected_dur + 'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
    # print(selected_dur+"aaaaaaaaaaaaaa")
    for x in curGraphSelection :
        curGraphSelection[x]['graphDuration'] = selected_duration
    return redirect(url_for('dashboard'))


@app.route('/process_graph_options' ,methods = ['POST'])
def process_graph_options() :
    global selected_graphs 
    global curGraphSelection
    list_of_graphs = request.form.getlist("graph_options[]")

    # print(graphs_selected_now + "llllllllllllllllllllllllllllllllllllllll")
    # print("hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
    for x in selected_graphs :
        if x in list_of_graphs:
            selected_graphs[x] = True 
        else :
            selected_graphs[x] = False 
    # if selected_graphs[graphs_selected_now] :
    #     selected_graphs[graphs_selected_now] = False
    # else :
    #     selected_graphs[graphs_selected_now] = True
    # if(len(list_of_graphs) == 0) :
        # return redirect(url_for('dashboard'))
    # if(list_of_graphs[-1] in selected_graphs ) :
        # selected_graphs.remove(list_of_graphs[-1])
    # else :
        # selected_graphs.append(list_of_graphs[-1])
    
    # selected_graphs[graphs_selected_now] = true 
    # print(list_of_graphs)
    # print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    print(last_selected)
    print("printing graph selection from process_gaph_options")
    curGraphSelection[last_selected]['graphCont'] = selected_graphs
    print(curGraphSelection)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
#helps ensure we don't have to restart derver on chaning code
    app.run(debug=True)
