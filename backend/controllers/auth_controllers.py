from werkzeug.security import generate_password_hash, check_password_hash
from models.models import Usuario
from config import db

def crear_usuario(id, nombre, email, password, rol='usuario'):
    if Usuario.query.filter_by(email=email).first():
        raise ValueError("Email ya registrado")
    hashed = generate_password_hash(password)
    u = Usuario(id_usuario= id, nombre=nombre, email=email, password=hashed, rol=rol)
    db.session.add(u)
    db.session.commit()
    return u

def verificar_login(id_usuario, password):
    u = Usuario.query.filter(Usuario.id_usuario == id_usuario).first()
    if not u:
        return None
    if check_password_hash(u.password, password):
        return u
    return None

