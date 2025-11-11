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
    token = create_access_token(identity=str(u.id_usuario))
    rol= u.rol 
    return jsonify({"mensaje":"login correcto","access_token": token, "rol": rol }), 200

@auth_bp.route('/auth/is_admin', methods=['GET'])
@jwt_required()
def is_admin():
    raw_id = get_jwt_identity()
    try:
        user_id = int(raw_id) if raw_id is not None else None
    except (TypeError, ValueError):
        user_id = raw_id

    from controllers.auth_controllers import obtener_usuario_por_id
    usuario = obtener_usuario_por_id(user_id)  # usa tu función existente
    return jsonify({"is_admin": bool(usuario and usuario.rol == "admin")}), 200
