import tempfile
import os
from flask import Flask, send_file, request
import pandas as pd
from sqlalchemy import create_engine, MetaData
import json
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import psycopg2
from openpyxl import *
from src.bot import Database, db
from src.bot.database import Session
from src.bot.database.dbapi import DatabaseConnector
from src.bot.database.models import *
from src.bot.database.models import Borrow


app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello!</h1>'


@app.route("/download/<book_id>")
def download_book_stats(book_id):
    session = Session(db)
    q = session.query(Borrow.borrow_id, Borrow.book_id, Borrow.date_start,Borrow.date_end).filter(Borrow.book_id == book_id)
    dict = {}
    dict['borrow_id'] = []
    dict['book_id'] = []
    dict['date_start'] = []
    dict['date_end'] = []
    for s in q:
        dict['borrow_id'].append(s.borrow_id)
        dict['book_id'].append(s.book_id)
        dict['date_start'].append(s.date_start)
        dict['date_end'].append(s.date_end)
        print(dict)
    data = pd.DataFrame(dict)

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filepath = tmp.name +'.xlsx'
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        data.to_excel(writer, sheet_name="stats")
        writer._save()

    return send_file(
        filepath,
        as_attachment=True,
    )

if __name__ == "__main__":
    app.run("0.0.0.0")
