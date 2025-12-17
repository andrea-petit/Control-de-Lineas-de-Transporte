import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from app_state import API_BASE, GlobalState
from PySide6.QtGui import QIcon
from app_state import resources_path
import os

from styles import estilos_formularios

class LineaDialog(QDialog):
    def __init__(self, parent=None, linea=None):
        super().__init__(parent)
        self.linea = linea 
        self.setWindowTitle("Editar Línea" if linea else "Nueva Línea")
        self.setWindowIcon(QIcon(resources_path('icons/bus.png').replace(os.sep, '/')))
        self.resize(450, 350)
        self.setup_ui()
        self.cargar_municipios()

        if linea:
            self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Nombre de la organización:"))
        self.input_nombre = QLineEdit()
        layout.addWidget(self.input_nombre)

        layout.addWidget(QLabel("Municipio:"))
        self.combo_municipio = QComboBox()
        self.combo_municipio.setStyleSheet(estilos_formularios + "QComboBox { color: black; } QComboBox QAbstractItemView { color: black; }")
        layout.addWidget(self.combo_municipio)

        layout.addWidget(QLabel("Descripción (registro de cambio):"))
        self.input_descripcion = QLineEdit()
        self.input_descripcion.setPlaceholderText("Breve descripción del cambio (opcional)")
        layout.addWidget(self.input_descripcion)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("cancelar")
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)

        self.setStyleSheet(estilos_formularios + "color: black;")

    def cargar_municipios(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/municipios/nombres", headers=headers)
            if r.status_code == 200:
                municipios = r.json()
                self.combo_municipio.clear()
                for m in municipios:
                    self.combo_municipio.addItem(m["nombre"], m["id"])
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar los municipios")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_datos(self):
        self.input_nombre.setText(self.linea.get("nombre_organizacion", ""))

        id_municipio = self.linea.get("id_municipio")
        idx = self.combo_municipio.findData(id_municipio)
        if idx >= 0:
            self.combo_municipio.setCurrentIndex(idx)

    def guardar(self):
        nombre_organizacion = self.input_nombre.text().strip().upper()
        id_municipio = self.combo_municipio.currentData()
        descripcion = self.input_descripcion.text().strip().upper()

        if not (nombre_organizacion and id_municipio):
            QMessageBox.warning(self, "Campos vacíos", "Completa todos los campos antes de guardar.")
            return

        token = getattr(GlobalState, "token", None)
        if not token or str(token).lower() in ("none", "null", ""):
            QMessageBox.warning(self, "Sin sesión", "Debe iniciar sesión antes de guardar o editar una línea.")
            return

        headers = {"Authorization": f"Bearer {token}"}

        try:
            if self.linea:
                linea_id = self.linea.get("id")
                updates = []

                if nombre_organizacion != self.linea.get("nombre_organizacion"):
                    updates.append(("nombre_organizacion", nombre_organizacion))
                if id_municipio != self.linea.get("id_municipio"):
                    updates.append(("id_municipio", id_municipio))

                if not updates:
                    QMessageBox.information(self, "Sin cambios", "No se detectaron cambios para guardar.")
                    return

                for campo, valor in updates:
                    payload = {"campo": campo, "valor": valor, "descripcion": descripcion}
                    r = requests.put(f"{API_BASE}/api/lineas/{linea_id}", json=payload, headers=headers, timeout=8)
                    if r.status_code not in (200, 201):
                        try:
                            detalle = r.json()
                        except Exception:
                            detalle = r.text
                        QMessageBox.warning(self, "Error al editar", f"{r.status_code}: {detalle}")
                        return

                QMessageBox.information(self, "Éxito", "Línea actualizada correctamente.")
                self.accept()
                return

            else:
                data = {
                    "nombre_organizacion": nombre_organizacion,
                    "id_municipio": id_municipio
                }
                r = requests.post(f"{API_BASE}/api/lineas", json=data, headers=headers, timeout=8)
                if r.status_code in (200, 201):
                    QMessageBox.information(self, "Éxito", "Línea creada correctamente.")
                    self.accept()
                    return
                try:
                    detalle = r.json()
                except Exception:
                    detalle = r.text
                QMessageBox.warning(self, "Error al crear", f"{r.status_code}: {detalle}")

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
