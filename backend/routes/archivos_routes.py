from flask import request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from controllers.archivos_controllers import generar_reporte_pdf_response, generar_reporte_excel_response
from datetime import datetime

ALLOWED_COMBUSTIBLES = {'diesel', 'gasolina'}
MAX_LIMIT_CAP = 5000  # to avoid very large exports

def _validate_combustible(c):
    if c is None or c == '':
        return None
    c = c.strip().lower()
    if c not in ALLOWED_COMBUSTIBLES:
        raise ValueError("combustible inválido. Valores permitidos: diesel, gasolina")
    return c

def _safe_filename(name, default_prefix):
    if not name:
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{default_prefix}_{ts}"
    return secure_filename(name)

def register_reporte_routes(app):

    @app.route('/reporte/vehiculos.pdf', methods=['GET'])
    @jwt_required()
    def reporte_vehiculos_pdf():
        try:
            id_municipio = request.args.get('id_municipio', type=int)
            combustible = _validate_combustible(request.args.get('combustible', type=str))
            filename = _safe_filename(request.args.get('filename', type=str), 'reporte_vehiculos')
            # opcionales: fechas y limite
            fecha_desde = request.args.get('fecha_desde', type=str)
            fecha_hasta = request.args.get('fecha_hasta', type=str)
            max_limit = request.args.get('max_limit', type=int, default=1000)
            if max_limit < 1 or max_limit > MAX_LIMIT_CAP:
                return jsonify({'error': f'max_limit debe estar entre 1 y {MAX_LIMIT_CAP}'}), 400

            return generar_reporte_pdf_response(
                id_municipio=id_municipio,
                municipios=request.args.get('municipios', type=str),
                combustible=combustible,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filename=filename,
                max_limit=max_limit
            )
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/reporte/vehiculos.xlsx', methods=['GET'])
    @jwt_required()
    def reporte_vehiculos_xlsx():
        try:
            id_municipio = request.args.get('id_municipio', type=int)
            combustible = _validate_combustible(request.args.get('combustible', type=str))
            filename = _safe_filename(request.args.get('filename', type=str), 'reporte_vehiculos')
            fecha_desde = request.args.get('fecha_desde', type=str)
            fecha_hasta = request.args.get('fecha_hasta', type=str)
            max_limit = request.args.get('max_limit', type=int, default=1000)
            if max_limit < 1 or max_limit > MAX_LIMIT_CAP:
                return jsonify({'error': f'max_limit debe estar entre 1 y {MAX_LIMIT_CAP}'}), 400

            return generar_reporte_excel_response(
                id_municipio=id_municipio,
                municipios=request.args.get('municipios', type=str),
                combustible=combustible,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                filename=filename,
                max_limit=max_limit
            )
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500