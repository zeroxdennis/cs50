import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
#    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Get user_id
    user_id = session["user_id"]

    # Get symbol, name, sum of shares, price and price of all shares of ticker from transactions db
    portfolio = db.execute(
        "SELECT symbol, name, SUM(shares) AS totalshares, price, SUM(shares)*price as priceofallshares FROM transactions WHERE user_id=? GROUP BY symbol", user_id)

    # Get current cash from users db
    cash = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0]["cash"]

    # Calculate TOTAL
    total = cash
    for stock in portfolio:
        total += stock["price"] * stock["totalshares"]

    return render_template("index.html", portfolio=portfolio, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "GET":
        return render_template("buy.html")
    else:
        # Get ticker from html form
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Enter stock ticker")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Enter a number of shares please")

        if shares <= 0:
            return apology("Low number of shares")

        stock = lookup(symbol.upper())

        # Check if ticker exists
        if not stock:
            return apology("Stock ticker doesn't exist")

        user_id = session["user_id"]
        user_cash = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0]["cash"]

        transaction_value = shares * stock["price"]

        if user_cash < transaction_value:
            return apology("Not enough money to buy stock")
        else:
            uptd_cash = user_cash - transaction_value
            db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)
            db.execute("INSERT INTO transactions (user_id, name, symbol, shares, price, type) VALUES (?, ?, ?, ?, ?, ?)",
                       user_id, stock["name"], stock["symbol"], shares, stock["price"], "buy")

        flash("Cryptocurrency has been purchased!")

        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user_id = session["user_id"]
    transactions = db.execute("SELECT type, symbol, shares, price, time FROM transactions WHERE user_id = ?", user_id)

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Enter stock ticker")

        ticker = lookup(symbol.upper())

        if ticker == None:
           return apology("Stock ticker doesn't exist quote func")

        return render_template("quoted.html", ticker=ticker)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Username is required")

        elif not password:
            return apology("Password is required")

        elif not confirmation:
            return apology("Confirm your password")

        elif password != confirmation:
            return apology("Passwords don't match")

        elif len(password) < 15:    
            return apology("Password is too short")

        hash = generate_password_hash(password)

        # Try/except, when except means that username is taken
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return apology("Username is already taken")

        session["user_id"] = new_user

        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "GET":

        tickers = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("sell.html", tickers=[row["symbol"] for row in tickers])

    else:
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        if not symbol:
            return apology("Enter stock ticker")

        stock = lookup(symbol.upper())
        stock_price = stock["price"]
        stock_ticker = stock["name"]

        if stock_ticker == None:
            return apology("Symbol doesn't exist")

        if shares <= 0:
            return apology("Enter a positive number of shares please")

        user_shares_owned = db.execute(
            "SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)[0]["shares"]

        if shares > user_shares_owned:
            return apology("Not enough stock")

        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        # Update cash in users db after stock sell
        transaction_value = shares * stock_price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + transaction_value, user_id)

        db.execute("INSERT INTO transactions (user_id, symbol, name, shares, price, type) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, stock["symbol"], stock["name"], -shares, stock["price"], "sell")

        flash("Cryptocurrency has been sold")

        return redirect("/")


@app.route("/add_money", methods=["GET", "POST"])
@login_required
def add_money():
    """Addition of money"""

    if request.method == "GET":
        return render_template("addition.html")
    else:
        user_id = session["user_id"]

        new_cash = int(request.form.get("new_money"))

        if new_cash <= 0:
            return apology("Enter positive integer please")

        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        db.execute("UPDATE users SET cash = ? WHERE id = ?", user_cash + new_cash, user_id)

        flash("Cash has been added to your account")

        return redirect("/")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    if request.method == "GET":
        return render_template("changepassword.html")
    else:
        user_id = session["user_id"]
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        current_hash = db.execute("SELECT hash FROM users where id = ?", user_id)[0]["hash"]
        print(current_hash)
        check_password_hash(current_hash, old_password)

        if check_password_hash(current_hash, old_password) == False:
            return apology("Current password is wrong")

        elif not confirmation:
            return apology("Confirm your password")

        elif new_password != confirmation:
            return apology("New passwords don't match")

        hash = generate_password_hash(new_password)

        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, user_id)

        flash("Your password has successfully been changed")

        return redirect("/")

