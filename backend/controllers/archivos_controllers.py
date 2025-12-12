import io
import os
from datetime import datetime
from flask import send_file
from sqlalchemy import func
from config import db, Config
from models.models import Vehiculo, LineaTransporte, Chofer, municicipio

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.drawing.image import Image as XLImage

_MES_ES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}

def _register_font():
    try:
        pdfmetrics.registerFont(TTFont("TimesNewRoman", "times.ttf"))
        return "TimesNewRoman"
    except:
        return "Helvetica"

_FONT_NAME = _register_font()
styles = getSampleStyleSheet()
styleN = styles["Normal"]


styleH = styles["Heading1"]
REPORT_LOGO_LEFT = Config.REPORT_LOGO_LEFT
REPORT_LOGO_RIGHT = Config.REPORT_LOGO_RIGHT

def _query_vehiculos(municipios=None, combustible=None, grupo=None, max_limit=5000):
    q = db.session.query(Vehiculo).join(LineaTransporte).join(municicipio)
    if municipios:
        if isinstance(municipios, str):
            municipios = [m.strip() for m in municipios.split(",") if m.strip()]
        q = q.filter(municicipio.nombre.in_(municipios))
    if combustible:
        q = q.filter(func.lower(Vehiculo.combustible) == combustible.lower())
    if grupo:
        q = q.filter(func.upper(Vehiculo.grupo) == grupo.upper())
    return q.order_by(LineaTransporte.nombre_organizacion, Vehiculo.placa).limit(max_limit).all()

def _vehiculo_to_row(v):
    linea = getattr(v, "linea", None)
    choferes = getattr(v, "choferes", []) or []
    chofer = choferes[0] if choferes else None
    return {
        "placa": v.placa,
        "marca": v.marca,
        "modelo": v.modelo,
        "capacidad": v.capacidad,
        "litraje": float(v.litraje or 0),
        "sindicato": v.sindicato or "",
        "modalidad": v.modalidad or "",
        "grupo": v.grupo or "",
        "estado": (v.estado or "").lower(),
        "propietario": v.nombre_propietario,
        "cedula_propietario": v.cedula_propietario,
        "linea": linea.nombre_organizacion if linea else "",
        "chofer": chofer.nombre if chofer else "",
        "cedula_chofer": chofer.cedula if chofer else "",
    }

