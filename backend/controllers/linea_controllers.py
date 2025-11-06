from models.models import LineaTransporte
from controllers.log_utils import registrar_cambio
from config import db

def listar_lineas():
    return LineaTransporte.query.all()

def obtener_linea(id_linea):
    return LineaTransporte.query.get(id_linea)

def obtener_linea_por_municipio(id_municipio):
    return LineaTransporte.query.filter_by(id_municipio=id_municipio).all()

def crear_linea(nombre_organizacion, id_municipio, id_usuario):
    if LineaTransporte.query.filter_by(nombre_organizacion=nombre_organizacion).first():
        raise ValueError("Ya existe una línea con ese nombre")
    
    nueva = LineaTransporte(nombre_organizacion=nombre_organizacion, id_municipio=id_municipio)
    db.session.add(nueva)

    registrar_cambio(
        usuario_id=id_usuario,
        tipo_cambio='crear',
        nombre_entidad=f'Línea {nombre_organizacion}',
        tabla='lineas_transporte',
        campo=None,
        descripcion='Creación de nueva línea de transporte'
    )

    db.session.commit()
    return nueva

def editar_linea(id_linea, campo, valor, id_usuario, descripcion):
    linea = LineaTransporte.query.get(id_linea)
    if not linea:
        raise ValueError("Línea no encontrada")
    
    setattr(linea, campo, valor)

    nombre_organizacion = getattr(linea, 'nombre_organizacion', None)

    registrar_cambio(
        usuario_id=id_usuario,
        tipo_cambio='editar',
        nombre_entidad=f'Línea {nombre_organizacion}',
        tabla='lineas_transporte',
        campo= campo,
        descripcion= descripcion
    )
    
    db.session.commit()
    return linea

def eliminar_linea(id_linea, descripcion=None, usuario_id=None):
    linea = LineaTransporte.query.get(id_linea)
    if not linea:
        raise ValueError("Línea no encontrada")

    nombre = getattr(linea, 'nombre_organizacion', None)

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='eliminar',
        nombre_entidad=f'Línea {nombre}',
        tabla='lineas_transporte',
        campo=None,
        descripcion=descripcion or 'Eliminación de línea'
    )

    db.session.delete(linea)
    db.session.commit()
    return True
