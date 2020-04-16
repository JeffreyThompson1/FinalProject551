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

        return render_template("index.html", login=login, user=session["user"])
    
@app.route("/status", methods=["POST"])
def status():
    #Change User Status
    db.execute("UPDATE users SET status = :status WHERE username = :user", {"status": request.form.get("status"), "user": session.get("user")})
    db.commit()
    return render_template("index.html", login=login, user=session["user"])

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
   
#We Can Modify this code to search for events in the database
@app.route("/search", methods=["POST"])
def search():
    genre = "%" + request.form.get("genre") + "%"
    title = "%" + request.form.get("title") + "%"
    radius = "%" + request.form.get("radius") + "%"
    items = db.execute("SELECT * FROM events WHERE genre LIKE :genre AND title LIKE :title AND radius LIKE :radius ", {"radius": genre, "title": title, "author": radius}).fetchall()
    return render_template("search.html", user=session["user"], items=items)   

@app.route("/book/<string:code>", methods=["GET", "POST"])
def book(code):
    fullcode = code.zfill(10)
    print(fullcode)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9LYdPW0XgC6gZkiQV8Aevg", "isbns": fullcode})
    data = res.json()["books"]
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": code}).fetchall()
    revs = db.execute("SELECT rating, opinion, username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :isbn", {"isbn": code})    
    if len(book) == 0:
        return render_template("error.html", message="No Book Selected Somehow")
    return render_template("book.html", user=session["user"], book=book, data=data, revs=revs)   

@app.route("/review/<string:code>", methods=["POST"])
def review(code):
    if request.form.get("rating")=="" or request.form.get("opinion")=="":
        return render_template("error.html", message="Incomplete Review Submitted")
    match = db.execute("SELECT * FROM reviews WHERE user_id=:user AND book_id=:isbn", {"user": session.get("user_id"), "isbn": code}).fetchall() 
    if  len(match) > 0:
        db.execute("UPDATE reviews SET rating = :rating, opinion = :opinion WHERE book_id = :isbn AND user_id = :user", {"isbn": code, "user": session.get("user_id"), "rating": int(request.form.get("rating")), "opinion": request.form.get("opinion")})
    else:
        db.execute("INSERT INTO reviews (book_id, user_id, rating, opinion) VALUES (:isbn, :user, :rating, :opinion)", {"isbn": code, "user": session.get("user_id"), "rating": int(request.form.get("rating")), "opinion": request.form.get("opinion")})
    db.commit()
    fullcode = code.zfill(10)
    print(fullcode)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9LYdPW0XgC6gZkiQV8Aevg", "isbns": fullcode})
    data = res.json()["books"]
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": code}).fetchall()
    revs = db.execute("SELECT rating, opinion, username FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :isbn", {"isbn": code})    
    if len(book) == 0:
        return render_template("error.html", message="No Book Selected Somehow")
    return render_template("book.html", user=session["user"], book=book, data=data, revs=revs)


@app.route("/api/<string:code>")
def book_api(code):
    fullcode = code.zfill(10)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9LYdPW0XgC6gZkiQV8Aevg", "isbns": fullcode, "format": "json"})
    data = res.json()["books"]
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 1", {"isbn": code}).fetchall() 
    if len(book)==0:
        return jsonify({"error": "Invalid Book ISBN"}), 404

    for bk in book: 
        for rev in data:
            return jsonify({
                "ISBN":                 bk.isbn,
                "Title":                bk.title,
                "Author":               bk.author,
                "Year":                 bk.year,
                "Number of Ratings":    rev["work_ratings_count"],
                "Average Rating":       rev["average_rating"]
        })


if __name__ == "__main__":
    index()
