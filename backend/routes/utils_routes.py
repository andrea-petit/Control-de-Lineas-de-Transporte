from controllers.utils_controllers import obtener_municipios
from flask import Blueprint, jsonify

utils_bp= Blueprint('utils_bp', __name__)

@utils_bp.route('/municipios/nombres', methods=['GET'])
def get_municipios():
    municipios = obtener_municipios()
    return jsonify([{"id": m.id_municipio, "nombre": m.nombre} for m in municipios]), 200

