from flask import Flask
from flask_cors import CORS
from config import Config, db

from routes.auth_routes import auth_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    with app.app_context():
        from models import models 
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port, debug=True)
