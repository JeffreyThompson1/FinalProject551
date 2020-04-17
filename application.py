import os
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #Checks if User Has Logged In
        if session.get("user") is None:
            session["user"] = ""

        login = True
        if session.get("user") == "":
            login = False

        return render_template("index.html", login=login, user=session["user"], location="")
    
@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username") == "" or request.form.get("password") == "":
        return render_template("error.html", message="Please Fill In All Required Fields.")
    elif db.execute("SELECT * FROM users WHERE username=:user AND password=:pwrd", {"user": request.form.get("username"), "pwrd": request.form.get("password")}).rowcount == 0:
        return render_template("error.html", message="Username and Password do not Match.")
    else:
        session["user"] = request.form.get("username")
        res = db.execute("SELECT id FROM users WHERE username=:user AND password=:pwrd LIMIT 1", {"user": request.form.get("username"), "pwrd": request.form.get("password")}).fetchall()
        for val in res:
            session["user_id"] = val.id
        login = True
        return render_template("index.html", login=login, user=session["user"])

@app.route("/register", methods=["POST"])
def register():
    if request.form.get("email") == "" or request.form.get("username") == "" or request.form.get("password") == "" or request.form.get("confirm") == "":
        return render_template("error.html", message="Please Fill In All Required Fields.")
    elif db.execute("SELECT * FROM users WHERE username=:user", {"user": request.form.get("username")}).rowcount > 0:
        return render_template("error.html", message="Username Already Exists")
    elif not request.form.get("password") == request.form.get("confirm"):
        return render_template("error.html", message="Password does not match Password Confirmation.")
    else:
        db.execute("INSERT INTO users (email, username, password, status) VALUES (:email, :user, :pwrd, :stat)", {"email": request.form.get("email"), "user": request.form.get("username"), "pwrd": request.form.get("password"), "stat": ""})
        db.commit()
        session["user"] = request.form.get("username")
        session["user_id"] = db.execute("SELECT id FROM users WHERE username=:user AND password=:pwrd LIMIT 1", {"user": request.form.get("username"), "pwrd": request.form.get("password")}).fetchall()
        login = True
        return render_template("index.html", login=login, user=session["user"])

@app.route("/logout", methods=["POST"])
def logout():
    session["user"] = ""
    session["user_id"] = ""
    login = False
    return render_template("index.html", login=login, user=session["user"])

#Change User Status
@app.route("/status", methods=["POST"])
def status():
    stat = request.form.get("status")
    db.execute("UPDATE users SET status = :status WHERE username = :user", {"status": stat, "user": session.get("user")})
    session["status"] = stat  
    host = False
    player = False
    if stat == "host" or stat == "both":
        host = True
    if stat == "player" or stat == "both":
        player = True
    db.commit()
    gametype = True
    if request.form.get("gametype")=="0":
        gametype = True
    else:
        gametype = False
    session["gametype"] = gametype
    return render_template("index.html", login=login, user=session["user"], host=host, player=player, location="", gametype=session["gametype"])

#We Can Modify this code to search for events in the database
@app.route("/search", methods=["POST"])
def search():
    user = session.get("user")
    stat = session["status"]
    genre = request.form.get("genre")
    title = request.form.get("title")
    radius = request.form.get("radius")
    address = request.form.get("address")
    radius = request.form.get("radius")
    host = False
    player = False
    if stat == "host" or stat == "both":
        host = True
    if stat == "player" or stat == "both":
        player = True
    return render_template("index.html", login=True, user=user, radius=radius, host=host, player=player, location="", gametype=session["gametype"])   

if __name__ == "__main__":
    index()
