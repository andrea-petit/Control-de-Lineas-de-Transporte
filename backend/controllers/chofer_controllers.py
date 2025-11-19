from models.models import Chofer
from models.models import Vehiculo
from config import db
from controllers.log_utils import registrar_cambio 

def listar_choferes():
    query = db.session.query(Chofer, Vehiculo).outerjoin(Vehiculo, Vehiculo.id_vehiculo == Chofer.id_vehiculo)

    rows = query.all()

    result = []

    for chofer, vehiculo in rows:
        result.append({
            "id_chofer": chofer.id_chofer,
            "nombre": chofer.nombre,
            "cedula": chofer.cedula,
            "vehiculo_id": chofer.id_vehiculo,
            "vehiculo_placa": vehiculo.placa if vehiculo else None,
            "vehiculo_marca": vehiculo.marca if vehiculo else None,
            "vehiculo_modelo": vehiculo.modelo if Vehiculo else None
        })

    return result



def listar_choferes_por_vehiculo(id_vehiculo):
    return Chofer.query.filter_by(vehiculo_id=id_vehiculo).all()

def buscar_choferes_por_placa(placa):
    query = db.session.query(Chofer, Vehiculo).join(Vehiculo, Vehiculo.id_vehiculo == Chofer.id_vehiculo).filter(Vehiculo.placa.ilike(f"%{placa}%"))

    rows = query.all()

    result = []

    for chofer, vehiculo in rows:
        result.append({
            "id_chofer": chofer.id_chofer,
            "nombre": chofer.nombre,
            "cedula": chofer.cedula,
            "vehiculo_id": chofer.id_vehiculo,
            "vehiculo_placa": vehiculo.placa if vehiculo else None,
            "vehiculo_marca": vehiculo.marca if vehiculo else None,
            "vehiculo_modelo": vehiculo.modelo if Vehiculo else None
        })

    return result

def buscar_choferes_por_idVehiculo(id_vehiculo):
    query = db.session.query(Chofer, Vehiculo).join(Vehiculo, Vehiculo.id_vehiculo == Chofer.id_vehiculo).filter(Vehiculo.id_vehiculo==id_vehiculo)

    rows = query.all()

    result = []

    for chofer, vehiculo in rows:
        result.append({
            "id_chofer": chofer.id_chofer,
            "nombre": chofer.nombre,
            "cedula": chofer.cedula,
            "vehiculo_id": chofer.id_vehiculo,
            "vehiculo_placa": vehiculo.placa if vehiculo else None,
            "vehiculo_marca": vehiculo.marca if vehiculo else None,
            "vehiculo_modelo": vehiculo.modelo if Vehiculo else None
        })

    return result


def obtener_chofer(id_chofer):
    return Chofer.query.get(id_chofer)

def crear_chofer(nombre, cedula, id_vehiculo, usuario_id=None, descripcion=None):
    if Chofer.query.filter_by(cedula=cedula).first():
        raise ValueError("Ya existe un chofer con esa cédula")
    
    nuevo = Chofer(
        nombre=nombre, cedula=cedula,
        id_vehiculo= id_vehiculo
    )

    db.session.add(nuevo)

    db.session.flush()

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='crear',
        nombre_entidad=f'Chofer {nombre} {cedula}',
        tabla='choferes',
        campo=None,
        descripcion= 'Creación de nuevo chofer'
    )

    db.session.commit()
    return nuevo

def editar_chofer(id_chofer, campo, valor, descripcion=None, usuario_id=None):
    chofer = Chofer.query.get(id_chofer)
    if not chofer:
        raise ValueError("Chofer no encontrado")

    previo = getattr(chofer, campo, None)
    setattr(chofer, campo, valor)

    nombre = getattr(chofer, 'nombre', None)
    cedula = getattr(chofer, 'cedula', None)

    registrar_cambio(
        usuario_id=usuario_id,
        tipo_cambio='editar',
        nombre_entidad=f'Chofer {nombre} {cedula}',
        tabla='choferes',
        campo= campo,
        descripcion= descripcion
    )
    
    db.session.commit()
    return chofer

def eliminar_chofer(id_chofer, id_usuario, descripcion):
    chofer = Chofer.query.get(id_chofer)
    if not chofer:
        raise ValueError("Chofer no encontrado")
    
    nombre = getattr(chofer, 'nombre', None)
    cedula = getattr(chofer, 'cedula', None)

    registrar_cambio(
        usuario_id=id_usuario,
        tipo_cambio='eliminar',
        nombre_entidad=f'Chofer {nombre} {cedula}',
        tabla='choferes',
        campo=None,
        descripcion=descripcion
    )

    db.session.delete(chofer)
    db.session.commit()
    return



