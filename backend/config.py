from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:31091420@localhost:5432/controldelineas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "clave-secreta"
