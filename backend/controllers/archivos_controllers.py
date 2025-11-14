import io
import textwrap
import os
from uuid import uuid4
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, current_app, send_from_directory
from sqlalchemy import desc, func
from config import db
from models.models import Vehiculo, LineaTransporte, Chofer, municicipio

# ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Pandas (para Excel)
try:
    import pandas as pd
except Exception:
    pd = None

def _register_font():
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        return 'DejaVuSans'
    except Exception:
        return 'Helvetica'

_FONT_NAME = _register_font()

def obtener_vehiculos_por_filtro(id_municipio=None, combustible=None):
    """
    Devuelve lista de dicts con la información del vehículo, línea y choferes
    filtrada por id_municipio (entero) y combustible (string: 'diesel' o 'gasolina').
    Si un filtro es None no se aplica.
    """
    query = db.session.query(Vehiculo).join(LineaTransporte).join(municicipio)
    if id_municipio is not None:
        query = query.filter(municicipio.id_municipio == id_municipio)
    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    vehiculos = query.order_by(Vehiculo.id_vehiculo).all()

    resultados = []
    for v in vehiculos:
        # obtener choferes asociados (puede ser lista)
        choferes = [c.nombre for c in getattr(v, 'choferes', []) if getattr(c, 'nombre', None)]
        linea = getattr(v, 'linea', None)
        municipio = getattr(linea, 'municipio', None) if linea else None

        resultados.append({
            'id_vehiculo': v.id_vehiculo,
            'placa': v.placa,
            'marca': v.marca,
            'modelo': v.modelo,
            'capacidad': v.capacidad,
            'litraje': v.litraje,
            'sindicato': v.sindicato,
            'modalidad': v.modalidad,
            'grupo': v.grupo,
            'estado': v.estado,
            'combustible': v.combustible,
            'nombre_propietario': v.nombre_propietario,
            'cedula_propietario': v.cedula_propietario,
            'nombre_linea': linea.nombre_organizacion if linea else None,
            'id_municipio': municipio.id_municipio if municipio else None,
            'nombre_municipio': municipio.nombre if municipio else None,
            'choferes': ', '.join(choferes) if choferes else None
        })
    return resultados

def generar_reporte_pdf_bytes(registros, title=None):
    """
    Genera PDF en memoria a partir de la lista de dicts `registros`.
    Devuelve io.BytesIO.
    """
    buffer = io.BytesIO()
    width, height = A4
    margin = 15 * mm
    line_height = 7 * mm
    left = margin
    right = width - margin
    y_start = height - margin

    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont(_FONT_NAME, 14)
    titulo = title or "Reporte de Vehículos"
    c.drawString(left, y_start, titulo)
    c.setFont(_FONT_NAME, 9)
    fecha_generacion = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
    c.drawRightString(right, y_start, f"Generado: {fecha_generacion}")

    y = y_start - 2 * line_height

    headers = ['Placa', 'Marca', 'Modelo', 'Combustible', 'Línea', 'Municipio', 'Choferes']
    col_widths = [28*mm, 28*mm, 28*mm, 22*mm, 36*mm, 36*mm, (right - left) - (28+28+28+22+36+36)*mm]
    c.setFont(_FONT_NAME, 8)
    # dibujar encabezados
    for i, h in enumerate(headers):
        x = left + sum(col_widths[:i])
        c.drawString(x + 2, y, h)
    y -= line_height

    c.setFont(_FONT_NAME, 8)
    for reg in registros:
        if y < margin + line_height:
            c.showPage()
            c.setFont(_FONT_NAME, 9)
            c.drawString(left, height - margin, titulo)
            c.setFont(_FONT_NAME, 8)
            y = height - margin - 2 * line_height
            for i, h in enumerate(headers):
                x = left + sum(col_widths[:i])
                c.drawString(x + 2, y, h)
            y -= line_height

        vals = [
            str(reg.get('placa') or ''),
            str(reg.get('marca') or ''),
            str(reg.get('modelo') or ''),
            str(reg.get('combustible') or ''),
            str(reg.get('nombre_linea') or ''),
            str(reg.get('nombre_municipio') or ''),
            str(reg.get('choferes') or '')
        ]

        x = left
        # Escribir las primeras 6 columnas
        for i in range(len(headers)-1):
            txt = vals[i]
            c.drawString(x + 2, y, txt[:int(col_widths[i]/3)])
            x += col_widths[i]

        # Descripción choferes: wrap
        desc_text = vals[-1]
        max_chars = int(col_widths[-1] / 3)
        wrapped = textwrap.wrap(desc_text, width=max_chars) or ['']
        c.drawString(x + 2, y, wrapped[0])
        y -= line_height
        for extra in wrapped[1:]:
            if y < margin + line_height:
                c.showPage()
                c.setFont(_FONT_NAME, 8)
                y = height - margin - line_height
            c.drawString(left + 2, y, '')  # espacio
            c.drawString(x + 2, y, extra)
            y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generar_reporte_excel_bytes(registros):
    """
    Genera un XLSX en memoria a partir de registros (lista de dicts).
    Devuelve io.BytesIO.
    Requiere pandas.
    """
    if pd is None:
        raise RuntimeError("Pandas no está instalado. Instala con: pip install pandas openpyxl")

    df = pd.DataFrame(registros)
    # reordenar columnas si existen
    cols = ['id_vehiculo','placa','marca','modelo','combustible','nombre_linea','nombre_municipio','choferes',
            'capacidad','litraje','nombre_propietario','cedula_propietario','estado','sindicato','modalidad','grupo']
    cols_present = [c for c in cols if c in df.columns]
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Vehiculos', columns=cols_present)
    buffer.seek(0)
    return buffer

