from models.models import LineaTransporte
from models.models import CambioLog
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db

def listar_lineas():
    return LineaTransporte.query.all()

def obtener_linea(id_linea):
    return LineaTransporte.query.get(id_linea)

def crear_linea(nombre_organizacion, nombre_propietario, cedula_propietario, id_municipio):
    if LineaTransporte.query.filter_by(nombre_organizacion=nombre_organizacion).first():
        raise ValueError("Ya existe una línea con ese nombre")
    
    nueva = LineaTransporte(nombre_organizacion=nombre_organizacion, nombre_propietario=nombre_propietario, cedula_propietario=cedula_propietario, id_municipio=id_municipio)
    db.session.add(nueva)

    user_id = get_jwt_identity()
    log = CambioLog(
        entidad="LineaTransporte",
        id_entidad=nueva.id,
        accion="CREAR",
        usuario_id=user_id
    )
    db.session.commit()
    return nueva

def editar_linea(id_linea, campo, valor):
    linea = LineaTransporte.query.get(id_linea)
    if not linea:
        raise ValueError("Línea no encontrada")
    
    setattr(linea, campo, valor)

    
    db.session.commit()
    return linea

def eliminar_linea(id_linea):
    linea = LineaTransporte.query.get(id_linea)
    if not linea:
        raise ValueError("Línea no encontrada")
    
    db.session.delete(linea)
    db.session.commit()
