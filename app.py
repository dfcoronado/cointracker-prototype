# app.py
from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from database import *
from main import *

app = Flask(__name__, template_folder='html')  # app with template folder = html
app.secret_key = 'cointracker_pt'  
login_manager = LoginManager()  # instance of LoginManager
login_manager.init_app(app)  # initialize LoginManager with Flask app

# Import databases
users_db = UsersDB()
btc_balances_db = BTCBalancesDB()
transactions_db = TransactionsDB()

# Classes from main.py
bitcoin_addresses = BitcoinAddresses()
sync = SynchronizeBitcoinAddress()
retrieve_data = RetrieveData()

# Classes from BlockChain API
blockchain_api = BlockChainAPI()

class User(UserMixin):
    pass

# LOAD USERS
@login_manager.user_loader
def load_user(username):
    user_data = users_db.get_user(username)
    if user_data:
        user = User()
        user.id = user_data['username']
        user.password = user_data['password']
        return user
    return None

# HOME
@app.route('/')
def home():
    return render_template('home.html')

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        existing_user = users_db.get_user(username)
        if existing_user:
            error = "Username already exists. Please login instead."
            return render_template('login.html', error=error)

        # Attempt to add the new user
        if users_db.add_user(username, password):
            return render_template('registration_success.html', username=username)
        else:
            return f"Failed to register user '{username}'. Please try again."
    return render_template('register.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user data from database
        user_data = users_db.get_user(username)

        # Validate user credentials
        if user_data and user_data['password'] == password:
            user = User()
            user.id = user_data['username']
            user.password = user_data['password']
            login_user(user)  # Log in the user
            return redirect(url_for('loggedin', username=username))
        else:
            error = "Incorrect username or password. Please try again or register if you're a new user."
            return render_template('login.html', error=error)
    return render_template('login.html')

# LOGGED IN FEATURES (All 3 Requirements)
@app.route('/loggedin', methods=['GET', 'POST'])
@login_required
def loggedin():
    message = ""
    username = request.args.get('username')  # Extract username from URL query parameter

    if request.method == 'POST':
        username = request.form['username']  # Retrieve username from form data
        action = request.form['action']  # Retrieve the action (add or remove)

        # Feature 1: Add/Remove Addresses
        if action == 'add_address':
            btc_address = request.form['btc_address']
            if btc_address in bitcoin_addresses.get_btc_addresses_for_user(username):
                message = f"Cannot add BTC address '{btc_address}, It is already on CoinTracker."
                return render_template('loggedin.html', username=username, message=message)
            
            elif bitcoin_addresses.add_address(btc_address, username):
                message = f"Hi {username}. You've successfully added '{btc_address}' to CoinTracker!"
                # Add BTC_Address and transaction to Transactions DB to use later
                sync.add_transactions(username, btc_address)
                return render_template('loggedin.html', username=username, message=message)
            
            else:
                message = f"Invalid address. Cannot add claimed BTC address '{btc_address}'."
                return render_template('loggedin.html', username=username, message=message)

        elif action == 'remove_address':
            btc_address = request.form['btc_address']
            if btc_address not in bitcoin_addresses.get_btc_addresses_for_user(username) and \
                not blockchain_api.valid_btc_address(btc_address): 
                message = f"Cannot remove BTC address '{btc_address}' because it is an invalid BTC address."
                return render_template('loggedin.html', username=username, message=message)
            
            elif btc_address in bitcoin_addresses.get_btc_addresses_for_user(username) and \
                bitcoin_addresses.remove_address(btc_address):
                message = f"Hi {username}. You've successfully removed BTC address '{btc_address}' from CoinTracker!"
                return render_template('loggedin.html', username=username, message=message)
            
            else:
                message = f"Cannot remove BTC address '{btc_address}' because you don't own it."
                return render_template('loggedin.html', username=username, message=message)
        
        # Feature 2: Synchronize BTC transactions with BTC addresses
        elif action == 'btc_transactions':
            btc_addresses = bitcoin_addresses.get_btc_addresses_for_user(username)
            btc_transactions = {}

            for btc_address in btc_addresses:
                transactions_for_btc_address = sync.get_transactions_table_for_btc_address(btc_address)
                btc_transactions[btc_address] = transactions_for_btc_address
            
            num_of_btc_addresses = retrieve_data.number_of_btc_addreses_owned(btc_addresses)
            return render_template('transactions.html', username=username, btc_transactions=btc_transactions, num_of_btc_addresses=num_of_btc_addresses)
        
        # Feature 3: Synchronize BTC transactions with BTC addresses
        elif action == 'retrieve':
            btc_addresses = bitcoin_addresses.get_btc_addresses_for_user(username)
            num_of_btc_addresses = retrieve_data.number_of_btc_addreses_owned(btc_addresses)
            btc_addresses_data = retrieve_data.get_btc_and_balance_data(btc_addresses)
            total_btc_owned = retrieve_data.get_total_amount(btc_addresses)
            btc_transactions = retrieve_data.get_btc_transactions(btc_addresses)
            return render_template('retrieve.html', username=username, btc_addresses=btc_addresses_data, btc_transactions=btc_transactions, total_btc_owned=total_btc_owned, num_of_btc_addresses=num_of_btc_addresses)
    
    return render_template('loggedin.html', username=username)

# LOGOUT
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()  # Log out the user
        session.pop('username', None)
        return redirect(url_for('home'))  # Redirect to home page after logout
    else:
        return redirect(url_for('home'))  # If accessed via GET, redirect to home page


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)