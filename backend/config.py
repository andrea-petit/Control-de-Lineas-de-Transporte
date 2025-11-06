from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:31091420@localhost:5432/controldelineas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "clave-secreta"
    JWT_SECRET_KEY ="clave-jwt-secreta"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)
