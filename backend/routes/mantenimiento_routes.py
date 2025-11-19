from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.mantenimiento_controllers import (
    registrar_log, obtener_logs, probar_conexion_db,
    obtener_ip_servidor, resumen_estado, limpiar_logs
)

mantenimiento_bp = Blueprint("mantenimiento_bp", __name__)


@mantenimiento_bp.route("/mantenimiento/resumen", methods=["GET"])
def get_resumen():
    return jsonify(resumen_estado()), 200


@mantenimiento_bp.route("/mantenimiento/logs", methods=["GET"])
def get_logs():
    try:
        cantidad = int(request.args.get("count", 100))
    except Exception:
        cantidad = 100
    logs = obtener_logs(cantidad)
    return jsonify({"count": len(logs), "logs": logs}), 200


@mantenimiento_bp.route("/mantenimiento/logs", methods=["POST"])
@jwt_required()
def post_log():
    data = request.get_json() or {}
    mensaje = data.get("mensaje") or data.get("message") or ""
    nivel = data.get("nivel", "info")
    if not mensaje:
        return jsonify({"error": "mensaje es requerido"}), 400
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else raw_id
    except Exception:
        user_id = raw_id
    texto = f"[user:{user_id}] {mensaje}"
    registro = registrar_log(texto, nivel)
    return jsonify(registro), 201


@mantenimiento_bp.route("/mantenimiento/logs", methods=["DELETE"])
@jwt_required()
def delete_logs():
    ok = limpiar_logs()
    if ok:
        return jsonify({"mensaje": "Logs eliminados"}), 200
    return jsonify({"error": "No había logs para eliminar"}), 404


@mantenimiento_bp.route("/mantenimiento/db_ping", methods=["GET"])
def get_db_ping():
    ok, msg = probar_conexion_db()
    return jsonify({"db_ok": ok, "mensaje": msg}), 200
