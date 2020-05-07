
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", default="postgresql://username:password@localhost/dbname")

db = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.bind = db # fixes sqlalchemy.exc.UnboundExecutionError: Table object 'books' is not bound to an Engine or Connection.  Execution can not proceed without a database to execute against.
BoundSession = sessionmaker(bind=db)

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    author = Column(String(128))
    readers = Column(ARRAY(String(128)))

if __name__ == "__main__":

    #base.metadata.create_all(db)

    #Book.__table__.drop(db)
    #Book.__table__.create(db)

    if not Book.__table__.exists():
        Book.__table__.create(db)

    session = BoundSession()

    try:
        book = session.query(Book).filter(Book.title=="Harry Potter").one()
    except NoResultFound as err:
        book = Book(title="Harry Potter", author="JKR", readers=["John", "Jane", "Sally"])
        session.add(book)
        session.commit()

    print("-------")
    print("BOOKS:")
    books = session.query(Book)
    for book in books:
        print("...", book.id, "|", book.title, "|", book.author, "|", book.readers)

    session.close()
