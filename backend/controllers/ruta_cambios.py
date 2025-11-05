from sqlalchemy import desc
from config import db
from models.models import CambioLog  # <-- importar el modelo de logs

def obtener_historial_cambios(tabla=None, limit=None, timestamp_field='fecha'):
    """
    Devuelve lista de registros de cambios del más nuevo al más viejo.
    - tabla: si se pasa, filtra por el nombre de la tabla (p.e. 'lineas')
    - limit: cantidad máxima de registros a devolver
    - timestamp_field: nombre del campo fecha en el modelo de historial (por defecto 'fecha')
    """
    model = CambioLog  # modelo de logs

    query = model.query
    if tabla:
        query = query.filter_by(tabla=tabla)
    # ordenar del más nuevo al más viejo
    ts_attr = getattr(model, timestamp_field)
    query = query.order_by(desc(ts_attr))
    if limit:
        query = query.limit(limit)
    return query.all()
