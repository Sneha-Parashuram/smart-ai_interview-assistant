import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security key (used for sessions if needed)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SMART_INTERVIEW_SECRET'

    # SQLite database (local, simple, perfect for mini project)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # (Optional) If you ever use session storage
    SESSION_TYPE = 'filesystem'
