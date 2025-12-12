from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required 
from werkzeug.utils import secure_filename
from datetime import datetime

#descomentar jwt para proteger las rutas !!!


from controllers.archivos_controllers import (
    generar_reporte_pdf_response,
    generar_reporte_excel_response
)
ALLOWED_COMBUSTIBLES = {'diesel', 'gasolina'}

def _validate_combustible(c):
    if not c:
        return None
    c = c.strip().lower()
    if c not in ALLOWED_COMBUSTIBLES:
        raise ValueError("Combustible inválido. Solo: diesel, gasolina")
    return c

def _safe_filename(prefix):
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{ts}"

archivos_bp = Blueprint("archivos_bp", __name__)

@archivos_bp.route("/reportes/pdf", methods=["GET"])
# @jwt_required()  #si  senecesita proteger la ruta
def reporte_pdf():
    try:
        municipios = request.args.get("municipios")
        combustible = _validate_combustible(request.args.get("combustible"))
        grupo = request.args.get("grupo")

        filename = _safe_filename("reporte_vehiculos")

        return generar_reporte_pdf_response(
            municipios=municipios,
            combustible=combustible,
            grupo=grupo,
            filename=filename
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error generando reporte PDF", "detalle": str(e)}), 500

@archivos_bp.route("/reportes/xlsx", methods=["GET"])
# @jwt_required()
def reporte_xlsx():
    try:
        municipios = request.args.get("municipios")
        combustible = _validate_combustible(request.args.get("combustible"))
        grupo = request.args.get("grupo")

        filename = _safe_filename("reporte_vehiculos")

        return generar_reporte_excel_response(
            municipios=municipios,
            combustible=combustible,
            grupo=grupo,
            filename=filename
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error generando reporte Excel", "detalle": str(e)}), 500
