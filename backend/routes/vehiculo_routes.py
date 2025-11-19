from flask import Blueprint, jsonify, request
from controllers.vehiculo_controllers import (
    listar_vehiculos_con_linea_y_chofer,
    listar_vehiculos_por_linea,
    listar_vehiculos_por_municipio,
    obtener_vehiculo,
    crear_vehiculo,
    editar_vehiculo,
    eliminar_vehiculo
)
from sqlalchemy import inspect
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback

vehiculo_bp = Blueprint('vehiculo_bp', __name__)


def model_to_dict_safe(obj):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, (list, tuple)):
        return [model_to_dict_safe(o) for o in obj]
    try:
        insp = inspect(obj)
        return {c.key: getattr(obj, c.key) for c in insp.mapper.column_attrs}
    except Exception:
        try:
            return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
        except Exception:
            return {}


@vehiculo_bp.route('/vehiculos', methods=['GET'])
def get_vehiculos():
    try:
        vehiculos = listar_vehiculos_con_linea_y_chofer()
        return jsonify(model_to_dict_safe(vehiculos) or []), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos/linea/<int:id_linea>', methods=['GET'])
def get_vehiculos_por_linea(id_linea):
    try:
        vehiculos = listar_vehiculos_por_linea(id_linea)
        return jsonify(model_to_dict_safe(vehiculos) or []), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos/municipio/<int:id_municipio>', methods=['GET'])
def get_vehiculos_por_municipio(id_municipio):
    try:
        vehiculos = listar_vehiculos_por_municipio(id_municipio)
        return jsonify(model_to_dict_safe(vehiculos) or []), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['GET'])
def get_vehiculo(id_vehiculo):
    try:
        vehiculo = obtener_vehiculo(id_vehiculo)
        if not vehiculo:
            return jsonify({'error': 'Vehículo no encontrado'}), 404
        return jsonify(model_to_dict_safe(vehiculo)), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos', methods=['POST'])
@jwt_required()
def post_vehiculo():
    data = request.json or {}
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        nuevo_vehiculo = crear_vehiculo(
            placa=data.get('placa'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            nombre_propietario=data.get('nombre_propietario'),
            cedula_propietario=data.get('cedula_propietario'),
            capacidad=data.get('capacidad'),
            litraje=data.get('litraje'),
            sindicato=data.get('sindicato'),
            modalidad=data.get('modalidad'),
            grupo=data.get('grupo'),
            combustible=data.get('combustible'),
            linea_id=data.get('linea_id'),
            descripcion=data.get('descripcion'),
            usuario_id=user_id
        )
        return jsonify(model_to_dict_safe(nuevo_vehiculo)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['PUT'])
@jwt_required()
def put_vehiculo(id_vehiculo):
    data = request.json or {}
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        vehiculo_editado = editar_vehiculo(
            id_vehiculo,
            campo=data.get('campo'),
            valor=data.get('valor'),
            descripcion=data.get('descripcion'),
            usuario_id=user_id
        )
        return jsonify(model_to_dict_safe(vehiculo_editado)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500


@vehiculo_bp.route('/vehiculos/<int:id_vehiculo>', methods=['DELETE'])
@jwt_required()
def delete_vehiculo(id_vehiculo):
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id
    try:
        eliminar_vehiculo(id_vehiculo, descripcion=(request.json or {}).get('descripcion'), usuario_id=user_id)
        return jsonify({'mensaje': 'Vehículo eliminado correctamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno", "detail": str(e)}), 500





