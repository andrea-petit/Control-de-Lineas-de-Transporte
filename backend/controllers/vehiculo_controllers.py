from models.models import Vehiculo
from models.models import LineaTransporte
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db

def listar_vehiculos():
    return Vehiculo.query.all()

def listar_vehiculos_por_linea(id_linea):
    return Vehiculo.query.filter_by(id_linea=id_linea).all()

def listar_vehiculos_por_municipio(id_municipio):
    return Vehiculo.query.join(Vehiculo.linea).filter_by(id_municipio=id_municipio).all()

def obtener_vehiculo(id_vehiculo):
    return Vehiculo.query.get(id_vehiculo)

def crear_vehiculo(placa, marca, modelo, capacidad, litraje, sindicato, modalidad, grupo, linea_id, combustible):
    if Vehiculo.query.filter_by(placa=placa).first():
        raise ValueError("Ya existe un vehículo con esa placa")
    
    nuevo = Vehiculo(placa=placa, marca=marca, modelo=modelo, capacidad=capacidad, litraje=litraje, sindicato=sindicato, modalidad=modalidad, grupo=grupo, linea_id=linea_id, combustible=combustible)
    db.session.add(nuevo)
    LineaTransporte.query.get(linea_id).cantidad_vehiculos += 1

    user_id = get_jwt_identity() #me quede aquì, aqui va el log


    db.session.commit()
    return nuevo

def editar_vehiculo(id_vehiculo, campo, valor):
    vehiculo = Vehiculo.query.get(id_vehiculo)
    if not vehiculo:
        raise ValueError("Vehículo no encontrado")
    
    setattr(vehiculo, campo, valor)
    
    db.session.commit()
    return vehiculo

def eliminar_vehiculo(id_vehiculo):
    vehiculo = Vehiculo.query.get(id_vehiculo)
    if not vehiculo:
        raise ValueError("Vehículo no encontrado")
    
    db.session.delete(vehiculo)
    db.session.commit()




