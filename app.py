# import os
# import requests
import datetime

from cs50 import SQL
from config import mail_email, app_password
from flask import Flask, flash, redirect, render_template, request, session, jsonify, Response, make_response
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from statistics import mean, fmean
from decimal import Decimal
import collections, functools, operator
from json import dumps
from random import choice
from string import printable, ascii_letters, digits
# from datetime import datetime, timedelta

from helpers import apology, top_ten, top_alts, top_memes, trending, login_required, usd, crypt, percent

# Configure application
app = Flask(__name__)

mail = Mail(app)

# Configure flask_mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_email
app.config['MAIL_PASSWORD'] = app_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crypto.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Register new user account
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Validate submissions
        email = request.form.get("email")
        username = request.form.get("username").lower()
        name = request.form.get("full_name")
        password = request.form.get("password")
        hash = generate_password_hash(password)
        confirm = request.form.get("confirmation")

        # Query database for existing username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        e_rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        if not email or not len(e_rows) != 1:
            return apology("must provide email and/or email already exists", 400)

        # Send error message if user already exists or field left empty
        if not username or not len(rows) != 1:
            return apology("must provide username and/or userame already exists", 400)

        # Send error message if no password or password doesn't match confirmation
        elif not password or not (password == confirm):
            return apology("must provide password and/or password doesn't match confirmation", 400)

        # Apply user credentials to database
        db.execute("INSERT INTO users (username, name, email, hash) VALUES (?, ?, ?, ?)", username, name, email, generate_password_hash(password))

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# Log in for users
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username").lower()
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        hashed = rows[0]["hash"]
        verify = check_password_hash(hashed, password)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not verify:
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Dashboard (Homepage) that ETF's items to purchase
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "GET":
        # Get arguments to pass to API function requests
        symbols = request.args.get("symbols")

        # API function requests
        top_etf = top_alts(symbols)
        majors = top_ten(symbols)
        memes = top_memes(symbols)

        # Find sum for every float price in each API request
        f_total = sum(float(d["price"]) for d in top_etf)
        fm_total = sum(float(e["price"]) for e in majors)
        fmeme_total = sum(float(f["price"]) for f in memes)

        # Convert sums into fiat currency $
        alt_total = usd(f_total)
        m_total = usd(fm_total)
        meme_total = usd(fmeme_total)

        return render_template("index.html", majors=majors, top_etf=top_etf, memes=memes, m_total=m_total, meme_total=meme_total, alt_total=alt_total)


# Implement buy function on the same page for the Top 10 etf form
@app.route("/majors_buy", methods=["Get","POST"])
@login_required
def major_buy():

    if request.method == "GET":
        # On get request return homepage
        return render_template("index.html")
    else:
        # Get form input and apply it to API function as a parameter
        symbols = request.args.get("symbols")
        X = top_ten(symbols)
        # Name of custom made etf
        etf = "Top 10"

        # Ensures that form input is a positive integer else throw error message
        try:
            major_shares = int(request.form.get("major_buy"))
        except:
            return apology("share size must be a positive number")

        # Ensures that entry is not a negative number
        if major_shares <= 0:
            return apology("Share size must not be less than 0")

        # Dictionary comprehension to find sum of price floats
        major_price = sum(float(row["price"]) for row in X)
        # Variable for cost which is number of shares times price of etf
        major_cost = major_shares * major_price

        # Query users database for cash amount
        user_id = session["user_id"]
        major_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_major_cash = major_cash[0]["cash"]

        # Ensures user has enough cash to buy the etf at share amount
        if user_major_cash < major_cost:
            return apology("not enough cash to buy etf", 400)

        # Variable for users new balance after purchase
        new_balance = user_major_cash - major_cost

        # Update database with users new balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)
        # Record time of purchase
        date = datetime.datetime.now()

        # For now this snippet is irrelivant. It was meant to store names and symbols from the purchased etf and store it into the database. Unfortunately the database cannot store multiple arguments for a single row
        name = []
        symbols = []
        for i in range(len(X)):
            name.append(X[i]["name"])
            symbols.append(X[i]["symbol"])

        # Insert information into databse
        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, major_cost, major_shares, date)

        # Alert user of purchase
        flash(f"{major_shares} of {etf} ETF's have been bought!")

        # Return home
        return redirect("/")


