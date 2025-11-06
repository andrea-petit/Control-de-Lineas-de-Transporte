import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from app_state import API_BASE, GlobalState

class ChoferDialog(QDialog):
    def __init__(self, parent=None, chofer=None):
        super().__init__(parent)
        self.chofer = chofer
        self.setWindowTitle("Editar Chofer" if chofer else "Nuevo Chofer")
        self.resize(420, 260)
        self.setup_ui()
        self.cargar_vehiculos()
        if self.chofer:
            self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nombre:"))
        self.input_nombre = QLineEdit()
        layout.addWidget(self.input_nombre)

        layout.addWidget(QLabel("Cédula:"))
        self.input_cedula = QLineEdit()
        layout.addWidget(self.input_cedula)

        layout.addWidget(QLabel("Vehículo asignado:"))
        self.combo_vehiculo = QComboBox()
        layout.addWidget(self.combo_vehiculo)

        layout.addWidget(QLabel("Descripción (registro de cambio, opcional):"))
        self.input_descripcion = QLineEdit()
        layout.addWidget(self.input_descripcion)

        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(self.btn_guardar)
        btns.addWidget(self.btn_cancelar)
        layout.addLayout(btns)

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

    def cargar_vehiculos(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/vehiculos", headers=headers, timeout=6)
            if r.ok:
                vehiculos = r.json()
                self.combo_vehiculo.clear()
                self.combo_vehiculo.addItem("Sin vehículo", None)
                for v in vehiculos:
                    label = f"{v.get('placa','')} - {v.get('marca','')} {v.get('modelo','')}".strip()
                    vid = v.get("id_vehiculo", v.get("id"))
                    self.combo_vehiculo.addItem(label or str(vid), vid)
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar vehículos")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_datos(self):
        c = self.chofer
        self.input_nombre.setText(c.get("nombre",""))
        self.input_cedula.setText(str(c.get("cedula","")))
        idx = self.combo_vehiculo.findData(c.get("id_vehiculo"))
        if idx >= 0:
            self.combo_vehiculo.setCurrentIndex(idx)

    def guardar(self):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debe iniciar sesión.")
            return
        headers = {"Authorization": f"Bearer {token}"}
        descripcion = self.input_descripcion.text().strip()

        if self.chofer:
            cid = self.chofer.get("id_chofer", self.chofer.get("id"))
            updates = []
            def add_if_changed(key, new):
                old = self.chofer.get(key)
                if (old is None and new) or (str(old) != str(new)):
                    updates.append((key, new))
            add_if_changed("nombre", self.input_nombre.text().strip())
            add_if_changed("cedula", self.input_cedula.text().strip())
            add_if_changed("id_vehiculo", self.combo_vehiculo.currentData())

            if not updates:
                QMessageBox.information(self, "Sin cambios", "No hay cambios para guardar.")
                return
            try:
                for campo, valor in updates:
                    payload = {"campo": campo, "valor": valor, "descripcion": descripcion}
                    r = requests.put(f"{API_BASE}/api/choferes/{cid}", json=payload, headers=headers, timeout=8)
                    if r.status_code not in (200,201):
                        detalle = r.text
                        try: detalle = r.json()
                        except: pass
                        QMessageBox.warning(self, "Error", f"{r.status_code}: {detalle}")
                        return
                QMessageBox.information(self, "Éxito", "Chofer actualizado.")
                self.accept()
            except requests.RequestException as e:
                QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
        else:
            payload = {
                "nombre": self.input_nombre.text().strip(),
                "cedula": self.input_cedula.text().strip(),
                "id_vehiculo": self.combo_vehiculo.currentData(),
                "descripcion": descripcion or None
            }
            if not payload["nombre"] or not payload["cedula"]:
                QMessageBox.warning(self, "Datos incompletos", "Nombre y cédula son obligatorios.")
                return
            try:
                r = requests.post(f"{API_BASE}/api/choferes", json=payload, headers=headers, timeout=8)
                if r.status_code in (200,201):
                    QMessageBox.information(self, "Éxito", "Chofer creado.")
                    self.accept()
                else:
                    detalle = r.text
                    try: detalle = r.json()
                    except: pass
                    QMessageBox.warning(self, "Error", f"{r.status_code}: {detalle}")
            except requests.RequestException as e:
                QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")