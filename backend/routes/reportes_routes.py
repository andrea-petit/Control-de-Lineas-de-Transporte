from flask import Blueprint, request, jsonify
import traceback
from controllers.archivos_controllers import generar_reporte_pdf_response, generar_reporte_excel_response

reportes_bp = Blueprint('reportes_bp', __name__)

@reportes_bp.route('/reportes/pdf', methods=['GET'])
def route_reporte_pdf():
    try:
        params = {
            "municipios": request.args.get("municipios"),
            "combustible": request.args.get("combustible"),
            "grupo": request.args.get("grupo"),
            "title": request.args.get("title")
        }
        return generar_reporte_pdf_response(**params)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error generando PDF", "detail": str(e)}), 500

@reportes_bp.route('/reportes/xlsx', methods=['GET'])
def route_reporte_xlsx():
    try:
        params = {
            "municipios": request.args.get("municipios"),
            "combustible": request.args.get("combustible"),
            "grupo": request.args.get("grupo"),
            "title": request.args.get("title")
        }
        return generar_reporte_excel_response(**params)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error generando Excel", "detail": str(e)}), 500