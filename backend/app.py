from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config, db, mail
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message
from routes.auth_routes import auth_bp
from routes.linea_routes import linea_bp
from routes.vehiculo_routes import vehiculo_bp
from routes.chofer_routes import chofer_bp
from routes.cambios_routes import cambios_bp
from routes.utils_routes import utils_bp
from routes.mantenimiento_routes import mantenimiento_bp
import os
import logging
from controllers.mantenimiento_controllers import handler as mantenimiento_handler



# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     CORS(app)

#     db.init_app(app)
#     mail.init_app(app)

#     app.register_blueprint(auth_bp, url_prefix='/api/auth')
#     app.register_blueprint(linea_bp, url_prefix='/api')
#     app.register_blueprint(vehiculo_bp, url_prefix='/api')
#     app.register_blueprint(chofer_bp, url_prefix='/api')
#     app.register_blueprint(cambios_bp, url_prefix='/api')
#     app.register_blueprint(utils_bp, url_prefix='/api')
#     app.register_blueprint(mantenimiento_bp, url_prefix='/api')

#     app.config['JWT_SECRET_KEY'] = 'secret-key'
#     jwt = JWTManager(app)

#     app.logger.setLevel(logging.ERROR)
#     if mantenimiento_handler not in app.logger.handlers:
#         app.logger.addHandler(mantenimiento_handler)

#     with app.app_context():
#         from models import models 
#         db.create_all()

#     return app




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    mail.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(linea_bp, url_prefix='/api')
    app.register_blueprint(vehiculo_bp, url_prefix='/api')
    app.register_blueprint(chofer_bp, url_prefix='/api')
    app.register_blueprint(cambios_bp, url_prefix='/api')
    app.register_blueprint(utils_bp, url_prefix='/api')
    app.register_blueprint(mantenimiento_bp, url_prefix='/api')

    app.config['JWT_SECRET_KEY'] = 'secret-key'
    jwt = JWTManager(app)

    app.logger.setLevel(logging.ERROR)
    if mantenimiento_handler not in app.logger.handlers:
        app.logger.addHandler(mantenimiento_handler)

    from controllers.mantenimiento_controllers import registrar_log
    from flask import jsonify

    @app.errorhandler(Exception)
    def handle_exception(e):
        try:
            ruta = request.path if request else "N/A"
            args = dict(request.args) if request else {}
            registrar_log(f"ERROR en {ruta} con args {args}: {e}", nivel="error")
        except Exception:
            pass  
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.errorhandler(404)
    def handle_404(e):
        registrar_log(f"404 Not Found: {e}", nivel="warning")
        return jsonify({"error": "Ruta no encontrada"}), 404

    with app.app_context():
        from models import models 
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=True)

