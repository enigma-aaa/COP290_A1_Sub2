from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import graph
import stockData  
import graphPage
import stockFilterPage

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
    return stockFilterPage.sort_page()

@app.route('/storehist')
def storehist() :
    return stockFilterPage.storehist()
@app.route('/set_to_fav')
def set_to_fav() :
    return stockFilterPage.set_to_fav()

@app.route('/login_welcome')
def login_welcome():
    (script,div) = graph.drawStockIndicesGraph()
    return render_template('loginWelcome.html',script=script,div=div,stocks_in_fav=stocks_in_fav , stocks_in_history=stocks_in_history,stocks_in_history_symbols=stocks_in_history_symbols,stocks_in_fav_symbols=stocks_in_fav_symbols
                           ,username=session['username'])
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/process_filters' , methods=['POST'])
def process_filters():
    return stockFilterPage.process_filters()
@app.route('/sort_filters' , methods=['POST'])
def sort_filters() :
    return stockFilterPage.sort_filters()


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
