from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize DB + Migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from .auth import auth_bp
    from .routes import main

    app.register_blueprint(auth_bp)
    app.register_blueprint(main)

    return app
