import os

from flask import Flask, session, render_template, request
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
    return "Project 1: TODO"

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
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        #verify
        user_name = request.form.get("username")
        passsword = request.form.get("password")
        #do stuff
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
