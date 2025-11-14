from flask import Blueprint, request, jsonify
from controllers.auth_controllers import crear_usuario, verificar_login, listar_usuarios, obtener_usuario, editar_usuario, eliminar_usuario, verificar_email, verificar_otp, resetear_password
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
    usuario = obtener_usuario_por_id(user_id)
    return jsonify({"is_admin": bool(usuario and usuario.rol == "admin")}), 200

@auth_bp.route('/editar/<int:id_usuario>', methods=['PUT'])
@jwt_required()
def edit_usuario(id_usuario):
    data = request.get_json()
    try:
        campo = data['campo']
        valor = data['valor']
        usuario = editar_usuario(id_usuario, campo, valor)
        return jsonify({"mensaje": "Usuario Actualizado", "id": usuario.id_usuario}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route('/eliminar/<int:id_linea>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id_usuario):
    data = request.get_json(silent=True) or {}
    try:
        eliminar_usuario(id_usuario)
        return jsonify({"mensaje": "Usuario Eliminado"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404

@auth_bp.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = listar_usuarios()
    data = [
        {
            "id": u.id_linea,
            "nombre": u.nombre,
            "email": u.email
        }
        for u in usuarios
    ]
    return jsonify(data), 200


@auth_bp.route('/usuarios/<int:id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    usuario = obtener_usuario(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = {
        "id": usuario.id_usuario,
        "nombre": usuario.nombre,
        "email": usuario.email
    }

    return jsonify(data), 200

@auth_bp.route("/email/<id_usuario>", methods=["GET"])
def route_enviar_otp(id_usuario):
    data, error = verificar_email(id_usuario)
    if error:
        return {"error": error}, 400
    return data, 200


@auth_bp.route("/verificar_otp", methods=["POST"])
def route_verificar_otp():
    body = request.json
    cedula = body.get("id_usuario")
    otp = body.get("otp")

    data, error = verificar_otp(cedula, otp)
    if error:
        return {"error": error}, 400
    return data, 200


@auth_bp.route("/reset_password", methods=["POST"])
def route_reset_password():
    body = request.json
    cedula = body.get("id_usuario")
    new_password = body.get("new_password")

    data, error = resetear_password(cedula, new_password)
    if error:
        return {"error": error}, 400
    return data, 200
    