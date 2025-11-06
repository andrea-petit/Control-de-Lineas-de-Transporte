from flask import Blueprint, jsonify, request
from controllers.cambios_controllers import obtener_historial_cambios
from flask_jwt_extended import jwt_required, get_jwt_identity

cambios_bp= Blueprint('cambios_bp', __name__)

@cambios_bp.route('/cambios', methods=['GET'])
@jwt_required()
def get_cambios():
    tabla = request.args.get('tabla')
    limit = request.args.get('limit', type=int)
    timestamp_field = request.args.get('timestamp_field', 'fecha')

    cambios = obtener_historial_cambios(tabla=tabla, limit=limit, timestamp_field=timestamp_field)
    return jsonify(cambios), 200

