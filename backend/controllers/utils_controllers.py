from models.models import municicipio
from config import db

def obtener_municipios():
    return municicipio.query.all()

