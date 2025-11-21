import io
import textwrap
import os
from uuid import uuid4
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, current_app, send_from_directory, has_app_context
from sqlalchemy import desc, func
from config import db
from models.models import Vehiculo, LineaTransporte, Chofer, municicipio

# ReportLab (se usa en generar_reporte_pdf_bytes)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ...existing code...
# Pandas (para Excel) - import opcional
try:
    import pandas as pd
except Exception:
    pd = None

# openpyxl para plantillas Excel (opcional)
try:
    from openpyxl import load_workbook
except Exception:
    load_workbook = None

# Si no vas a usar desc, eliminarlo de los imports iniciales o dejarlo si se usa
# from sqlalchemy import desc, func  -> si no usas desc, deja solo: from sqlalchemy import func
# ...existing code...

def _register_font():
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        return 'DejaVuSans'
    except Exception:
        return 'Helvetica'

_FONT_NAME = _register_font()

def _parse_date(d):
    """Parsea string 'YYYY-MM-DD' o devuelve datetime si ya es datetime o None."""
    if d is None or d == '':
        return None
    if isinstance(d, datetime):
        return d
    try:
        return datetime.strptime(d, '%Y-%m-%d')
    except Exception:
        raise ValueError("Formato de fecha inválido. Usa 'YYYY-MM-DD'.")

def obtener_vehiculos_por_municipios(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, max_limit=1000):
    """
    Busca vehículos por lista de municipios (nombres) y tipo de combustible.
    - municipios: lista de nombres o string separado por comas (ej. 'Carirubana,Taques,Falcon').
      Si None devuelve todos.
    - combustible: 'diesel' o 'gasolina' (case-insensitive). Si None no filtra.
    - fecha_desde, fecha_hasta: opcional, formato 'YYYY-MM-DD'. Aplican solo si Vehiculo tiene campo fecha.
    - max_limit: límite de seguridad.
    Retorna lista de dicts con información del vehículo, línea y chofer(es).
    """
    # validar combustible
    if combustible and combustible.lower() not in ('diesel', 'gasolina'):
        raise ValueError("combustible debe ser 'diesel' o 'gasolina'")

    # Normalizar municipios a lista de nombres
    nombres = None
    if municipios:
        if isinstance(municipios, str):
            nombres = [m.strip() for m in municipios.split(',') if m.strip()]
        else:
            nombres = [str(m).strip() for m in municipios if m]

    # Parsear fechas
    fd = _parse_date(fecha_desde)
    fh = _parse_date(fecha_hasta)
    if fd and fh and fh < fd:
        raise ValueError("fecha_hasta debe ser mayor o igual a fecha_desde.")

    # Construir consulta base
    query = db.session.query(Vehiculo).join(LineaTransporte).join(municicipio)

    if nombres:
        query = query.filter(municicipio.nombre.in_(nombres))

    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    # Aplicar filtro por rango de fechas si el modelo Vehiculo tiene columna de fecha
    fecha_attr = None
    for posible in ('created_at', 'fecha', 'fecha_creacion', 'created', 'created_on'):
        if hasattr(Vehiculo, posible):
            fecha_attr = getattr(Vehiculo, posible)
            break

    if (fd or fh):
        if fecha_attr is None:
            raise RuntimeError("No se encontró un campo fecha en Vehiculo para filtrar por fechas. "
                               "Si quieres filtrar por logs usa CambioLog o añade un campo fecha al modelo Vehiculo.")
        if fd:
            query = query.filter(fecha_attr >= fd)
        if fh:
            fh_end = datetime(fh.year, fh.month, fh.day, 23, 59, 59)
            query = query.filter(fecha_attr <= fh_end)

    vehiculos = query.order_by(Vehiculo.id_vehiculo).limit(max_limit).all()

    resultados = []
    for v in vehiculos:
        # obtener choferes asociados (puede ser lista)
        chofer_objs = getattr(v, 'choferes', []) or []
        choferes_nombres = [c.nombre for c in chofer_objs if getattr(c, 'nombre', None)]
        nombre_chofer = choferes_nombres[0] if choferes_nombres else None

        linea = getattr(v, 'linea', None)
        municipio = getattr(linea, 'municipio', None) if linea else None

        resultados.append({
            'id_vehiculo': getattr(v, 'id_vehiculo', None),
            'placa': getattr(v, 'placa', None),
            'marca': getattr(v, 'marca', None),
            'modelo': getattr(v, 'modelo', None),
            'capacidad': getattr(v, 'capacidad', None),
            'litraje': getattr(v, 'litraje', None),
            'sindicato': getattr(v, 'sindicato', None),
            'modalidad': getattr(v, 'modalidad', None),
            'grupo': getattr(v, 'grupo', None),
            'estado': getattr(v, 'estado', None),
            'combustible': getattr(v, 'combustible', None),
            'nombre_propietario': getattr(v, 'nombre_propietario', None),
            'cedula_propietario': getattr(v, 'cedula_propietario', None),
            'nombre_linea': linea.nombre_organizacion if linea else None,
            'id_municipio': municipio.id_municipio if municipio else None,
            'nombre_municipio': municipio.nombre if municipio else None,
            'nombre_chofer': nombre_chofer,
            'choferes': ', '.join(choferes_nombres) if choferes_nombres else None
        })
    return resultados

