from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import graph
import pandas as pd
import stockData
import numpy as np
# import sys
import math
import os
import colorGenerator
import graphPage
from filterStocks import allIndustriesList,companies_to_remove,initStockInfo,perform_filtering

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


initial = 1
app = Flask(__name__)
#change secret key later
app.secret_key = 'your_secret_key'  # Replace with your actual secret key


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

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

    return render_template('register.html')

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

@app.route('/sort_page')
def sort_page():
    # print('gonna render')
    # print(filtered_df)
    # print(*filtered_df_columns)
    return render_template('sort.html' , stockList = graphPage.stockList ,filtered_df = filtered_df ,
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
        stocks_viewed = list(graphPage.getCurGraphSelection().keys())
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
@app.route('/login_welcome')
def login_welcome():
    (script,div) = graph.drawStockIndicesGraph()
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
    global filtered_df,filtered_df_columns

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
    (filtered_df,filtered_df_columns)  = perform_filtering(all_stocks_df,filter_lims,checked_filter_boxes,Industries_filter)
    return(redirect(url_for('sort_page')))




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

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    return graphPage.dashboard(session,stocks_in_history)
@app.route('/updateList',methods=['POST','GET'])
def updateList():
    return graphPage.updateList()
@app.route('/selectAndRemoveStock',methods=['POST','GET'])
def stockselected():
    return graphPage.stockselected()
@app.route('/process_duration' , methods = ['POST','GET'])
def process_duration_fun():
    return graphPage.process_duration_fun()
@app.route('/process_graph_options' ,methods = ['POST','GET'])
def process_graph_options():
    return graphPage.process_graph_options()
@app.route('/closeStock' , methods=['POST'])
def closeStock():
    return graphPage.closeStock()
@app.route('/process_mode_change' , methods=['POST'])
def process_mode_change():
    return graphPage.process_mode_change()
@app.route('/downloadTable',methods=['POST'])
def downloadTable():
    return graphPage.downloadTable()

if __name__ == '__main__':
#helps ensure we don't have to restart derver on chaning code
    app.run(debug=True)
