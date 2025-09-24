import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Default to SQLite for quick start; override with MySQL via env vars
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Flask-Login
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days

class ProdConfig(Config):
    DEBUG = False

class DevConfig(Config):
    DEBUG = True
