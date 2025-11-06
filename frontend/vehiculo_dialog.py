import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QSpinBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState


class VehiculoDialog(QDialog):
    def __init__(self, parent=None, vehiculo=None):
        super().__init__(parent)
        self.vehiculo = vehiculo
        self.setWindowTitle("Editar Vehículo" if vehiculo else "Nuevo Vehículo")
        self.resize(520, 460)
        self.setup_ui()
        self.cargar_lineas_combo()
        if self.vehiculo:
            self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)

        # ---------- Campos ----------
        self.input_placa = QLineEdit()
        self.input_marca = QLineEdit()
        self.input_modelo = QLineEdit()
        self.input_propietario = QLineEdit()
        self.input_cedula = QLineEdit()
        self.spin_capacidad = QSpinBox()
        self.spin_capacidad.setRange(0, 999)
        self.input_litraje = QLineEdit()

        self.input_sindicato = QLineEdit()

        # Combos con opciones fijas
        self.combo_modalidad = QComboBox()
        self.combo_modalidad.addItems(["Masivo", "Por puesto", "Taxi", "Mototaxi"])
        self.combo_grupo = QComboBox()
        self.combo_grupo.addItems(["A", "B"])
        self.combo_combustible = QComboBox()
        self.combo_combustible.addItems(["Gasolina", "Diésel"])

        self.combo_linea = QComboBox()
        self.input_descripcion = QLineEdit()

        # ---------- Añadir al formulario ----------
        form.addRow("Placa:", self.input_placa)
        form.addRow("Marca:", self.input_marca)
        form.addRow("Modelo:", self.input_modelo)
        form.addRow("Nombre propietario:", self.input_propietario)
        form.addRow("Cédula propietario:", self.input_cedula)
        form.addRow("Capacidad:", self.spin_capacidad)
        form.addRow("Litraje:", self.input_litraje)
        form.addRow("Sindicato / Grupo:", self.input_sindicato)
        form.addRow("Modalidad:", self.combo_modalidad)
        form.addRow("Grupo:", self.combo_grupo)
        form.addRow("Combustible:", self.combo_combustible)
        form.addRow("Línea asignada:", self.combo_linea)
        form.addRow("Descripción (opcional):", self.input_descripcion)

        layout.addLayout(form)

        # ---------- Botones ----------
        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(self.btn_guardar)
        btns.addWidget(self.btn_cancelar)
        layout.addLayout(btns)

        # ---------- Estilo ----------
        self.setStyleSheet("""
            QDialog {
                background-color: #f7faff;
            }
            QLabel {
                font-weight: bold;
                color: #2a4d69;
                margin-bottom: 3px;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #a3c2ff;
                border-radius: 6px;
                padding: 6px;
                background-color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #4a90e2;
                background-color: #f0f6ff;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
            QPushButton#cancelar {
                background-color: #e74c3c;
            }
            QPushButton#cancelar:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.setCursor(Qt.PointingHandCursor)
        self.btn_cancelar.setObjectName("cancelar")

    # -------------------------------------------------------------------------
    def cargar_lineas_combo(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/lineas", headers=headers, timeout=6)
            if r.status_code == 200:
                lineas = r.json()
                self.combo_linea.clear()
                for l in lineas:
                    self.combo_linea.addItem(l.get("nombre_organizacion", "Sin nombre"), l.get("id"))
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar las líneas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    # -------------------------------------------------------------------------
    def cargar_datos(self):
        v = self.vehiculo
        self.input_placa.setText(v.get("placa", ""))
        self.input_marca.setText(v.get("marca", ""))
        self.input_modelo.setText(v.get("modelo", ""))
        self.input_propietario.setText(v.get("nombre_propietario", ""))
        self.input_cedula.setText(v.get("cedula_propietario", ""))
        try:
            self.spin_capacidad.setValue(int(v.get("capacidad") or 0))
        except Exception:
            self.spin_capacidad.setValue(0)
        self.input_litraje.setText(str(v.get("litraje", "")))
        self.input_sindicato.setText(v.get("sindicato", ""))

        # Combos
        if v.get("modalidad"):
            i = self.combo_modalidad.findText(v["modalidad"], Qt.MatchFixedString)
            if i >= 0: self.combo_modalidad.setCurrentIndex(i)
        if v.get("grupo"):
            i = self.combo_grupo.findText(v["grupo"], Qt.MatchFixedString)
            if i >= 0: self.combo_grupo.setCurrentIndex(i)
        if v.get("combustible"):
            i = self.combo_combustible.findText(v["combustible"], Qt.MatchFixedString)
            if i >= 0: self.combo_combustible.setCurrentIndex(i)

        idx = self.combo_linea.findData(v.get("linea_id", v.get("id_linea", None)))
        if idx >= 0:
            self.combo_linea.setCurrentIndex(idx)

    # -------------------------------------------------------------------------
    def guardar(self):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debe iniciar sesión.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        descripcion = self.input_descripcion.text().strip()

        data = {
            "placa": self.input_placa.text().strip(),
            "marca": self.input_marca.text().strip(),
            "modelo": self.input_modelo.text().strip(),
            "nombre_propietario": self.input_propietario.text().strip(),
            "cedula_propietario": self.input_cedula.text().strip(),
            "capacidad": self.spin_capacidad.value(),
            "litraje": self.input_litraje.text().strip(),
            "sindicato": self.input_sindicato.text().strip(),
            "modalidad": self.combo_modalidad.currentText(),
            "grupo": self.combo_grupo.currentText(),
            "combustible": self.combo_combustible.currentText(),
            "linea_id": self.combo_linea.currentData(),
            "descripcion": descripcion or None
        }

        if not data["placa"] or not data["linea_id"]:
            QMessageBox.warning(self, "Datos incompletos", "Placa y línea son obligatorias.")
            return

        try:
            if self.vehiculo:
                vid = self.vehiculo.get("id_vehiculo", self.vehiculo.get("id"))
                r = requests.put(f"{API_BASE}/api/vehiculos/{vid}", json=data, headers=headers, timeout=8)
                if r.status_code in (200, 201):
                    QMessageBox.information(self, "Éxito", "Vehículo actualizado correctamente.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", f"Error al actualizar ({r.status_code})")
            else:
                r = requests.post(f"{API_BASE}/api/vehiculos", json=data, headers=headers, timeout=8)
                if r.status_code in (200, 201):
                    QMessageBox.information(self, "Éxito", "Vehículo creado correctamente.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", f"Error al crear ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
