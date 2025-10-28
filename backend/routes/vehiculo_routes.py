from flask import Blueprint, jsonify, request
from controllers.vehiculo_controllers import listar_vehiculos, listar_vehiculos_por_linea, listar_vehiculos_por_municipio, obtener_vehiculo, crear_vehiculo, editar_vehiculo, eliminar_vehiculo
from sqlalchemy.inspection import inspect

def model_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

vehiculo_bp = Blueprint('vehiculo_bp', __name__)

@vehiculo_bp.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    vehiculos = listar_vehiculos()
    return jsonify([model_to_dict(v) for v in vehiculos]), 200

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
def post_vehiculo():
    data = request.json
    try:
        nuevo_vehiculo = crear_vehiculo(
            placa=data['placa'],
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            capacidad=data.get('capacidad'),
            litraje=data.get('litraje'),
            sindicato=data.get('sindicato'),
            modalidad=data.get('modalidad'),
            grupo=data.get('grupo'),
            combustible=data.get('combustible'),
            linea_id=data['linea_id']
        )
        return jsonify(model_to_dict(nuevo_vehiculo)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['PUT'])
def put_vehiculo(id_vehiculo):
    data = request.json
    try:
        vehiculo_editado = editar_vehiculo(
            id_vehiculo,
            campo=data['campo'],
            valor=data['valor']
        )
        return jsonify(model_to_dict(vehiculo_editado)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['DELETE'])
def delete_vehiculo(id_vehiculo):
    try:
        eliminar_vehiculo(id_vehiculo)
        return jsonify({'mensaje': 'Vehículo eliminado correctamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404





