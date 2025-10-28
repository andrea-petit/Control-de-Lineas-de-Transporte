from flask import Blueprint, request, jsonify
from controllers.auth_controllers import crear_usuario, verificar_login
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status":"ok"}), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error":"sin cuerpo JSON"}), 400
    try:
        u = crear_usuario(data.get('id'), data.get('nombre'), data.get('email'), data.get('password'), data.get('rol','usuario'))
        return jsonify({"mensaje":"usuario creado", "email": u.email}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 409
    except Exception as e:
        return jsonify({"error": "error interno", "detail": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    u = verificar_login(data.get('id_usuario'), data.get('password'))
    if not u:
        return jsonify({"error":"credenciales inválidas"}), 401
    token = create_access_token(identity=u.id_usuario)
    return jsonify({"mensaje":"login correcto","access_token": token}), 200
