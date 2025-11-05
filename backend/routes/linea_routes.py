from flask import Blueprint, jsonify, request
from controllers.linea_controllers import listar_lineas, obtener_linea, crear_linea, editar_linea, eliminar_linea
from flask_jwt_extended import jwt_required, get_jwt_identity

linea_bp = Blueprint('linea_bp', __name__)

@linea_bp.route('/lineas', methods=['GET'])
def get_lineas():
    lineas = listar_lineas()
    data = [
        {
            "id": l.id_linea,
            "nombre_organizacion": l.nombre_organizacion,
            "id_municipio": l.id_municipio
        }
        for l in lineas
    ]
    return jsonify(data), 200


@linea_bp.route('/lineas/<int:id_linea>', methods=['GET'])
def get_linea(id_linea):
    linea = obtener_linea(id_linea)
    if not linea:
        return jsonify({"error": "Línea no encontrada"}), 404

    data = {
        "id": linea.id_linea,
        "nombre_organizacion": linea.nombre_organizacion,
        "id_municipio": linea.id_municipio
    }

    return jsonify(data), 200


@linea_bp.route('/lineas', methods=['POST'])
@jwt_required()
def add_linea():
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    data = request.get_json()
    try:
        nueva = crear_linea(
            data['nombre_organizacion'],
            data['id_municipio'],
            user_id
        )
        return jsonify({"mensaje": "Línea creada", "id": nueva.id_linea}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400


@linea_bp.route('/lineas/<int:id_linea>', methods=['PUT'])
@jwt_required()
def update_linea(id_linea):
    data = request.get_json()
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        campo = data['campo']
        valor = data['valor']
        linea = editar_linea(id_linea, campo, valor, user_id, descripcion=data.get('descripcion'))
        return jsonify({"mensaje": "Línea actualizada", "id": linea.id_linea}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@linea_bp.route('/lineas/<int:id_linea>', methods=['DELETE'])
@jwt_required()
def delete_linea(id_linea):
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        eliminar_linea(id_linea, user_id, descripcion=request.json.get('descripcion'))
        return jsonify({"mensaje": "Línea eliminada"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404


