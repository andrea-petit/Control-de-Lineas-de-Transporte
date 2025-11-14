from werkzeug.security import generate_password_hash, check_password_hash
from models.models import Usuario
from models.models import otp_recovery
from config import db
from controllers.mail_utils import enviar_OTP
from datetime import datetime, timedelta

def crear_usuario(id, nombre, email, password, rol='usuario'):
    if Usuario.query.filter_by(email=email).first():
        raise ValueError("Email ya registrado")
    hashed = generate_password_hash(password)
    u = Usuario(id_usuario= id, nombre=nombre, email=email, password=hashed, rol=rol)
    db.session.add(u)
    db.session.commit()
    return u

def listar_usuarios():
    return Usuario.query.all()

def obtener_usuario(id_usuario):
    return Usuario.query.get(id_usuario)

def editar_usuario(id_usuario, campo, valor):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        raise ValueError("Línea no encontrada")
    
    setattr(usuario, campo, valor)
    
    db.session.commit()
    return usuario

def eliminar_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        raise ValueError("Línea no encontrada")

    db.session.delete(usuario)
    db.session.commit()
    return True

def verificar_login(id_usuario, password):
    u = Usuario.query.filter(Usuario.id_usuario == id_usuario).first()
    if not u:
        return None
    if check_password_hash(u.password, password):
        return u
    return None

def verificar_email(id_usuario):
    u= Usuario.query.filter(Usuario.id_usuario == id_usuario).first()
    email= u.email
    nombre= u.nombre
    otp= enviar_OTP(email, nombre)

    expira = datetime.utcnow() + timedelta(minutes=5)

    registro = otp_recovery.query.get(id_usuario)
    
    egistro = otp_recovery.query.get(id_usuario)

    if registro:
        registro.otp = otp
        registro.expira = expira
    else:
        registro = otp_recovery(
            id_usuario=id_usuario,
            otp=otp,
            expira=expira
        )
        db.session.add(registro)

    db.session.commit()

    return {
        "message": "OTP enviado al correo",
        "expira": expira
    }, None

def verificar_otp(id_usuario, otp):
    registro = otp_recovery.query.get(id_usuario)
    

    if not registro:
        return None, "No se ha generado un OTP para este usuario"

    if registro.otp != int(otp):
        return None, "OTP incorrecto"

    if datetime.utcnow() > registro.expira:
        return None, "OTP expirado"

    return {"message": "OTP correcto"}, None

def resetear_password(id_usuario, new_password):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return None, "Usuario no encontrado"

    usuario.password = generate_password_hash(new_password)
    db.session.commit()

    otp_recovery.query.filter_by(id_usuario=id_usuario).delete()
    db.session.commit()

    return {"message": "Contraseña actualizada correctamente"}, None