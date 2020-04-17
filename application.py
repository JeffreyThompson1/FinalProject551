import os
import requests
import json

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

""" #testing serializing
class User:
   def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns} """

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #Checks if User Has Logged In
        if session.get("user") is None:
            session["user"] = ""
        login = True
        if session.get("user") == "":
            login = False
        if session.get("status") is None:
            session["status"] = ""
        if session.get("gametype") is None:
            session["gametype"] = ""
        reply1 = db.execute("SELECT * FROM events LIMIT 0").fetchall()
        events = json.dumps([(dict(row.items())) for row in reply1])
        reply2 = db.execute("SELECT * FROM locations").fetchall()
        locale = json.dumps([(dict(row.items())) for row in reply2])
        return render_template("index.html", login=login, user=session["user"], location="", status=session["status"], gametype=session["gametype"], lat=0, lon=0, rad=0, events=events, locale=locale)
    
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
    db.commit()
    session["status"] = stat
    gametype = request.form.get("gametype")
    session["gametype"] = gametype
    reply1 = db.execute("SELECT * FROM events LIMIT 0").fetchall()
    events = json.dumps([(dict(row.items())) for row in reply1])
    reply2 = db.execute("SELECT * FROM locations").fetchall()
    locale = json.dumps([(dict(row.items())) for row in reply2])
    return render_template("index.html", login=login, user=session["user"], status=session["status"], gametype=session["gametype"], lat=0, lon=0, rad=0, events=events, locale=locale)

#We Can Modify this code to search for events in the database
@app.route("/search", methods=["POST"])
def search():
    genre = "%" + request.form.get("genre") + "%"
    title = "%" + request.form.get("title") + "%"
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    radius = request.form.get("radius")
    if lat == "0" or lon == "0" or radius is None:
        return render_template("error.html", message="Please Fill In All Required Fields.")
    if request.form.get("genre") == "" and request.form.get("title") == "":
        reply1 = db.execute("SELECT * FROM events").fetchall()
        events = json.dumps([(dict(row.items())) for row in reply1])
    elif request.form.get("genre") == "":
        reply1 = db.execute("SELECT * FROM events WHERE title LIKE :title", {"title": title}).fetchall()
        events = json.dumps([(dict(row.items())) for row in reply1])
    elif request.form.get("title") == "":
        reply1 = db.execute("SELECT * FROM events WHERE genre LIKE :genre", {"genre": genre}).fetchall()
        events = json.dumps([(dict(row.items())) for row in reply1])   
    else:
        reply1 = db.execute("SELECT * FROM events WHERE title LIKE :title OR genre LIKE :genre", {"title": title, "genre": genre}).fetchall()
        events = json.dumps([(dict(row.items())) for row in reply1])
    reply2 = db.execute("SELECT * FROM locations").fetchall()
    locale = json.dumps([(dict(row.items())) for row in reply2])
    return render_template("index.html", login=True, user=session["user"], status=session["status"], gametype=session["gametype"], lat=lat, lon=lon, rad=radius, events=events, locale=locale)   


@app.route("/create", methods=["POST"])
def create():
    user = session.get("user")
    name = request.form.get("name")
    genre = request.form.get("genre")
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    cap = request.form.get("capacity")
    public = request.form.get("locationprivacy")
    gametype = session["gametype"]
    if name == "" or lat == "0" or lon == "0" or public == "":
        return render_template("error.html", message="Please Fill In All Required Fields.")
    db.execute("INSERT INTO events (title, genre, lat, long, capacity, privacy, gametype, creator) VALUES (:title, :genre, :lat, :lon, :cap, :public, :gametype, :user)", {"title": name, "genre": genre, "lat": lat, "lon": lon, "cap": cap, "public": public, "gametype": gametype, "user": session["user"]})
    db.commit()
    reply1 = db.execute("SELECT * FROM events LIMIT 0").fetchall()
    events = json.dumps([(dict(row.items())) for row in reply1])
    reply2 = db.execute("SELECT * FROM locations").fetchall()
    locale = json.dumps([(dict(row.items())) for row in reply2])
    return render_template("index.html", login=True, user=user, status=session["status"], gametype=session["gametype"], lat=lat, lon=lon, rad=0, events=events, locale=locale)

if __name__ == "__main__":
    index()
