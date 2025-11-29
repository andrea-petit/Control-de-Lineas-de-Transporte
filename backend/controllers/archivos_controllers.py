import io
import os
from uuid import uuid4
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file, current_app, send_from_directory, has_app_context
from sqlalchemy import func
from config import db
from models.models import Vehiculo, LineaTransporte, Chofer, municicipio

# ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Pandas (opcional)
try:
    import pandas as pd
except Exception:
    pd = None

# openpyxl (opcional)
try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, Alignment
except Exception:
    Workbook = None
    load_workbook = None
    Font = None
    Alignment = None

def _register_font():
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        return 'DejaVuSans'
    except Exception:
        return 'Helvetica'

_FONT_NAME = _register_font()

def _parse_date(d):
    if d is None or d == '':
        return None
    if isinstance(d, datetime):
        return d
    try:
        return datetime.strptime(d, '%Y-%m-%d')
    except Exception:
        raise ValueError("Formato de fecha inválido. Usa 'YYYY-MM-DD'.")

# ----------------------------
# Consultas
# ----------------------------
def obtener_vehiculos_por_municipios(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, max_limit=1000):
    if combustible and combustible.lower() not in ('diesel', 'gasolina'):
        raise ValueError("combustible debe ser 'diesel' o 'gasolina'")

    nombres = None
    if municipios:
        if isinstance(municipios, str):
            nombres = [m.strip() for m in municipios.split(',') if m.strip()]
        else:
            nombres = [str(m).strip() for m in municipios if m]

    fd = _parse_date(fecha_desde)
    fh = _parse_date(fecha_hasta)
    if fd and fh and fh < fd:
        raise ValueError("fecha_hasta debe ser mayor o igual a fecha_desde.")

    query = db.session.query(Vehiculo).join(LineaTransporte).join(municicipio)

    if nombres:
        query = query.filter(municicipio.nombre.in_(nombres))
    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    fecha_attr = None
    for posible in ('created_at', 'fecha', 'fecha_creacion', 'created', 'created_on'):
        if hasattr(Vehiculo, posible):
            fecha_attr = getattr(Vehiculo, posible)
            break

    if fd or fh:
        if fecha_attr is None:
            raise RuntimeError("No se encontró un campo fecha en Vehiculo para filtrar por fechas.")
        if fd:
            query = query.filter(fecha_attr >= fd)
        if fh:
            fh_end = datetime(fh.year, fh.month, fh.day, 23, 59, 59)
            query = query.filter(fecha_attr <= fh_end)

    vehiculos = query.order_by(getattr(Vehiculo, 'id_vehiculo', Vehiculo.id)).limit(max_limit).all()

    resultados = []
    for v in vehiculos:
        chofer_objs = getattr(v, 'choferes', []) or []
        choferes_nombres = [getattr(c, 'nombre', '') for c in chofer_objs if getattr(c, 'nombre', None)]
        nombre_chofer = choferes_nombres[0] if choferes_nombres else None

        linea = getattr(v, 'linea', None)
        municipio = getattr(linea, 'municipio', None) if linea else None

        resultados.append({
            'id_vehiculo': getattr(v, 'id_vehiculo', None),
            'placa': getattr(v, 'placa', None),
            'marca': getattr(v, 'marca', None),
            'modelo': getattr(v, 'modelo', None),
            'capacidad': getattr(v, 'capacidad', None),
            'litraje': getattr(v, 'litraje', 0) or 0,
            'sindicato': getattr(v, 'sindicato', None),
            'modalidad': getattr(v, 'modalidad', None),
            'grupo': getattr(v, 'grupo', None),
            'estado': (getattr(v, 'estado', '') or '').strip().lower(),
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
    if combustible and combustible.lower() not in ('diesel', 'gasolina'):
        raise ValueError("combustible debe ser 'diesel' o 'gasolina'")

    query = db.session.query(Vehiculo).join(LineaTransporte)
    if id_municipio is not None:
        # LineaTransporte assumed to have id_municipio
        query = query.filter(LineaTransporte.id_municipio == id_municipio)
    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    fecha_attr = None
    for posible in ('created_at', 'fecha', 'fecha_creacion', 'created', 'created_on'):
        if hasattr(Vehiculo, posible):
            fecha_attr = getattr(Vehiculo, posible)
            break

    fd = _parse_date(fecha_desde)
    fh = _parse_date(fecha_hasta)
    if fd and fh and fh < fd:
        raise ValueError("fecha_hasta debe ser mayor o igual a fecha_desde.")
    if fd or fh:
        if fecha_attr is None:
            raise RuntimeError("No se encontró un campo fecha en Vehiculo para filtrar por fechas.")
        if fd:
            query = query.filter(fecha_attr >= fd)
        if fh:
            fh_end = datetime(fh.year, fh.month, fh.day, 23, 59, 59)
            query = query.filter(fecha_attr <= fh_end)

    vehiculos = query.order_by(getattr(Vehiculo, 'id_vehiculo', Vehiculo.id)).limit(max_limit).all()

    resultados = []
    for v in vehiculos:
        chofer_objs = getattr(v, 'choferes', []) or []
        choferes_nombres = [getattr(c, 'nombre', '') for c in chofer_objs if getattr(c, 'nombre', None)]
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

# ----------------------------
# Plantilla: registros y total
# ----------------------------
def _obtener_registros_para_plantilla(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, max_limit=1000):
    nombres = None
    if municipios:
        if isinstance(municipios, str):
            nombres = [m.strip() for m in municipios.split(',') if m.strip()]
        else:
            nombres = [str(m).strip() for m in municipios if m]

    if combustible and combustible.lower() not in ('diesel', 'gasolina'):
        raise ValueError("combustible debe ser 'diesel' o 'gasolina'")

    query = db.session.query(Vehiculo).join(LineaTransporte).join(municicipio)
    if nombres:
        query = query.filter(municicipio.nombre.in_(nombres))
    if combustible:
        query = query.filter(func.lower(Vehiculo.combustible) == combustible.lower())

    fd = _parse_date(fecha_desde)
    fh = _parse_date(fecha_hasta)
    fecha_attr = None
    for posible in ('created_at', 'fecha', 'fecha_creacion', 'created', 'created_on'):
        if hasattr(Vehiculo, posible):
            fecha_attr = getattr(Vehiculo, posible)
            break
    if fd or fh:
        if fecha_attr is None:
            raise RuntimeError("No se encontró un campo fecha en Vehiculo para filtrar por fechas.")
        if fd:
            query = query.filter(fecha_attr >= fd)
        if fh:
            fh_end = datetime(fh.year, fh.month, fh.day, 23, 59, 59)
            query = query.filter(fecha_attr <= fh_end)

    vehiculos = query.order_by(getattr(Vehiculo, 'id_vehiculo', Vehiculo.id)).limit(max_limit).all()

    registros = []
    total_litros = 0.0
    for v in vehiculos:
        linea = getattr(v, 'linea', None)

        propietario_nombre = getattr(v, 'nombre_propietario', '') or ''
        propietario_cedula = getattr(v, 'cedula_propietario', '') or ''

        chofer_objs = getattr(v, 'choferes', []) or []
        chofer_nombre = getattr(chofer_objs[0], 'nombre', '') if chofer_objs else ''
        chofer_cedula = getattr(chofer_objs[0], 'cedula', '') if chofer_objs else ''

        placa = getattr(v, 'placa', '') or ''
        marca = getattr(v, 'marca', '') or ''
        modelo = getattr(v, 'modelo', '') or ''
        numero_puestos = getattr(v, 'capacidad', None)
        litraje = float(getattr(v, 'litraje', 0) or 0)
        total_litros += litraje
        sindicato = getattr(v, 'sindicato', '') or ''
        grupo = getattr(v, 'grupo', '') or ''
        modalidad = getattr(v, 'modalidad', '') or ''
        estado = (getattr(v, 'estado', '') or '').strip().lower()

        registros.append({
            'organizacion': linea.nombre_organizacion if linea else '',
            'propietario_nombre': propietario_nombre,
            'propietario_cedula': propietario_cedula,
            'chofer_nombre': chofer_nombre,
            'chofer_cedula': chofer_cedula,
            'placa': placa,
            'marca': marca,
            'modelo': modelo,
            'numero_puestos': numero_puestos,
            'litraje': litraje,
            'sindicato': sindicato,
            'grupo': grupo,
            'modalidad': modalidad,
            'estado': estado
        })

    return registros, total_litros

# ----------------------------
# Generación PDF / Excel con plantilla
# ----------------------------
def generar_plantilla_pdf_bytes(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, title=None):
    registros, total = _obtener_registros_para_plantilla(municipios=municipios, combustible=combustible,
                                                        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=12*mm, rightMargin=12*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    story = []

    titulo = title or f"Reporte de Uso - {combustible or 'Todos'}"
    story.append(Paragraph(f"<b>{titulo}</b>", styles['Title']))
    story.append(Paragraph(f"Municipios: {municipios or 'Todos'}", styles['Normal']))
    story.append(Paragraph(f"Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
    story.append(Spacer(1, 6))

    headers = [
        'Organización','Propietario','Cédula Propietario','Chofer','Cédula Chofer','Placa',
        'Marca','Modelo','N° Puestos','Litraje','Sindic.','Grupo','Modalidad','Firma'
    ]
    data = [headers]

    for r in registros:
        estado = (r.get('estado') or '').lower()
        if estado == 'inactivo':
            firma_cell = Paragraph("INACTIVO", styles['Normal'])
        else:
            firma_cell = Paragraph("__________________________", styles['Normal'])

        row = [
            r.get('organizacion',''),
            r.get('propietario_nombre',''),
            r.get('propietario_cedula',''),
            r.get('chofer_nombre',''),
            r.get('chofer_cedula',''),
            r.get('placa',''),
            r.get('marca',''),
            r.get('modelo',''),
            str(r.get('numero_puestos') or ''),
            f"{r.get('litraje'):.2f}",
            r.get('sindicato',''),
            r.get('grupo',''),
            r.get('modalidad',''),
            firma_cell
        ]
        data.append(row)

    # total row: place label and total near Litraje column (index 9)
    total_row = [''] * len(headers)
    total_row[8] = 'Total litros:'
    total_row[9] = f"{total:.2f}"
    data.append(total_row)

    col_widths = [36*mm,36*mm,26*mm,36*mm,28*mm,20*mm,26*mm,20*mm,18*mm,22*mm,24*mm,20*mm,24*mm,38*mm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dfeaf6')),
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('ALIGN',(9,1),(9,-2),'RIGHT'),
        ('ALIGN',(8,-1),(9,-1),'RIGHT'),
    ]))
    story.append(table)
    story.append(Spacer(1,12))
    story.append(Paragraph("Responsable: _____________________    Fecha: ____________", styles['Normal']))
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_plantilla_excel_bytes(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None):
    registros, total = _obtener_registros_para_plantilla(municipios=municipios, combustible=combustible,
                                                        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)

    if Workbook is not None:
        wb = Workbook()
        ws = wb.active
        ws.title = "UsoCombustible"
        headers = [
            'Organización','Propietario','Cédula Propietario','Chofer','Cédula Chofer','Placa',
            'Marca','Modelo','N° Puestos','Litraje','Sindic.','Grupo','Modalidad','Firma'
        ]
        ws.append(headers)
        widths = [20,25,15,20,15,12,15,12,10,12,15,12,15,25]
        for i,w in enumerate(widths, start=1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w

        for r in registros:
            values = [
                r.get('organizacion',''),
                r.get('propietario_nombre',''),
                r.get('propietario_cedula',''),
                r.get('chofer_nombre',''),
                r.get('chofer_cedula',''),
                r.get('placa',''),
                r.get('marca',''),
                r.get('modelo',''),
                r.get('numero_puestos') or '',
                r.get('litraje') or 0,
                r.get('sindicato',''),
                r.get('grupo',''),
                r.get('modalidad',''),
                ''
            ]
            ws.append(values)
            current_row = ws.max_row
            estado = (r.get('estado') or '').lower()
            firma_cell = ws.cell(row=current_row, column=len(headers))
            if estado == 'inactivo' and Font is not None:
                firma_cell.value = "INACTIVO"
                firma_cell.font = Font(strike=True)
                firma_cell.alignment = Alignment(horizontal='center')
            else:
                firma_cell.value = ""

        total_row = ws.max_row + 2
        ws.cell(row=total_row, column=9, value="Total litros:")
        ws.cell(row=total_row, column=10, value=total)

        out = io.BytesIO()
        wb.save(out)
        out.seek(0)
        return out

    # fallback con pandas (sin formato)
    if pd is None:
        raise RuntimeError("No se puede generar Excel: falta openpyxl o pandas.")
    df = pd.DataFrame(registros)
    # normalizar nombres de columnas para exportar
    df = df.rename(columns={
        'organizacion':'Organización',
        'propietario_nombre':'Propietario',
        'propietario_cedula':'Cédula Propietario',
        'chofer_nombre':'Chofer',
        'chofer_cedula':'Cédula Chofer',
        'placa':'Placa',
        'marca':'Marca',
        'modelo':'Modelo',
        'numero_puestos':'N° Puestos',
        'litraje':'Litraje',
        'sindicato':'Sindic.',
        'grupo':'Grupo',
        'modalidad':'Modalidad',
        'estado':'Estado'
    })
    # añadir fila total
    total_row = {col: '' for col in df.columns}
    if 'Litraje' in df.columns:
        total_row['Litraje'] = total
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='UsoCombustible')
    out.seek(0)
    return out

def generar_plantilla_pdf_response(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, filename=None):
    buf = generar_plantilla_pdf_bytes(municipios=municipios, combustible=combustible,
                                      fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    if not filename:
        filename = f"plantilla_uso_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=filename)

def generar_plantilla_excel_response(municipios=None, combustible=None, fecha_desde=None, fecha_hasta=None, filename=None):
    buf = generar_plantilla_excel_bytes(municipios=municipios, combustible=combustible,
                                        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
    if not filename:
        filename = f"plantilla_uso_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=filename)

# ----------------------------
# Utilidades de archivos
# ----------------------------
def _upload_folder(carpeta=None):
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