import os
import socket
import logging
from datetime import datetime
from sqlalchemy import text
from config import db

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SERVER_LOG = os.path.join(BASE_DIR, "server.log")
LEGACY_LOG = os.path.join(BASE_DIR, "servicio_tecnico.log")

LOG_FILE = SERVER_LOG if os.path.exists(SERVER_LOG) else LEGACY_LOG

MAX_LOG_LINES = 100

logger = logging.getLogger("servicio_tecnico")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler(LEGACY_LOG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _trim_file_to_last_n_lines(path: str, max_lines: int):
    """Mantiene solo las últimas `max_lines` líneas del archivo `path`."""
    try:
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        if len(lines) <= max_lines:
            return
        tail = lines[-max_lines:]
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8", errors="ignore") as f:
            f.writelines(tail)
        os.replace(tmp_path, path)
    except Exception as e:
        try:
            logger.error(f"Error trimming log file {path}: {e}")
        except Exception:
            pass


def _trim_all_logs(max_lines: int = MAX_LOG_LINES):
    for p in (SERVER_LOG, LEGACY_LOG):
        _trim_file_to_last_n_lines(p, max_lines)


def registrar_log(mensaje: str, nivel: str = "info"):
    nivel = (nivel or "info").lower()
    if nivel == "info":
        logger.info(mensaje)
    elif nivel == "warning":
        logger.warning(mensaje)
    elif nivel == "error":
        logger.error(mensaje)
    else:
        logger.debug(mensaje)

    try:
        _trim_all_logs(MAX_LOG_LINES)
    except Exception:
        pass

    return {"timestamp": datetime.now().isoformat(), "nivel": nivel, "mensaje": mensaje}


def obtener_logs(ultima_cantidad: int = 100):
    """
    Devuelve las últimas `ultima_cantidad` líneas del archivo de logs del servidor (server.log).
    Si no existe server.log, intenta servicio_tecnico.log.
    Antes de leer recorta el archivo para asegurar que no crezca indefinidamente.
    """
    # escoger archivo disponible
    path = SERVER_LOG if os.path.exists(SERVER_LOG) else LEGACY_LOG
    if not os.path.exists(path):
        return []
    try:
        # Asegurar que el archivo no supere MAX_LOG_LINES (recorta si es necesario)
        _trim_file_to_last_n_lines(path, MAX_LOG_LINES)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            tail = lines[-int(ultima_cantidad):] if lines else []
            return [l.rstrip("\n") for l in tail]
    except Exception as e:
        registrar_log(f"Error al leer logs: {e}", "error")
        return []


def probar_conexion_db():
    try:
        result = db.session.execute(text("SELECT 1")).scalar()
        if result == 1:
            return True, "Conexión OK"
        return False, "Conexión fallida: resultado inesperado"
    except Exception as e:
        registrar_log(f"Error de conexión a DB: {e}", "error")
        return False, str(e)


def obtener_ip_servidor():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
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
    removed = False
    try:
        for p in (LEGACY_LOG, SERVER_LOG):
            if os.path.exists(p):
                try:
                    os.remove(p)
                    removed = True
                except Exception as e:
                    registrar_log(f"Error eliminando {p}: {e}", "error")
        if removed:
            registrar_log("Logs limpiados", "info")
            return True
        return False
    except Exception as e:
        registrar_log(f"Error al limpiar logs: {e}", "error")
        return False

