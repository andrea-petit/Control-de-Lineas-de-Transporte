from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from controllers.archivos_controllers import generar_reporte_pdf_response, generar_reporte_excel_response

def register_reporte_routes(app):
    """
    Registra las rutas de reporte en la app Flask.
    Uso: en tu run.py o donde creas `app` llama: register_reporte_routes(app)
    """

    @app.route('/reporte/vehiculos.pdf', methods=['GET'])
    def reporte_vehiculos_pdf():
        # parametros opcionales: id_municipio (int), combustible (string)
        id_municipio = request.args.get('id_municipio', type=int)
        combustible = request.args.get('combustible', type=str)
        filename = request.args.get('filename')  # opcional
        try:
            return generar_reporte_pdf_response(id_municipio=id_municipio, combustible=combustible, filename=filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/reporte/vehiculos.xlsx', methods=['GET'])
    def reporte_vehiculos_xlsx():
        id_municipio = request.args.get('id_municipio', type=int)
        combustible = request.args.get('combustible', type=str)
        filename = request.args.get('filename')  # opcional
        try:
            return generar_reporte_excel_response(id_municipio=id_municipio, combustible=combustible, filename=filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 400