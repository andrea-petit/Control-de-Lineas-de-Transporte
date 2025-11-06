import requests
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState


class CambiosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Historial de Cambios")
        self.resize(1000, 520)
        self.setup_ui()
        self.cargar_cambios()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        self.label_titulo = QLabel("Historial de Cambios")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight:bold; font-size:16px; margin:8px; color:#2a3d66;")
        header.addWidget(self.label_titulo)
        layout.addLayout(header)



        self.tabla = QTableWidget()
        cols = ["Fecha", "Usuario", "Tipo", "Tabla", "Entidad", "Campo", "Descripción"]
        self.tabla.setColumnCount(len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        self.tabla.setAlternatingRowColors(True)



        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f2f6ff;
                border: 1px solid #d0d7e2;
                gridline-color: #d0d7e2;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #e3e9f5;
                padding: 6px;
                border: 1px solid #c7cdd8;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)


        anchos = [130, 160, 90, 110, 140, 130, 300]
        for idx, w in enumerate(anchos):
            self.tabla.setColumnWidth(idx, w)
        self.tabla.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.tabla)

        btns = QHBoxLayout()
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("Filtrar por tabla (ej: vehiculos)")
        self.input_filtro.setStyleSheet("""
            QLineEdit {
                border: 1px solid #b0b8c6;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #5b8def;
                outline: none;
            }
        """)

        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.setCursor(Qt.PointingHandCursor)
        self.btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #5b8def;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4a7ad1;
            }
            QPushButton:pressed {
                background-color: #3b66af;
            }
        """)
        self.btn_filtrar.clicked.connect(self.cargar_cambios)

        btns.addWidget(self.input_filtro)
        btns.addWidget(self.btn_filtrar)
        btns.addStretch()
        layout.addLayout(btns)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#f4f7ff"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

 
    def cargar_cambios(self):
        tabla = self.input_filtro.text().strip() or None
        params = {}
        if tabla:
            params["tabla"] = tabla
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/cambios", headers=headers, params=params, timeout=6)
            if r.ok:
                self.mostrar_cambios(r.json())
            else:
                QMessageBox.warning(self, "Error", f"No se pudo obtener historial ({r.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

 
    def mostrar_cambios(self, rows):
        self.tabla.setRowCount(0)
        for i, r in enumerate(rows):
            self.tabla.insertRow(i)

            fecha_str = r.get("fecha", "")
            try:
                fecha = datetime.fromisoformat(fecha_str).strftime("%d/%m/%Y %H:%M")
            except Exception:
                fecha = fecha_str

            usuario = r.get("usuario_nombre") or r.get("usuario", "") or str(r.get("usuario_id", ""))
            tipo = r.get("tipo_cambio", "")
            tabla = r.get("tabla", "")
            entidad = r.get("nombre_entidad", "")
            campo = r.get("campo", "")
            descripcion = r.get("descripcion", "")

            items = [fecha, usuario, tipo, tabla, entidad, campo, descripcion]
            for col, text in enumerate(items):
                it = QTableWidgetItem(str(text or ""))
                if col == 0:
                    it.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(i, col, it)