# Same implentation as major_buy for Alt coins etf
@app.route("/alts_buy", methods=["GET","POST"])
@login_required
def alt_buy():

    if request.method == "GET":
        return render_template("index.html")
    else:

        symbols = request.args.get("symbols")
        Xalt = top_alts(symbols)
        etf = "AltCoins"

        try:
            alt_shares = int(request.form.get("alt_buy"))
        except:
            return apology("share size must be a positive number")

        if alt_shares <= 0:
            return apology("Share size must not be less than 0")

        alt_price = sum(float(row["price"]) for row in Xalt)

        alt_cost = alt_shares * alt_price

        user_id = session["user_id"]
        alt_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_alt_cash = alt_cash[0]["cash"]

        if user_alt_cash < alt_cost:
            return apology("not enough cash to buy etf", 400)

        new_balance = user_alt_cash - alt_cost

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        date = datetime.datetime.now()

        name = []
        symbols = []

        for i in range(len(Xalt)):
            name.append(Xalt[i]["name"])
            symbols.append(Xalt[i]["symbol"])

        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, alt_cost, alt_shares, date)

        flash(f"{alt_shares} of {etf} ETF's have been bought!")

        return redirect("/")


# Same implentation as major_buy for meme coins etf
@app.route("/memes_buy", methods=["GET","POST"])
@login_required
def meme_buy():

    if request.method == "GET":
        return render_template("index.html")
    else:
        symbols = request.args.get("symbols")
        Xmeme = top_memes(symbols)
        etf = "MemeCoins"

        try:
            meme_shares = int(request.form.get("meme_buy"))
        except:
            return apology("share size must be a positive number")

        if meme_shares <= 0:
            return apology("Share size must not be less than 0")

        meme_price = sum(float(row["price"]) for row in Xmeme)

        meme_cost = meme_shares * meme_price

        user_id = session["user_id"]
        meme_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_meme_cash = meme_cash[0]["cash"]

        if user_meme_cash < meme_cost:
            return apology("not enough cash to buy etf", 400)

        new_balance = user_meme_cash - meme_cost

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        date = datetime.datetime.now()

        name = []
        symbols = []

        for i in range(len(Xmeme)):
            name.append(Xmeme[i]["name"])
            symbols.append(Xmeme[i]["symbol"])

        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, meme_cost, meme_shares, date)

        flash(f"{meme_shares} of {etf} ETF's have been bought!")

        return redirect("/")


# Implement sell function on same page for Top 10 etf form
@app.route("/majors_sell", methods=["GET","POST"])
@login_required
def major_sell():
    # Grab users id and name of custom made etf
    user_id = session["user_id"]
    etf = "Top 10"

    if request.method == "GET":
        return render_template("index.html")
    else:
        # Get form input and apply it to API function as a parameter
        symbols = request.args.get("symbols")
        X = top_ten(symbols)

        # Ensures that the users input is a positive number else throw error message
        try:
            major_shares = int(request.form.get("major_sell"))
        except:
            return apology("share size must be a positive number")

        # Ensures users input is not a negative integer
        if major_shares <= 0:
            return apology("Share size must not be less than 0")

        # Dictionary comprehension for the sum of price floats
        major_price = sum(float(row["price"]) for row in X)
        # Calculate cost by multiplying share amount by price
        major_cost = major_shares * major_price
        # Query databse for users cash amount
        major_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_major_cash = major_cash[0]["cash"]

        # Query database for shares and ensures the user has the amount of shares they are trying to sell. If not then throw error
        try:
            sell_shares = db.execute("SELECT SUM(coins) AS coins FROM etf_grid WHERE user_id = ? AND etf = ? GROUP BY etf", user_id, etf)
            sell_coins = sell_shares[0]["coins"]

            if len(sell_shares) != 1 or sell_coins <= -1 or sell_coins < major_shares:
                return apology("you don't have enough coins of this etf", 400)

        except IndexError:
            return apology("you must have these coins in order to buy", 400)

        # Calculate users new balance
        new_balance = user_major_cash + major_cost
        # Update users balance with new balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)
        # Record time of purcahse
        date = datetime.datetime.now()

        # For now this snippet is irrelivant. It was meant to store names and symbols from the purchased etf and store it into the database. Unfortunately the database cannot store multiple arguments for a single row
        name = []
        symbols = []
        for i in range(len(X)):
            name.append(X[i]["name"])
            symbols.append(X[i]["symbol"])

        # Insert information into database
        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, (-1) * major_cost, (-1) * major_shares, date)

        # Alert user on successful sale
        flash(f"{major_shares} of your {etf} ETF's have been Sold!")

        # Return to homepage
        return redirect("/")


