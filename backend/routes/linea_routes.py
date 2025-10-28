from flask import Blueprint, jsonify, request
from controllers.linea_controllers import listar_lineas, obtener_linea, crear_linea, editar_linea, eliminar_linea

linea_bp = Blueprint('linea_bp', __name__)

@linea_bp.route('/lineas', methods=['GET'])
def get_lineas():
    lineas = listar_lineas()
    data = [
        {
            "id": l.id_linea,
            "nombre_organizacion": l.nombre_organizacion,
            "nombre_propietario": l.nombre_propietario,
            "cedula_propietario": l.cedula_propietario,
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
        "nombre_propietario": linea.nombre_propietario,
        "cedula_propietario": linea.cedula_propietario,
        "id_municipio": linea.id_municipio
    }
    return jsonify(data), 200


@linea_bp.route('/lineas', methods=['POST'])
def add_linea():
    data = request.get_json()
    try:
        nueva = crear_linea(
            data['nombre_organizacion'],
            data['nombre_propietario'],
            data['cedula_propietario'],
            data['id_municipio']
        )
        return jsonify({"mensaje": "Línea creada", "id": nueva.id_linea}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400


@linea_bp.route('/lineas/<int:id_linea>', methods=['PUT'])
def update_linea(id_linea):
    data = request.get_json()
    try:
        campo = data['campo']
        valor = data['valor']
        linea = editar_linea(id_linea, campo, valor)
        return jsonify({"mensaje": "Línea actualizada", "id": linea.id_linea}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@linea_bp.route('/lineas/<int:id_linea>', methods=['DELETE'])
def delete_linea(id_linea):
    try:
        eliminar_linea(id_linea)
        return jsonify({"mensaje": "Línea eliminada"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
