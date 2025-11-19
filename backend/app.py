from flask import Flask
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


    # --- DESHACER: no agregar FileHandler que escriba server.log ---
    # mantenemos logging por defecto (salida en terminal). Si ya agregaste handlers
    # manualmente puedes comentarlos o eliminarlos aquí.
    # Ejemplo: asegurar que no redirigimos sys.stdout/sys.stderr ni añadimos handlers a werkzeug.
    import logging
    werk = logging.getLogger("werkzeug")
    werk.setLevel(logging.INFO)
    # No añadimos FileHandler ni redirecciones para evitar escribir en server.log
    # ...existing code...

    with app.app_context():
        from models import models 
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=True)

