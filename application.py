import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

GOODREADS_API_KEY = "v3bCS9Nn5lNxbavMW3uRg"

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://postgres:password@localhost:5432/postgres")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if session.get("username") is None:
        session["logged_in"] = False
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #register
        user_name = request.form.get("username")
        password = request.form.get("password")
        db.execute("INSERT INTO users(username, pass) VALUES(:user, :pass)", {"user":user_name, "pass":password})
        db.commit()
        return render_template("register_result.html", result=True)
    else:
        # if logged in, redirect to index
        if session.get("logged_in") == True:
            return redirect(url_for("index"))
        else:
            return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username") is None:
        session["logged_in"] = False

    if request.method=="POST":
        #if already logged in, take the user to logout page
        if session["logged_in"] == True:
            return redirect(url_for("logout"))

        #verify
        user_name = request.form.get("username")
        password = request.form.get("password")
        #do stuff
        user = db.execute("SELECT * FROM users WHERE username=:user AND pass=:passw", {"user":user_name, "passw" : password}).fetchone()
        if user is None:
            return render_template("register_result.html", result=False)
        else:
            session["logged_in"] = True
            session["username"] = user_name
            session["user_id"] = user["id"]
            return render_template("register_result.html", result=True)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session["logged_in"] = False
    return "Logged out! :)"

@app.route("/test")
def test():
    booksa = db.execute("SELECT * FROM books").fetchone()
    return booksa["title"]

@app.route("/search", methods=["GET"])
def search():
    isbn = request.args.get("isbn_query")
    isbn = "%{}%".format(isbn)
    title = request.args.get("title_query")
    title = "%{}%".format(title.title())
    author = request.args.get("author_query")
    author = "%{}%".format(author.title())
    results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author LIMIT 10", {"isbn":isbn, "title":title, "author":author}).fetchall()
    return render_template("search.html", results=results)

@app.route("/books/<string:isbn>")
def books(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    if book is None:
        return render_template("book.html", found=False)

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :bookid LIMIT 10", {"bookid":book["id"]}).fetchall()

    return render_template("book.html", found=True ,book=book, reviews=reviews)

if __name__ == "__main__":
    app.run(debug=True)
