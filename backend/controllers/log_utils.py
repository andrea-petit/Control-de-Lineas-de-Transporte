import json
from config import db
from models.models import CambioLog

def registrar_cambio(usuario_id, tipo_cambio, nombre_entidad, tabla, campo, descripcion):
    entry = CambioLog(
        usuario_id=usuario_id,
        tipo_cambio=tipo_cambio,
        nombre_entidad=nombre_entidad,
        tabla=tabla,
        campo=campo,
        descripcion=descripcion
    )
    db.session.add(entry)

    return entry