from sqlalchemy import desc
from config import db
from models.models import CambioLog, Usuario 

def obtener_historial_cambios(tabla=None, limit=None, timestamp_field='fecha'):
    query = db.session.query(CambioLog, Usuario).outerjoin(Usuario, Usuario.id_usuario == CambioLog.usuario_id)

    if tabla:
        query = query.filter(CambioLog.tabla == tabla)

    ts_attr = getattr(CambioLog, timestamp_field)
    query = query.order_by(desc(ts_attr))

    if limit:
        query = query.limit(limit)

    rows = query.all()

    result = []
    for cambio, usuario in rows:
        result.append({
            "id_cambio": cambio.id_cambio,
            "usuario_id": cambio.usuario_id,
            "usuario_nombre": usuario.nombre if usuario else None,
            "tipo_cambio": cambio.tipo_cambio,
            "nombre_entidad": cambio.nombre_entidad,
            "tabla": cambio.tabla,
            "campo": cambio.campo,
            "descripcion": cambio.descripcion,
            "fecha": cambio.fecha.isoformat() if cambio.fecha else None
        })

    return result
