# app/models.py
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)   # <-- YOU WERE MISSING THIS!

    phone_number = db.Column(db.String(20))
    birthday = db.Column(db.String(20))

    streak = db.Column(db.Integer, default=0)
    total_answers = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    last_answered = db.Column(db.String(20))


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.String(10))

    answer = db.Column(db.Text)          # user answer
    feedback_text = db.Column(db.Text)   # final feedback from AI
    keywords = db.Column(db.String(200))

    score = db.Column(db.Float, default=0)
    sentiment = db.Column(db.Float, default=0)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
