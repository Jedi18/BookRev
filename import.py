import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://postgres:password@localhost:5432/postgres")
db = scoped_session(sessionmaker(bind=engine))

#db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, isbn VARCHAR(50) NOT NULL, title VARCHAR(50) NOT NULL, author VARCHAR(50) NOT NULL, year INTEGER)")

with open("books.csv", "rb")  as file:
    book_reader = csv.DictReader(file)

    for book in book_reader:
        # add to db
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES(:isbn, :title, :author, :year)", {"isbn":book["isbn"], "title":book["title"], "author":book["author"], "year":book["year"]})
        db.commit()
