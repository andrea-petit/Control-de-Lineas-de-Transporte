from config import db
from models.models import Vehiculo, LineaTransporte
from controllers.log_utils import registrar_cambio
from sqlalchemy.orm import joinedload

def _chofer_dict_from_vehiculo(v):

    if hasattr(v, "chofer") and getattr(v, "chofer") is not None:
        ch = getattr(v, "chofer")
        return {
            "id_chofer": getattr(ch, "id_chofer", None) or getattr(ch, "id", None),
            "nombre": getattr(ch, "nombre", None),
            "cedula": getattr(ch, "cedula", None)
        }
    if hasattr(v, "choferes"):
        chs = getattr(v, "choferes") or []
        if isinstance(chs, (list, tuple)) and len(chs) > 0:
            ch = chs[0]
            return {
                "id_chofer": getattr(ch, "id_chofer", None) or getattr(ch, "id", None),
                "nombre": getattr(ch, "nombre", None),
                "cedula": getattr(ch, "cedula", None)
            }
    return None

def _serialize_vehiculo(v):
    linea_obj = getattr(v, "linea", None)
    return {
        "id_vehiculo": getattr(v, "id_vehiculo", None) or getattr(v, "id", None),
        "placa": getattr(v, "placa", None),
        "marca": getattr(v, "marca", None),
        "modelo": getattr(v, "modelo", None),
        "nombre_propietario": getattr(v, "nombre_propietario", None),
        "cedula_propietario": getattr(v, "cedula_propietario", None),
        "capacidad": getattr(v, "capacidad", None),
        "litraje": getattr(v, "litraje", None),
        "sindicato": getattr(v, "sindicato", None),
        "modalidad": getattr(v, "modalidad", None),
        "grupo": getattr(v, "grupo", None),
        "estado": getattr(v, "estado", None),
        "combustible": getattr(v, "combustible", None),
        "linea_id": getattr(v, "linea_id", None) or (getattr(linea_obj, "id_linea", None) if linea_obj else None),
        "linea_nombre_organizacion": getattr(linea_obj, "nombre_organizacion", None) if linea_obj else None,
        "chofer": _chofer_dict_from_vehiculo(v)
    }


def listar_vehiculos_con_linea_y_chofer():

    options = []
    if hasattr(Vehiculo, "linea"):
        options.append(joinedload(getattr(Vehiculo, "linea")))
    for rel in ("chofer", "choferes"):
        if hasattr(Vehiculo, rel):
            options.append(joinedload(getattr(Vehiculo, rel)))
            break

    query = db.session.query(Vehiculo).options(*options)
    vehiculos = query.all()
    return [_serialize_vehiculo(v) for v in vehiculos]


def listar_vehiculos_por_linea(id_linea):
    options = []
    if hasattr(Vehiculo, "linea"):
        options.append(joinedload(getattr(Vehiculo, "linea")))
    for rel in ("chofer", "choferes"):
        if hasattr(Vehiculo, rel):
            options.append(joinedload(getattr(Vehiculo, rel)))
            break
    vehiculos = db.session.query(Vehiculo).filter(Vehiculo.linea_id == id_linea).options(*options).all()
    return [_serialize_vehiculo(v) for v in vehiculos]


def obtener_vehiculo(id_vehiculo):
    options = []
    if hasattr(Vehiculo, "linea"):
        options.append(joinedload(getattr(Vehiculo, "linea")))
    for rel in ("chofer", "choferes"):
        if hasattr(Vehiculo, rel):
            options.append(joinedload(getattr(Vehiculo, rel)))
            break
    v = db.session.query(Vehiculo).options(*options).get(id_vehiculo)
    if not v:
        return None
    return _serialize_vehiculo(v)


def listar_vehiculos_por_municipio(id_municipio):
    return Vehiculo.query.join(Vehiculo.linea).filter_by(id_municipio=id_municipio).all()

def crear_vehiculo(placa, marca, modelo, nombre_propietario, cedula_propietario, capacidad, litraje, sindicato, modalidad, grupo, linea_id, combustible, usuario_id=None, descripcion=None):
    if Vehiculo.query.filter_by(placa=placa).first():
        raise ValueError("Ya existe un vehículo con esa placa")
    
    linea = LineaTransporte.query.get(linea_id)
    if not linea:
        raise ValueError("Línea de transporte no encontrada")

    nuevo = Vehiculo(
        placa=placa, marca=marca, modelo=modelo, nombre_propietario= nombre_propietario, cedula_propietario=cedula_propietario, 
        capacidad=capacidad, litraje=litraje, sindicato=sindicato, modalidad=modalidad,
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

def buscar_vehiculos_por_placa(placa_parcial):
    vehiculos = Vehiculo.query.filter(Vehiculo.placa.ilike(f"%{placa_parcial}%")).all()
    return [_serialize_vehiculo(v) for v in vehiculos]

