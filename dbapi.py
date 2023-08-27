from datetime import datetime, date
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, DateTime, func, null
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from src.bot.database.models import *


class DatabaseConnector():

    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connection(self):
        engine = create_engine(f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}")
        connection = engine.connect()
        Session = sessionmaker(bind=connection)
        return Session()

    def add(self, dict):
        try:
            session = self.connection()
            book = Book()
            book.title = dict['title']
            book.author = dict['author']
            book.published = dict['published']
            book.date_added = date.today()
            session.add(book)
            session.commit()
            id = session.query(func.max(Book.book_id)).scalar()
            return id
        except Exception:
            return False

    def delete(self, dict):
        try:
            session = self.connection()
            q = session.query(Book.book_id, Book.date_deleted).filter(Book.title == dict['title']).filter(Book.author == dict['author']).filter(Book.published == dict['published'])
            book_id = q.scalar()
            date_deleted = q.first()[1]
            if q.count() > 0 and date_deleted == None:
                q2 = session.query(Borrow).filter(Borrow.book_id == book_id).filter(Borrow.date_end == None)
                if q2.count() > 0:
                    return False
                else:
                    book = session.query(Book).filter(Book.book_id == book_id).one()
                    book.date_deleted = date.today()
                    session.commit()
                    return True
            else:
                return False
        except Exception:
            return False

    def list_books(self):
        session = self.connection()
        book_list = []
        q = session.query(Book)
        for s in q:
            if s.date_deleted != None:
                book_list.append([s.title, s.author, s.published, '(удалена)'])
            else:
                book_list.append([s.title, s.author, s.published])

        return book_list

    def get_book(self, dict):
        try:
            session = self.connection()
            q = session.query(Book.book_id,Book.date_deleted).filter(Book.title == dict['title']).filter(Book.author == dict['author']).filter(Book.published == dict['published'])
            if q.count() > 0 and q.first()[1] == None:
                return q.first()[0]
            else:
                return None
        except Exception:
            return None

    def borrow(self, dict, customer_id):
        try:
            session = self.connection()
            book_id = self.get_book(dict)
            if book_id != None:
                q = session.query(Borrow.borrow_id).filter(Borrow.book_id == book_id).filter(Borrow.date_end == None)
                if q.count() == 0 and self.get_borrow(customer_id) == 0:
                    borrow = Borrow()
                    borrow.book_id = book_id
                    borrow.date_start = datetime.now()
                    borrow.user_id = customer_id
                    session.add(borrow)
                    session.commit()
                    return session.query(func.max(Borrow.borrow_id)).first()[0]
                else:
                    print('Пользователь не вернул прошлую книгу или книгу взял кто-то другой')
                    return False
            else:
                print('Книга не найдена')
                return False
            q = session.query(Book).filter(Book.title == dict['title']).filter(Book.author == dict['author']).filter(Book.published == dict['published'])
            result = False
            for s in q:
                result = True
                borrow = Borrow()
                borrow.book_id = s.book_id
                borrow.date_start = datetime.now()
                borrow.user_id = dict['user_id']
                session.add(borrow)
                session.commit()
                q2 = session.query(func.max(Borrow.borrow_id))
                for s2 in q2:
                    id = s2[0]
                return id
            return result
        except Exception:
            return False

    def get_borrow(self, user_id):
        try:
            session = self.connection()
            q = session.query(Borrow.borrow_id).filter(Borrow.user_id == user_id).filter(Borrow.date_end == None)
            if (q.count()) == 1:
                return q.first()[0]
            else:
                return 0
        except Exception:
            return 0

    def retrieve(self, user_id):
        try:
            session = self.connection()
            borrow_id = self.get_borrow(user_id)
            if borrow_id > 0:
                q = session.query(Borrow).filter(Borrow.borrow_id == borrow_id)
                for s in q:
                    s.date_end = datetime.now()
                    session.commit()
                    print('Книга успешно возвращена')
                    return True
            else:
                print('У вас нет взятых книг')
                return False
        except Exception:
            return False
