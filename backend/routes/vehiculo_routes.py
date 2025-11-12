from flask import Blueprint, jsonify, request
from controllers.vehiculo_controllers import listar_vehiculos, listar_vehiculos_por_linea, listar_vehiculos_por_municipio, obtener_vehiculo, crear_vehiculo, editar_vehiculo, eliminar_vehiculo
from sqlalchemy.inspection import inspect
from flask_jwt_extended import jwt_required, get_jwt_identity

def model_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

vehiculo_bp = Blueprint('vehiculo_bp', __name__)

@vehiculo_bp.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = listar_vehiculos()
    return jsonify(vehiculos), 200

@vehiculo_bp.route('/vehiculos/linea/<int:id_linea>', methods=['GET'])
def get_vehiculos_por_linea(id_linea):
    vehiculos = listar_vehiculos_por_linea(id_linea)
    return jsonify([model_to_dict(v) for v in vehiculos]), 200    

@vehiculo_bp.route('/vehiculos/municipio/<int:id_municipio>', methods=['GET'])
def get_vehiculos_por_municipio(id_municipio):
    vehiculos = listar_vehiculos_por_municipio(id_municipio)
    return jsonify([model_to_dict(v) for v in vehiculos]), 200

@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['GET'])
def get_vehiculo(id_vehiculo):
    vehiculo = obtener_vehiculo(id_vehiculo)
    if vehiculo:
        return jsonify(model_to_dict(vehiculo)), 200
    return jsonify({'error': 'Vehículo no encontrado'}), 404

@vehiculo_bp.route('/vehiculos', methods=['POST'])
@jwt_required()
def post_vehiculo():
    data = request.json
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        nuevo_vehiculo = crear_vehiculo(
            placa=data['placa'],
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            nombre_propietario=data['nombre_propietario'],
            cedula_propietario=data['cedula_propietario'],
            capacidad=data.get('capacidad'),
            litraje=data.get('litraje'),
            sindicato=data.get('sindicato'),
            modalidad=data.get('modalidad'),
            grupo=data.get('grupo'),
            combustible=data.get('combustible'),
            linea_id=data['linea_id'],
            descripcion=data.get('descripcion'),
            usuario_id=user_id  
        )
        return jsonify(model_to_dict(nuevo_vehiculo)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['PUT'])
@jwt_required()
def put_vehiculo(id_vehiculo):
    data = request.json
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        vehiculo_editado = editar_vehiculo(
            id_vehiculo,
            campo=data['campo'],
            valor=data['valor'],
            descripcion=data.get('descripcion'),
            usuario_id=user_id  
        )
        return jsonify(model_to_dict(vehiculo_editado)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['DELETE'])
@jwt_required()
def delete_vehiculo(id_vehiculo):
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        eliminar_vehiculo(id_vehiculo, descripcion=request.json.get('descripcion'), usuario_id=user_id)
        return jsonify({'mensaje': 'Vehículo eliminado correctamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404