# Same implentation as major_sell for Alt coins etf
@app.route("/alts_sell", methods=["GET","POST"])
@login_required
def alt_sell():
    user_id = session["user_id"]
    etf = "AltCoins"

    if request.method == "GET":
        return render_template("index.html")
    else:

        symbols = request.args.get("symbols")
        Xalt = top_alts(symbols)

        try:
            alt_shares = int(request.form.get("alt_sell"))
        except:
            return apology("share size must be a positive number")

        if alt_shares <= 0:
            return apology("Share size must not be less than 0")

        alt_price = sum(float(row["price"]) for row in Xalt)

        alt_cost = alt_shares * alt_price

        alt_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_alt_cash = alt_cash[0]["cash"]

        try:
            sell_shares = db.execute("SELECT SUM(coins) AS coins FROM etf_grid WHERE user_id = ? AND etf = ? GROUP BY etf", user_id, etf)
            sell_coins = sell_shares[0]["coins"]

            if len(sell_shares) != 1 or sell_coins <= -1 or sell_coins < alt_shares:
                return apology("you don't have enough coins of this etf", 400)

        except IndexError:
            return apology("you must have these coins in order to buy", 400)

        new_balance = user_alt_cash + alt_cost

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        date = datetime.datetime.now()

        name = []
        symbols = []

        for i in range(len(Xalt)):
            name.append(Xalt[i]["name"])
            symbols.append(Xalt[i]["symbol"])

        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, (-1) * alt_cost, (-1) * alt_shares, date)

        flash(f"{alt_shares} of your {etf} ETF's have been Sold!")

        return redirect("/")


# Same implentation as major_sell for meme coins etf
@app.route("/memes_sell", methods=["GET","POST"])
@login_required
def meme_sell():
    user_id = session["user_id"]
    etf = "MemeCoins"

    if request.method == "GET":
        return render_template("index.html")

    else:

        symbols = request.args.get("symbols")
        Xmeme = top_memes(symbols)

        try:
            meme_shares = int(request.form.get("meme_sell"))
        except:
            return apology("share size must be a positive number")

        if meme_shares <= 0:
            return apology("Share size must not be less than 0")

        meme_price = sum(float(row["price"]) for row in Xmeme)

        meme_cost = meme_shares * meme_price

        meme_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_meme_cash = meme_cash[0]["cash"]

        try:
            sell_shares = db.execute("SELECT SUM(coins) AS coins FROM etf_grid WHERE user_id = ? AND etf = ? GROUP BY etf", user_id, etf)
            sell_coins = sell_shares[0]["coins"]

            if len(sell_shares) != 1 or sell_coins <= -1 or sell_coins < meme_shares:
                return apology("you don't have enough coins of this etf", 400)

        except IndexError:
            return apology("you must have these coins in order to buy", 400)

        new_balance = user_meme_cash + meme_cost

        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_balance, user_id)

        date = datetime.datetime.now()

        name = []
        symbols = []

        for i in range(len(Xmeme)):
            name.append(Xmeme[i]["name"])
            symbols.append(Xmeme[i]["symbol"])

        db.execute("INSERT INTO etf_grid (user_id, etf, price, coins, date) VALUES (?,?,?,?,?)", user_id, etf, (-1) * meme_cost, (-1) * meme_shares, date)

        flash(f"{meme_shares} of your {etf} ETF's have been Sold!")

        return redirect("/")

