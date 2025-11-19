from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.chofer_controllers import listar_choferes, listar_choferes_por_vehiculo, obtener_chofer, crear_chofer, editar_chofer, eliminar_chofer, buscar_choferes_por_placa
from sqlalchemy.inspection import inspect


chofer_bp = Blueprint('chofer_bp', __name__)

def model_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

@chofer_bp.route('/choferes', methods=['GET'])
def get_choferes():
    choferes = listar_choferes()
    return jsonify(choferes), 200

@chofer_bp.route('/choferes/vehiculo/<int:id_vehiculo>', methods=['GET'])
def get_choferes_por_vehiculo(id_vehiculo):
    choferes = listar_choferes_por_vehiculo(id_vehiculo)
    return jsonify([model_to_dict(c) for c in choferes]), 200

@chofer_bp.route('/choferes/<int:id_chofer>', methods=['GET'])
def get_chofer(id_chofer):
    chofer = obtener_chofer(id_chofer)
    if chofer:
        return jsonify(model_to_dict(chofer)), 200
    return jsonify({'error': 'Chofer no encontrado'}), 404

@chofer_bp.route('/choferes/buscar/<placa>', methods=['GET'])
def buscar_choferes_por_placa(placa):
    choferes = buscar_choferes_por_placa(placa)
    return jsonify(choferes), 200

@chofer_bp.route('/choferes/buscar/<int:id_vehiculo>', methods=['GET'])
def buscar_choferes_por_idVehiculo(id_vehiculo):
    choferes = buscar_choferes_por_idVehiculo(id_vehiculo)
    return jsonify(choferes), 200

@chofer_bp.route('/choferes', methods=['POST'])
@jwt_required()
def post_chofer():
    data = request.json
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        nuevo_chofer = crear_chofer(
            nombre=data['nombre'],
            cedula=data['cedula'],
            id_vehiculo=data['id_vehiculo'],
            usuario_id=user_id  
        )
        return jsonify(model_to_dict(nuevo_chofer)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@chofer_bp.route('/choferes/<int:id_chofer>', methods=['PUT'])
@jwt_required()
def put_chofer(id_chofer):
    data = request.json
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    campo = data.get('campo')
    valor = data.get('valor')
    descripcion = data.get('descripcion')
    if not campo or valor is None:
        return jsonify({'error': 'Campo y valor son requeridos'}), 400
    try:
        chofer_editado = editar_chofer(
            id_chofer=id_chofer,
            campo=campo,
            valor=valor,
            descripcion=descripcion,
            usuario_id=user_id
        )
        return jsonify(model_to_dict(chofer_editado)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@chofer_bp.route('/choferes/<int:id_chofer>', methods=['DELETE'])
@jwt_required()
def delete_chofer(id_chofer):
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    data = request.get_json()
    descripcion = data.get('descripcion', 'Eliminación de chofer')
    try:
        eliminar_chofer(
            id_chofer=id_chofer,
            id_usuario=user_id,
            descripcion=descripcion
        )
        return jsonify({'mensaje': 'Chofer eliminado'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

