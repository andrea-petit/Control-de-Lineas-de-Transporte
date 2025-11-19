import os
import socket
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from sqlalchemy import text
from config import db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG_PATH = os.path.join(BASE_DIR, "servicio_tecnico.log")

logger = logging.getLogger("servicio_tecnico")
logger.setLevel(logging.WARNING)

handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=1 * 1024 * 1024, 
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)



def registrar_log(mensaje: str, nivel="warning"):
    nivel = nivel.lower().strip()

    if nivel == "error":
        logger.error(mensaje)
    else:
        logger.warning(mensaje)

    return {
        "timestamp": datetime.now().isoformat(),
        "nivel": nivel,
        "mensaje": mensaje
    }

def obtener_logs(ultima_cantidad: int = 100):
    if not os.path.exists(LOG_PATH):
        return []

    try:
        with open(LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            return [l.rstrip("\n") for l in lines[-ultima_cantidad:]]
    except Exception as e:
        registrar_log(f"Error leyendo logs: {e}", "error")
        return []

def probar_conexion_db():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        if result == 1:
            return True, "Conexión OK"
        return False, "La BD respondió algo inesperado"
    except Exception as e:
        registrar_log(f"Error de conexión a DB: {e}", "error")
        return False, str(e)

def obtener_ip_servidor():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        registrar_log(f"No se pudo obtener IP del servidor: {e}", "error")
        return None

def resumen_estado():
    db_ok, db_msg = probar_conexion_db()
    ip = obtener_ip_servidor()

    return {
        "fecha": datetime.now().isoformat(),
        "ip_servidor": ip,
        "db_conectada": db_ok,
        "mensaje_db": db_msg,
        "logs_recientes": obtener_logs(50)
    }

def limpiar_logs():
    count = 0
    try:
        base = LOG_PATH
        directory = os.path.dirname(base)
        base_name = os.path.basename(base)

        for fname in os.listdir(directory):
            if fname.startswith(base_name):
                try:
                    os.remove(os.path.join(directory, fname))
                    count += 1
                except:
                    pass

        registrar_log("Se limpiaron todos los archivos de log", "warning")
        return count > 0
    except Exception as e:
        registrar_log(f"Error limpiando logs: {e}", "error")
        return False