# Portfolio to display users stats and information
@app.route("/portfolio", methods=["GET"])
@login_required
def portfolio():

    # Get data from the arguments passed in the api function call
    category = request.args.get("category")
    trend = trending(category)

    # Iterate over api function to get each set of data for display
    for row in trend:
        row["avg_price_change"] = 100*float(round(row["avg_price_change"], 2))/100
        row["market_cap"] = usd(float(row["market_cap"]))
        row["market_cap_change"] = 100*float(round(row["market_cap_change"], 2))/100
        row["volume"] = usd(float(row["volume"]))

    # get user id
    user_id = session["user_id"]
    # Query database for users by user_id
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    # Query etf database for transactions
    transactions = db.execute("SELECT * FROM etf_grid WHERE user_id = ? ORDER BY date DESC", user_id)

    c_total = 0
    b_list = []

    # Ensures that if the user has made a transaction to return data, else return None, 0, or information that was already stored
    if transactions:
        username = user[0]["username"]
        name = user[0]["name"]
        c_balance = user[0]["cash"]
        etf = transactions[0]["etf"]
        coins = transactions[0]["coins"]
        # Iterate over database query and return prices of transactions
        # Append each purchase to empty balance list (b_list)
        for i in transactions:
            etf_cost = i["price"]
            b_list.append(etf_cost)
        # A List comprehension to find sum of all purchses and add sum to the users balance for the total amount that the user owns between shares and cash
        b_total = [x for x in b_list]
        c_total += c_balance + sum(b_total)
    else:
        username = user[0]["username"]
        name = user[0]["name"]
        c_balance = user[0]["cash"]
        c_total = c_balance
        etf = None
        etf_cost = 0
        coins = None

    # Display users Full name, since Full name is not required to provide; If the user didn't provide name, then display username
    display = ''

    if name == None:
        display += username
    else:
        display += name

    # convert balance and total to fiat currency $
    total = usd(c_total)
    balance = usd(c_balance)

    return render_template("portfolio.html", name=display, transactions=transactions, balance=balance, etf=etf, etf_cost=etf_cost, coins=coins, user=user, total=total, trend=trend)


# Allows user to add additional paper cash for purchases
@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():

    if request.method == "GET":
        return render_template("cash.html")
    else:
        user_id = session["user_id"]

        # Ensures that the cash amount entered is a positive integer
        try:
            add_cash = float(request.form.get("cash"))
        except:
            return apology("amount must be a postive number")

        # if user doesn't provide cash amount or the amount isn't a real number then return error
        if add_cash < 0 or not add_cash:
            return apology("please enter an accurate amount you want added")

        # Add user's current cash with the new cash amount submitted
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = user_cash[0]["cash"]
        new_cash = cash + add_cash

        # Update database with new cash amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, user_id)

        # Notify a succesful purchase
        flash("Cash added!")

    return redirect("/portfolio")


# Settings Render template
@app.route("/settings", methods=["GET"])
@login_required
def settings():
    return render_template("settings.html")

# Allows users to edit the data they provided for their profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    if request.method == "GET":
        # On Get request Query for users name, email, and username for display
        users = db.execute("SELECT name, username, email FROM users WHERE id = ?", user_id)

        name = users[0]["name"]
        username = users[0]["username"]
        email = users[0]["email"]

        return render_template("profile.html",name=name, username=username, email=email)
    else:
        # Form requests to change profile information
        name = request.form.get("name")
        username = request.form.get("username").lower()
        email = request.form.get("email")

        # If all fields are empty on submit return error message
        if not name and not username and not email:
            return apology("must enter details", 400)

        # Ensures that one or all inputs are fulfilled and updates databse with new entry
        if name:
            db.execute("UPDATE users SET name = ? WHERE id = ?", name, user_id)
        if username:
            db.execute("UPDATE users SET username = ? WHERE id = ?", username, user_id)
        if email:
            db.execute("UPDATE users SET email = ? WHERE id = ?", email, user_id)

        # Alert user on success
        flash("Profile updated!")

        return redirect("/profile")

# Verify password before user can change it
@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify():
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("verify.html")
    else:
        # Get form input
        password = request.form.get("password")
        # If the form is empty return error
        if not password:
            return apology("please enter password to continue", 400)

        # Query database for password and check if it's True
        user = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
        user_hash = user[0]["hash"]
        verify_hash = check_password_hash(user_hash, password)

        # If false then return error message
        if not verify_hash:
            return apology("sorry wrong password", 400)

        # Render change password template (go to next route)
        return render_template("password.html")

