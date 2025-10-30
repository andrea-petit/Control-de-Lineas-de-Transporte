from models.models import Vehiculo
from models.models import LineaTransporte
from config import db
from controllers.log_utils import registrar_cambio

def listar_vehiculos():
    return Vehiculo.query.all()

def listar_vehiculos_por_linea(id_linea):
    return Vehiculo.query.filter_by(linea_id=id_linea).all()

def listar_vehiculos_por_municipio(id_municipio):
    return Vehiculo.query.join(Vehiculo.linea).filter_by(id_municipio=id_municipio).all()

def obtener_vehiculo(id_vehiculo):
    return Vehiculo.query.get(id_vehiculo)

def crear_vehiculo(placa, marca, modelo, capacidad, litraje, sindicato, modalidad, grupo, linea_id, combustible, usuario_id=None, descripcion=None):
    if Vehiculo.query.filter_by(placa=placa).first():
        raise ValueError("Ya existe un vehículo con esa placa")
    
    linea = LineaTransporte.query.get(linea_id)
    if not linea:
        raise ValueError("Línea de transporte no encontrada")

    nuevo = Vehiculo(
        placa=placa, marca=marca, modelo=modelo, capacidad=capacidad,
        litraje=litraje, sindicato=sindicato, modalidad=modalidad,
        grupo=grupo, linea_id=linea_id, combustible=combustible
    )

    db.session.add(nuevo)

    db.session.flush()

    linea.cantidad_vehiculos = (linea.cantidad_vehiculos or 0) + 1

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='crear',
        nombre_entidad=f'Vehículo {placa} {marca} {modelo}',
        tabla='vehiculos',
        campo=None,
        descripcion= descripcion or 'Creación de nuevo vehículo'
    )

    db.session.commit()
    return nuevo

def editar_vehiculo(id_vehiculo, campo, valor, descripcion=None, usuario_id=None):
    vehiculo = Vehiculo.query.get(id_vehiculo)
    if not vehiculo:
        raise ValueError("Vehículo no encontrado")

    previo = getattr(vehiculo, campo, None)
    setattr(vehiculo, campo, valor)

    marca = getattr(vehiculo, 'marca', None)
    modelo = getattr(vehiculo, 'modelo', None)
    placa = getattr(vehiculo, 'placa', None)

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='editar',
        nombre_entidad=f'Vehículo {placa} {marca} {modelo}',
        tabla='vehiculos',
        campo=campo,
        descripcion= descripcion or f'Actualizó {campo} de {previo} a {valor}'
    )

    db.session.commit()
    return vehiculo

def eliminar_vehiculo(id_vehiculo, descripcion=None, usuario_id=None):
    vehiculo = Vehiculo.query.get(id_vehiculo)
    if not vehiculo:
        raise ValueError("Vehículo no encontrado")

    placa = getattr(vehiculo, 'placa', None)
    marca = getattr(vehiculo, 'marca', None)
    modelo = getattr(vehiculo, 'modelo', None)

    try:
        linea = LineaTransporte.query.get(getattr(vehiculo, 'linea_id', None))
        if linea and (linea.cantidad_vehiculos or 0) > 0:
            linea.cantidad_vehiculos = (linea.cantidad_vehiculos or 0) - 1
    except Exception:
        pass

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='eliminar',
        nombre_entidad=f'Vehículo {placa} {marca} {modelo}',
        tabla='vehiculos',
        campo=None,
        descripcion= descripcion or 'Eliminación de vehículo'
    )

    db.session.delete(vehiculo)
    db.session.commit()
    return True