def generar_reporte_pdf_bytes(municipios=None, combustible=None, grupo=None, title=None, **kwargs):
    vehiculos = _query_vehiculos(municipios, combustible, grupo)
    registros = [_vehiculo_to_row(v) for v in vehiculos]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    story = []

    mes = _MES_ES.get(datetime.now().month, "").upper()

    try: img_left = RLImage(REPORT_LOGO_LEFT, width=50, height=50)
    except: img_left = Paragraph("", styleN)
    try: img_right = RLImage(REPORT_LOGO_RIGHT, width=50, height=50)
    except: img_right = Paragraph("", styleN)

    title_style = ParagraphStyle("title", alignment=TA_CENTER, fontName=_FONT_NAME, fontSize=12)
    header_style = ParagraphStyle("header", alignment=TA_CENTER, fontName=_FONT_NAME, fontSize=11)
    sub_style = ParagraphStyle("sub", alignment=TA_CENTER, fontName=_FONT_NAME, fontSize=11)

    # Encabezado en 3 filas
    encabezado_tabla = Table([
        [img_left, Paragraph("<b>INSTITUTO MUNICIPAL DE TRÁNSITO Y TRANSPORTE PÚBLICO DE PASAJEROS DEL MUNICIPIO CARIRUBANA</b>", title_style), img_right],
        ["", Paragraph("<b>REGISTRO DE ORGANIZACIONES DE TRANSPORTE PÚBLICO URBANO DEL MUNICIPIO CARIRUBANA</b>", header_style), ""],
        ["", Paragraph(f"<b>{mes} — MASIVOS / POR PUESTO / TAXI / MOTO TAXI</b>", sub_style), ""]
    ], colWidths=[60, None, 60])
    encabezado_tabla.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(1,0),(1,0),"CENTER"),
        ("ALIGN",(1,1),(1,1),"CENTER"),
        ("ALIGN",(1,2),(1,2),"CENTER"),
        ("BOTTOMPADDING",(0,0),(-1,-1),6)
    ]))
    story.append(encabezado_tabla)
    story.append(Spacer(1, 10))

    # Tabla principal
    headers = ["Nº", "ORGANIZACIÓN", "PROPIETARIO - NOMBRE Y APELLIDO", "C.I",
               "CHOFER - NOMBRE Y APELLIDO", "C.I", "PLACA", "MARCA", "MODELO",
               "Nº DE PUESTOS", "LITRAJE", "SINDICATO", "GRUPO", "MODALIDAD", "FIRMA"]
    data = [headers]
    for i, r in enumerate(registros, 1):
        firma = "INACTIVO - NO FIRMA" if r["estado"] in ("inactivo", "suspendido") else ""
        data.append([i, r["linea"], r["propietario"], r["cedula_propietario"], r["chofer"], r["cedula_chofer"],
                     r["placa"], r["marca"], r["modelo"], r["capacidad"], r["litraje"], r["sindicato"],
                     r["grupo"], r["modalidad"], firma])

    base_widths = [19.33, 98.22, 82.11, 46, 65, 37, 49.89, 49.78,
                   45.67, 29.22, 27.33, 63.67, 25.78, 52.33, 141.33]
    usable_width = landscape(A4)[0] - 40
    scale = usable_width / sum(base_widths)
    col_widths = [w * scale for w in base_widths]

    tabla = Table(data, repeatRows=1, colWidths=col_widths)
    ts = TableStyle([
        ("FONTNAME",(0,0),(-1,-1),_FONT_NAME),
        ("FONTSIZE",(0,0),(-1,0),11),
        ("FONTSIZE",(0,1),(-1,-1),10),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#BFBFBF")),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.5,colors.black)
    ])
    for idx in range(1, len(data)):
        estado = registros[idx-1]["estado"]
        if estado == "suspendido":
            ts.add("BACKGROUND", (0, idx), (-1, idx), colors.HexColor("#C60505"))
        elif estado == "inactivo":
            ts.add("BACKGROUND", (0, idx), (-1, idx), colors.HexColor("#F4F429"))
    tabla.setStyle(ts)
    story.append(tabla)
    story.append(Spacer(1, 10))

    # Resumen
    story.append(Paragraph("<b>RESUMEN DE LITRAJE POR SINDICATO</b>", header_style))
    resumen = {}
    for r in registros:
        resumen.setdefault(r["sindicato"] or "SIN SINDICATO", 0)
        resumen[r["sindicato"] or "SIN SINDICATO"] += r["litraje"]

    resumen_data = [["Sindicato", "Total litros"]] + [[s, float(t)] for s, t in resumen.items()]
    resumen_tabla = Table(resumen_data, colWidths=[400, 150])
    resumen_tabla.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.black),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#BFBFBF")),
        ("FONTNAME",(0,0),(-1,-1),_FONT_NAME),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ]))
    story.append(resumen_tabla)
    story.append(Spacer(1, 6))

    # Total general en cuadro
    total_tabla = Table([[f"TOTAL GENERAL DE LITRAJE: {sum(resumen.values())}"]],
                        colWidths=[550])
    total_tabla.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#D9D9D9")),
        ("FONTNAME",(0,0),(-1,-1),_FONT_NAME),
        ("FONTSIZE",(0,0),(-1,-1),10),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("BOX",(0,0),(-1,-1),0.5,colors.black)
    ]))
    story.append(total_tabla)

    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_reporte_excel_bytes(municipios=None, combustible=None, grupo=None, title=None, **kwargs):
    vehiculos = _query_vehiculos(municipios, combustible, grupo)
    registros = [_vehiculo_to_row(v) for v in vehiculos]

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Vehículos"
    mes = _MES_ES.get(datetime.now().month, "").upper()

    # Ajuste de anchos de columna (A y O reservadas para logos; tabla va B..O)
    base_widths = [19.33, 98.22, 82.11, 46, 65, 37, 49.89, 49.78,
                   45.67, 29.22, 27.33, 63.67, 25.78, 52.33, 141.33]
    excel_widths = [round(w * 0.12, 2) for w in base_widths]  # B..O
    # Column A (logo izq) y O (logo der) con ancho fijo para que no se tape
    ws.column_dimensions["A"].width = 10
    for i, w in enumerate(excel_widths, start=2):  # B=2 .. O=15
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    ws.column_dimensions["O"].width = max(ws.column_dimensions["O"].width, 10)

    # Alturas del encabezado (fila 1 más alta para los logos)
    ws.row_dimensions[1].height = 60
    for r in (2, 3, 4):
        ws.row_dimensions[r].height = 25

    # Encabezado
    ws.merge_cells("B1:O1")
    ws.merge_cells("B2:O2")
    ws.merge_cells("B3:O3")
    ws.merge_cells("B4:O4")

    ws["B1"].value = "INSTITUTO MUNICIPAL DE TRÁNSITO Y TRANSPORTE PÚBLICO DE PASAJEROS DEL MUNICIPIO CARIRUBANA"
    ws["B1"].font = Font(bold=True, size=12)
    ws["B1"].alignment = Alignment(horizontal="center", vertical="center")

    ws["B2"].value = "REGISTRO DE ORGANIZACIONES DE TRANSPORTE PÚBLICO URBANO DEL MUNICIPIO CARIRUBANA"
    ws["B2"].font = Font(bold=True, size=11, color="FFC60505")  # rojo oscuro
    ws["B2"].alignment = Alignment(horizontal="center", vertical="center")

    ws["B3"].value = mes
    ws["B3"].font = Font(bold=True, size=11, color="FFC60505")
    ws["B3"].alignment = Alignment(horizontal="left", vertical="center")

    ws["B4"].value = "MASIVOS / POR PUESTO / TAXI / MOTO TAXI"
    ws["B4"].font = Font(bold=True, size=11)
    ws["B4"].alignment = Alignment(horizontal="right", vertical="center")

    # Logos: no silenciar errores; si no existen, fallar claramente
    if REPORT_LOGO_LEFT and os.path.exists(REPORT_LOGO_LEFT):
        img_l = XLImage(REPORT_LOGO_LEFT)
        img_l.width, img_l.height = 60, 60  # encaja en fila 1 (60 pt altura)
        ws.add_image(img_l, "A1")
    else:
        # Si falta, insertamos texto placeholder en A1 para que notes el hueco
        ws["A1"].value = "LOGO"
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws["A1"].font = Font(bold=True, size=10)

    if REPORT_LOGO_RIGHT and os.path.exists(REPORT_LOGO_RIGHT):
        img_r = XLImage(REPORT_LOGO_RIGHT)
        img_r.width, img_r.height = 60, 60
        ws.add_image(img_r, "O1")
    else:
        ws["O1"].value = "LOGO"
        ws["O1"].alignment = Alignment(horizontal="center", vertical="center")
        ws["O1"].font = Font(bold=True, size=10)

    # Tabla principal
    start_row = 6
    headers = ["Nº", "ORGANIZACIÓN", "PROPIETARIO - NOMBRE Y APELLIDO", "C.I",
               "CHOFER - NOMBRE Y APELLIDO", "C.I", "PLACA", "MARCA", "MODELO",
               "Nº DE PUESTOS", "LITRAJE", "SINDICATO", "GRUPO", "MODALIDAD", "FIRMA"]

    ws.row_dimensions[start_row].height = 30
    thin = Side(border_style="thin", color="000000")

    for col, h in enumerate(headers, start=1):  # columnas A..O (15)
        c = ws.cell(row=start_row, column=col, value=h)
        c.font = Font(bold=True, size=10)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.fill = PatternFill("solid", fgColor="BFBFBF")
        c.border = Border(top=thin, left=thin, right=thin, bottom=thin)

    for i, r in enumerate(registros, start=1):
        row = start_row + i
        ws.row_dimensions[row].height = 25
        firma = "INACTIVO - NO FIRMA" if r["estado"] in ("inactivo", "suspendido") else ""
        values = [i, r["linea"], r["propietario"], r["cedula_propietario"], r["chofer"], r["cedula_chofer"],
                  r["placa"], r["marca"], r["modelo"], r["capacidad"], r["litraje"], r["sindicato"],
                  r["grupo"], r["modalidad"], firma]
        for col, val in enumerate(values, start=1):
            c = ws.cell(row=row, column=col, value=val)
            c.font = Font(size=10)
            # Centro solo la primera columna (Nº); el resto a la izquierda
            c.alignment = Alignment(horizontal="center" if col == 1 else "left", vertical="center", wrap_text=True)
            c.border = Border(top=thin, left=thin, right=thin, bottom=thin)
            if r["estado"] == "suspendido":
                c.fill = PatternFill("solid", fgColor="FF0000")
            elif r["estado"] == "inactivo":
                c.fill = PatternFill("solid", fgColor="FFFF00")

    # Resumen
    resumen_start = start_row + len(registros) + 2
    ws.cell(row=resumen_start, column=1, value="RESUMEN DE LITRAJE POR SINDICATO").font = Font(bold=True, size=11)
    ws.cell(row=resumen_start + 1, column=1, value="Sindicato").font = Font(bold=True, size=10)
    ws.cell(row=resumen_start + 1, column=2, value="Total litros").font = Font(bold=True, size=10)

    resumen = {}
    for r in registros:
        key = r["sindicato"] or "SIN SINDICATO"
        resumen[key] = resumen.get(key, 0) + r["litraje"]

    for i, (s, t) in enumerate(resumen.items(), start=1):
        ws.cell(row=resumen_start + 1 + i, column=1, value=s).font = Font(size=10)
        ws.cell(row=resumen_start + 1 + i, column=2, value=t).font = Font(size=10)

    # Total general en cuadro (merge 1–2, borde y fondo)
    total_row = resumen_start + len(resumen) + 3
    ws.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=2)
    c = ws.cell(row=total_row, column=1, value=f"TOTAL GENERAL DE LITRAJE: {sum(resumen.values())}")
    c.font = Font(bold=True, size=11)
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.fill = PatternFill("solid", fgColor="D9D9D9")
    c.border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.row_dimensions[total_row].height = 25

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out

def generar_reporte_pdf_response(**params):
    buf = generar_reporte_pdf_bytes(**params)
    filename = f"reporte_vehiculos_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name=filename)


def generar_reporte_excel_response(**params):
    buf = generar_reporte_excel_bytes(**params)
    filename = f"reporte_vehiculos_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name=filename)

