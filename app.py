import os

from flask import Flask

from books import book_bp
from members import member_bp
from loans import loan_bp
from reports import report_bp
from db import init_db


app = Flask(__name__)

app.register_blueprint(book_bp)
app.register_blueprint(member_bp)
app.register_blueprint(loan_bp)
app.register_blueprint(report_bp)


if not os.path.exists("library.db"):
    init_db()