def obtener_vehiculos_por_filtro(id_municipio=None, combustible=None, fecha_desde=None, fecha_hasta=None, max_limit=1000):
    """
    Filtra vehículos por id_municipio y combustible. Devuelve lista de dicts.
    - max_limit: evita cargar demasiados registros.
    """
    if combustible and combustible.lower() not in ('diesel', 'gasolina'):
        raise ValueError("combustible debe ser 'diesel' o 'gasolina'")

    query = db.session.query(Vehiculo).join(LineaTransporte)
    if id_municipio is not None:
        # LineaTransporte tiene id_municipio
        query = query.filter(LineaTransporte.id_municipio == id_municipio)

    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    # aplicar filtro de fechas si existe campo fecha en Vehiculo
    fecha_attr = None
    for posible in ('created_at', 'fecha', 'fecha_creacion', 'created', 'created_on'):
        if hasattr(Vehiculo, posible):
            fecha_attr = getattr(Vehiculo, posible)
            break

    fd = _parse_date(fecha_desde)
    fh = _parse_date(fecha_hasta)
    if fd and fh and fh < fd:
        raise ValueError("fecha_hasta debe ser mayor o igual a fecha_desde.")
    if (fd or fh):
        if fecha_attr is None:
            raise RuntimeError("No se encontró un campo fecha en Vehiculo para filtrar por fechas.")
        if fd:
            query = query.filter(fecha_attr >= fd)
        if fh:
            fh_end = datetime(fh.year, fh.month, fh.day, 23, 59, 59)
            query = query.filter(fecha_attr <= fh_end)

    vehiculos = query.order_by(Vehiculo.id_vehiculo).limit(max_limit).all()

    resultados = []
    for v in vehiculos:
        chofer_objs = getattr(v, 'choferes', []) or []
        choferes_nombres = [c.nombre for c in chofer_objs if getattr(c, 'nombre', None)]
        nombre_chofer = choferes_nombres[0] if choferes_nombres else None
        linea = getattr(v, 'linea', None)
        municipio = getattr(linea, 'municipio', None) if linea else None
        resultados.append({
            'id_vehiculo': getattr(v, 'id_vehiculo', None),
            'placa': getattr(v, 'placa', None),
            'marca': getattr(v, 'marca', None),
            'modelo': getattr(v, 'modelo', None),
            'combustible': getattr(v, 'combustible', None),
            'nombre_linea': linea.nombre_organizacion if linea else None,
            'id_municipio': municipio.id_municipio if municipio else None,
            'nombre_municipio': municipio.nombre if municipio else None,
            'nombre_chofer': nombre_chofer,
            'choferes': ', '.join(choferes_nombres) if choferes_nombres else None
        })
    return resultados

# --- funciones de generación de PDF / Excel --