# Allows user to change their password
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    user_id = session["user_id"]
    # Ensures that user can only change their password if they have verified their old (current) password
    if request.method == "GET":
        return redirect("/verify")
    else:
        # Get form requests
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # If the user doesn't fill out both form inputs or if inputs don't match return error
        if not password:
            return apology("Please enter password", 400)
        elif not confirm:
            return apology("Please verify new password", 400)

        # Query database for user's passowrd
        user = db.execute("SELECT hash FROM users WHERE id = ?", user_id)
        user_hash = user[0]["hash"]
        # Decode password to check if password provided matches
        uncoded_hash = check_password_hash(user_hash, password)

        # If the password matches old password, prompt user to enter a new password
        if uncoded_hash:
            return apology("please enter a password that has not been used before")
        # If the two input fields do not match return error message
        if not password == confirm:
            return apology("password does not match confirmation")

        # Generate new password and update database
        new_password = generate_password_hash(password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_password, user_id)

        # Alert user that the password has been updated
        flash("Password has been changed!")

        return redirect("/settings")

# Validate users credit card information, but does not store or save it
@app.route("/credit", methods=["GET", "POST"])
@login_required
def credit():
    if request.method == "GET":
        return render_template("credit.html")
    else:
        cc = request.form.get("credit")

        am = ['34', '37']
        mc = ['51', '52', '53', '54', '55']
        vs = ['4']

        # Variable that iterates over the every other item in input starting at index-2
        evenCount = cc[-2::-2]
        # Variable that starts from index-1 and returns every other item
        oddCount = cc[-1::-2]

        # tmp variable that converts evenCount input into integers
        tmpEven = list(map(int, evenCount))
        # multiply every list item by 2
        newEven = [i * 2 for i in tmpEven]
        # convert newEven list into string list
        strEven = ''.join(map(str, newEven))
        # map through strEven list convert to integers digit by digit and add sum
        sumEven = sum(list(map(int, strEven)))
        # map through oddCount list convert to integers digit by digit and add sum
        sumOdd = sum(list(map(int, oddCount)))

        # add up the sum of lists
        checkSum = sumEven + sumOdd

        # if the last digit in the algorithmic equation is 0 then continue
        if (checkSum % 10 == 0):
            # if first 2 letters in list match as well as length of list match then print associated card
            if (cc[:2] == am[0] or cc[:2] == am[1]) and (len(cc) == 15):
                flash("Your AMEX is Accepted!")
            elif (cc[:2] == mc[0] or cc[:2] == mc[1] or cc[:2] == mc[2] or cc[:2] == mc[3] or cc[:2] == mc[4]) and (len(cc) == 16):
                flash("Your MASTERCARD is Accepted!")
            elif (cc[:1] == vs[0]) and (len(cc) == 13 or len(cc) == 16):
                flash("Your VISA is Accepted!")
            else:
                flash("The card number you entered is Invalid!")
        else:
            flash("The card number you entered is Invalid!")

        return redirect("/credit")


# Route to recover users forgotten password
@app.route("/forgot", methods =["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")
    else:
        email = request.form.get("email")
        # Ensures user enters email address
        if not email:
            return apology("please enter valid email address", 400)
        # Query database for the provided email
        user = db.execute("SELECT * from users WHERE email = ?", email)
        # Ensures that the email exists
        if len(user) != 1:
            return apology("email address does not exist", 400)

        user_email = user[0]["email"]
        username = user[0]["username"]

        # Generate new random password for user
        characters = ascii_letters + digits
        tmp_password = ''.join(choice(characters) for i in range(12))
        hashed_tmp = generate_password_hash(tmp_password)

        # Update database with new password
        db.execute("UPDATE users SET hash = ? WHERE email = ?", hashed_tmp, email)

        # Initialize mailer information
        msg = Message( "Hello", sender = mail_email, recipients = [user_email])
        # Create mailer body
        msg.body = f"Hello {username},\n\nWe will provide you with a temporary password. Please update your password as soon as possible using the Change passowrd tab in Settings. Here is your temporary password below: \n\n{tmp_password}"
        # Send mail to user
        mail.send(msg)

        return redirect("/login")
    