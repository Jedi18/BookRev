import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

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

    if session["logged_in"] == True:
        return render_template("test.html", test="You need to log out first.")

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
            return redirect(url_for('register'))
        else:
            session["logged_in"] = True
            session["username"] = user_name
            session["user_id"] = user["id"]
            return redirect(url_for('index'))
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session["logged_in"] = False
    return redirect(url_for("index"))

@app.route("/test")
def test():
    booksa = db.execute("SELECT * FROM books").fetchone()
    return booksa["title"]

@app.route("/search", methods=["GET"])
def search():
    offset = request.args.get("page")
    next_url = request.url

    if offset is None:
        offset = 0
        next_url += '&page=1'
    else:
        offset = int(offset)
        extra = "&page={}".format(offset+1)
        next_url = next_url[:-7] + extra
        # page number * 10, so as to get correct offset for that page
        offset = int(offset) * 10

    isbn = request.args.get("isbn_query")
    isbn = "%{}%".format(isbn)
    title = request.args.get("title_query")
    title = "%{}%".format(title.title())
    author = request.args.get("author_query")
    author = "%{}%".format(author.title())
    results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn AND title LIKE :title AND author LIKE :author ORDER BY id LIMIT 10 OFFSET :offset", {"isbn":isbn, "title":title, "author":author, "offset":offset}).fetchall()
    return render_template("search.html", results=results,next_url=next_url)

@app.route("/books/<string:isbn>")
def books(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()

    if book is None:
        return render_template("book.html", found=False)

    # update book visit counter
    db.execute("UPDATE books SET visit_counter = :counter WHERE isbn = :isbn", {"counter":book["visit_counter"]+1, "isbn":isbn})
    db.commit()

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :bookid LIMIT 10", {"bookid":book["id"]}).fetchall()

    #Good reads review data
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key":GOODREADS_API_KEY, "isbns":isbn})
    goodreads = res.json()

    goodreads_data = {"avg_ratings":goodreads['books'][0]["average_rating"], "ratings_count":goodreads['books'][0]["work_ratings_count"]}

    return render_template("book.html", found=True ,book=book, reviews=reviews, goodreads_data=goodreads_data)

@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    if request.method == "POST":
        if not (session["logged_in"] == True):
            return redirect(url_for("login"))

        review = request.form.get("review")
        bookid = request.form.get("bookid")
        rating = request.form.get("rating")
        db.execute("INSERT INTO reviews(review, book_id, user_name, rating) VALUES(:review, :bookid, :username, :rating)", {"review":review, "bookid":bookid, "username":session["username"], "rating":rating})
        db.commit()
        return redirect(url_for("index"))
    else:
        if not (session["logged_in"] == True):
            return redirect(url_for("login"))
        else:
            book_id = request.args.get("bookid")
            bookidprovided = True
            if book_id is None:
                bookidprovided = False

            return render_template("review.html", book_id = book_id, bookidprovided = bookidprovided)

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()

    reviews = db.execute("SELECT rating FROM reviews WHERE book_id = :bookid",{"bookid":book["id"]}).fetchall()

    review_count = len(reviews)
    ratings = 0

    for review in reviews:
        ratings += review["rating"]

    ratings = ratings//review_count

    if book is None:
        abort(404)

    response = jsonify({"title":book["title"], "author":book["author"], "year":book["year"], "isbn":book["isbn"], "review_count":review_count,"average_score":ratings})
    response.status_code = 200
    return response

@app.route("/user")
def user():
    if not (session["logged_in"] == True):
        return redirect(url_for("login"))

    user = db.execute("SELECT * FROM users WHERE id = :id", {"id":session["user_id"]}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE user_name = :username", {"username":user['username']}).fetchall()

    return render_template("user.html", user=user, reviews=reviews)

@app.route("/author")
def author():
    name = request.args.get("name")

    if name is None:
        abort(404)

    books = db.execute("SELECT * FROM books WHERE author = :name", {"name":name}).fetchall()
    return render_template("author.html", books=books, author_name=name)

@app.route("/mostvisited/<string:type>")
def mostvisited(type):
    if type=='BOOK':
        books = db.execute("SELECT * FROM books ORDER BY visit_counter DESC LIMIT 5").fetchall()
        return render_template("mostvisited.html", type=type, books=books)
    else:
        abort(400)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/userdescription", methods=["POST"])
def userdescription():
    description = request.form.get('description')
    
    db.execute("UPDATE users SET description = :desc WHERE id = :id", {"desc":description, "id":session["user_id"]})
    db.commit()
    return jsonify({"success":True, "description":description})

if __name__ == "__main__":
    app.run(debug=True)