def generar_reporte_pdf_bytes(registros, title=None):
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

    headers = ['Placa', 'Marca', 'Modelo', 'Combustible', 'Línea', 'Municipio', 'Chofer']
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
            str(reg.get('nombre_chofer') or '')
        ]

        x = left
        for i in range(len(headers)-1):
            txt = vals[i]
            c.drawString(x + 2, y, txt[:int(col_widths[i]/3)])
            x += col_widths[i]

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
            c.drawString(left + 2, y, '')
            c.drawString(x + 2, y, extra)
            y -= line_height

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generar_reporte_excel_bytes(registros):
    if pd is None:
        raise RuntimeError("Pandas no está instalado. Instala con: pip install pandas openpyxl")

    df = pd.DataFrame(registros)
    cols = ['id_vehiculo','placa','marca','modelo','combustible','nombre_linea','nombre_municipio','nombre_chofer','choferes',
            'capacidad','litraje','nombre_propietario','cedula_propietario','estado','sindicato','modalidad','grupo']
    cols_present = [c for c in cols if c in df.columns]
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Vehiculos', columns=cols_present)
    buffer.seek(0)
    return buffer

def generar_reporte_pdf_response(id_municipio=None, municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, filename=None, max_limit=1000):
    """
    Genera Response Flask con PDF. Usa id_municipio o lista/str municipios.
    """
    if id_municipio is not None:
        registros = obtener_vehiculos_por_filtro(id_municipio=id_municipio, combustible=combustible,
                                                fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, max_limit=max_limit)
    else:
        registros = obtener_vehiculos_por_municipios(municipios=municipios, combustible=combustible,
                                                     fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, max_limit=max_limit)
    buffer = generar_reporte_pdf_bytes(registros, title=f"Vehículos - combustible={combustible}")
    if not filename:
        fecha = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_vehiculos_{fecha}.pdf"
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

def generar_reporte_excel_response(id_municipio=None, municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, filename=None, max_limit=1000):
    if id_municipio is not None:
        registros = obtener_vehiculos_por_filtro(id_municipio=id_municipio, combustible=combustible,
                                                fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, max_limit=max_limit)
    else:
        registros = obtener_vehiculos_por_municipios(municipios=municipios, combustible=combustible,
                                                     fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, max_limit=max_limit)
    buffer = generar_reporte_excel_bytes(registros)
    if not filename:
        fecha = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_vehiculos_{fecha}.xlsx"
    return send_file(buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

# --- utilidades de archivos (mantengo las funciones existentes) ---

def _upload_folder(carpeta=None):
    """Devuelve la carpeta de subida (usa config o ./uploads)."""
    base = current_app.config.get('UPLOAD_FOLDER') if has_app_context() else None
    if carpeta:
        return os.path.join(base or os.getcwd(), carpeta)
    return base or os.path.join(os.getcwd(), 'uploads')

def guardar_archivo(file_storage, carpeta=None):
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
    return {'filename': nombre_unico, 'original_name': nombre_seguro, 'size': size, 'fecha': fecha, 'path': ruta}

def listar_archivos(carpeta=None):
    folder = _upload_folder(carpeta)
    if not os.path.isdir(folder):
        return []
    entradas = []
    for fn in os.listdir(folder):
        ruta = os.path.join(folder, fn)
        if os.path.isfile(ruta):
            mtime = os.path.getmtime(ruta)
            entradas.append({'filename': fn, 'size': os.path.getsize(ruta),
                             'fecha_modificacion': datetime.utcfromtimestamp(mtime).isoformat() + 'Z', 'path': ruta})
    entradas.sort(key=lambda e: e['fecha_modificacion'], reverse=True)
    return entradas

def obtener_ruta_archivo(filename, carpeta=None):
    folder = _upload_folder(carpeta)
    ruta = os.path.join(folder, filename)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {filename}")
    return ruta

def eliminar_archivo(filename, carpeta=None):
    try:
        ruta = obtener_ruta_archivo(filename, carpeta=carpeta)
    except FileNotFoundError:
        return False
    os.remove(ruta)
    return True

def descargar_archivo(filename, carpeta=None, as_attachment=True):
    folder = _upload_folder(carpeta)
    return send_from_directory(folder, filename, as_attachment=as_attachment)