def generar_reporte_pdf_response(id_municipio=None, combustible=None, filename=None):
    registros = obtener_vehiculos_por_filtro(id_municipio=id_municipio, combustible=combustible)
    buffer = generar_reporte_pdf_bytes(registros, title=f"Vehículos - municipio={id_municipio} combustible={combustible}")
    if not filename:
        fecha = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_vehiculos_{fecha}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

def generar_reporte_excel_response(id_municipio=None, combustible=None, filename=None):
    registros = obtener_vehiculos_por_filtro(id_municipio=id_municipio, combustible=combustible)
    buffer = generar_reporte_excel_bytes(registros)
    if not filename:
        fecha = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_vehiculos_{fecha}.xlsx"
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

def _upload_folder(carpeta=None):
    """Devuelve la carpeta de subida (usa config o ./uploads)."""
    base = current_app.config.get('UPLOAD_FOLDER') if current_app else None
    if carpeta:
        return os.path.join(base or os.getcwd(), carpeta)
    return base or os.path.join(os.getcwd(), 'uploads')

def guardar_archivo(file_storage, carpeta=None):
    """
    Guarda un FileStorage (request.files['file']) en disco con nombre único.
    Devuelve metadata del archivo guardado.
    """
    if file_storage is None or file_storage.filename == '':
        raise ValueError("No se proporcionó ningún archivo")

    nombre_seguro = secure_filename(file_storage.filename)
    nombre_unico = f"{uuid4().hex}_{nombre_seguro}"
    folder = _upload_folder(carpeta)
    os.makedirs(folder, exist_ok=True)
    ruta = os.path.join(folder, nombre_unico)
    file_storage.save(ruta)

    size = os.path.getsize(ruta)
    fecha = datetime.utcfromtimestamp(os.path.getmtime(ruta)).isoformat() + 'Z'

    return {
        'filename': nombre_unico,
        'original_name': nombre_seguro,
        'size': size,
        'fecha': fecha,
        'path': ruta
    }

def listar_archivos(carpeta=None):
    """
    Lista archivos en la carpeta de uploads. Devuelve lista ordenada del más nuevo al más viejo.
    """
    folder = _upload_folder(carpeta)
    if not os.path.isdir(folder):
        return []

    entradas = []
    for fn in os.listdir(folder):
        ruta = os.path.join(folder, fn)
        if os.path.isfile(ruta):
            mtime = os.path.getmtime(ruta)
            entradas.append({
                'filename': fn,
                'size': os.path.getsize(ruta),
                'fecha_modificacion': datetime.utcfromtimestamp(mtime).isoformat() + 'Z',
                'path': ruta
            })
    # ordenar por fecha modificacion descendente (nuevo -> viejo)
    entradas.sort(key=lambda e: e['fecha_modificacion'], reverse=True)
    return entradas

def obtener_ruta_archivo(filename, carpeta=None):
    """
    Devuelve la ruta absoluta del archivo si existe, si no lanza FileNotFoundError.
    """
    folder = _upload_folder(carpeta)
    ruta = os.path.join(folder, filename)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {filename}")
    return ruta

def eliminar_archivo(filename, carpeta=None):
    """
    Elimina un archivo. Devuelve True si se eliminó, False si no existía.
    """
    try:
        ruta = obtener_ruta_archivo(filename, carpeta=carpeta)
    except FileNotFoundError:
        return False
    os.remove(ruta)
    return True

def descargar_archivo(filename, carpeta=None, as_attachment=True):
    """
    Devuelve send_from_directory para usar en una vista Flask.
    Ejemplo de uso en ruta: return descargar_archivo('mi.pdf')
    """
    folder = _upload_folder(carpeta)
    # send_from_directory lanza error si no existe; no manejamos aquí para que la ruta Flask controle el 404
    return send_from_directory(folder, filename, as_attachment=as_attachment)