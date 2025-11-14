from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import timedelta

db = SQLAlchemy()
mail= Mail()

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:31091420@localhost:5432/controldelineas"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "clave-secreta"
    JWT_SECRET_KEY ="clave-jwt-secreta"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT= 587
    MAIL_USERNAME= "optcontroldelineas@gmail.com"
    MAIL_PASSWORD= "oqsq taig kkzw npsx"
    MAIL_USE_TLS= True
    MAIL_USE_SSL= False
    MAIL_DEFAULT_SENDER = "optcontroldelineas@gmail.com"