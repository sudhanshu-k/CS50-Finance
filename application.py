import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import json

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")

symb = 0
rows = 0

@app.route("/")
@login_required
def index():
    stocks = db.execute("SELECT * FROM stock WHERE username = :username", username = rows[0]["username"])
    return render_template("index.html", stocks= json.dumps(stocks), num= len(stocks))



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    cash = rows[0]["cash"]
    if request.method == "POST":
        toGet = request.form.get("symbol")
        if toGet != None:
            global symb
            symb = toGet
        unit = request.form.get("quantity")
        if not toGet and not unit:
            return render_template("buy.html", error = 'Empty Field.')
        elif toGet:
            return render_template("buy.html", toGet = lookup(toGet), cash = cash, symbol = toGet)
        elif unit:
                x = lookup(symb)
                if float(x["price"])*float(unit) > cash:
                    return render_template("buy.html", error = 'Transaction amount greater than cash.')
                else:
                    db.execute("INSERT INTO stock (username, symbol, units, date, price) VALUES (:x, :y, :z, CURRENT_TIMESTAMP, :b)", x= rows[0]["username"], y=symb, z=unit, b= x["price"])
                    db.execute("UPDATE users SET cash = :x WHERE username = :y",x = (float(cash) - float(x["price"])*float(unit)), y = rows[0]["username"])
                    return render_template("buy.html", error = 'succesful')
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")

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
        global rows
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/sell")

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
    toGet = request.form.get("symbol")
    if request.method == "POST":
        if not toGet:
            return render_template("quote.html", error = "Symbol Field Is Blank")
        else:
            return render_template("quote.html", toGet = lookup(toGet))
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    user = request.form.get("username")
    passo = request.form.get("password")
    passc = request.form.get("confirm password")

    rows = db.execute("SELECT * FROM users WHERE username = :username", username=user)

    if request.method == "POST":
        if len(rows) != 0:
            return apology('Username Already Exist')
        elif not user:
            return apology('Must Provide Username')
        elif not passo:
            return apology('Must Provide Password')
        elif passo != passc:
            return apology("Password didn't match")
        else:
            passo = generate_password_hash(passo)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username = user, hash = passo)
            return render_template("sorry.html")
    
    else:
        return render_template("register.html")
        

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    stocks = db.execute("SELECT * FROM stock WHERE username = :username", username = rows[0]["username"])
    if request.method == "POST":
        if request.form.get("stocks"):
            stock = db.execute("SELECT * FROM stock WHERE username = :username AND symbol = :symbol", username = rows[0]["username"], symbol = request.form.get("stocks"))
            print(stock)
            unit = 0
            for i in range(len(stock)):
                unit += stock[i]["units"]
            print(unit)
            return render_template("sell.html", stocks= json.dumps(stocks), stock = json.dumps(stock), unit = unit, toGet = lookup(request.form.get("stocks")))







    else:
        return render_template("sell.html", stocks= json.dumps(stocks))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
