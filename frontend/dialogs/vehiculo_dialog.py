import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from app_state import API_BASE, GlobalState


class VehiculoDialog(QDialog):
    def __init__(self, parent=None, vehiculo=None):
        super().__init__(parent)
        self.vehiculo = vehiculo
        self.setWindowTitle("Editar Vehículo" if vehiculo else "Nuevo Vehículo")
        self.resize(480, 350)
        self.setup_ui()
        if self.vehiculo:
            self.cargar_datos()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Inicializar widgets de campos ---
        self.widgets_campos = {
            "Placa": QLineEdit(),
            "Marca": QLineEdit(),
            "Modelo": QLineEdit(),
            "Nombre propietario": QLineEdit(),
            "Cédula propietario": QLineEdit(),
            "Capacidad": QSpinBox(),
            "Litraje": QLineEdit(),
            "Sindicato / Grupo": QLineEdit(),
            "Modalidad": QComboBox(),
            "Grupo": QComboBox(),
            "Combustible": QComboBox(),
            "Línea asignada": QComboBox(),
            "Descripción": QLineEdit()
        }

        # Configurar SpinBox y combos
        self.widgets_campos["Capacidad"].setRange(0, 999)
        self.widgets_campos["Modalidad"].addItems(["Masivo", "Por puesto", "Taxi", "Mototaxi"])
        self.widgets_campos["Grupo"].addItems(["A", "B"])
        self.widgets_campos["Combustible"].addItems(["Gasolina", "Diésel"])
        self.cargar_lineas_combo_widget(self.widgets_campos["Línea asignada"])

        # --- Selección del campo a editar ---
        layout.addWidget(QLabel("Seleccionar campo a editar:"))
        self.combo_campo = QComboBox()
        self.combo_campo.addItems(list(self.widgets_campos.keys()))
        self.combo_campo.currentIndexChanged.connect(self.mostrar_campo)
        layout.addWidget(self.combo_campo)

        # --- Contenedor dinámico para el campo elegido ---
        self.campo_layout = QVBoxLayout()
        layout.addLayout(self.campo_layout)

        # --- Motivo del cambio ---
        layout.addWidget(QLabel("Motivo del cambio:"))
        self.input_motivo = QLineEdit()
        self.input_motivo.setPlaceholderText("Escriba la razón del cambio")
        layout.addWidget(self.input_motivo)

        # --- Botones ---
        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_cancelar.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(self.btn_guardar)
        btns.addWidget(self.btn_cancelar)
        layout.addLayout(btns)

        # --- Estilo compacto ---
        self.setStyleSheet("""
            QDialog {
                background-color: #f7faff;
            }
            QLabel {
                font-weight: bold;
                color: #2a4d69;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #a3c2ff;
                border-radius: 6px;
                padding: 4px 6px;
                min-width: 120px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
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

        # Mostrar el primer campo
        self.mostrar_campo()

    def mostrar_campo(self):
        # Limpiar layout dinámico
        while self.campo_layout.count():
            item = self.campo_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        campo_actual = self.combo_campo.currentText()
        widget = self.widgets_campos[campo_actual]

        self.campo_layout.addWidget(QLabel(campo_actual + ":"))
        self.campo_layout.addWidget(widget)

    def cargar_lineas_combo_widget(self, combo):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/lineas", headers=headers, timeout=6)
            if r.status_code == 200:
                combo.clear()
                for l in r.json():
                    combo.addItem(l.get("nombre_organizacion", "Sin nombre"), l.get("id"))
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar las líneas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_datos(self):
        v = self.vehiculo
        if not v:
            return

        map_fields = {
            "Placa": "placa",
            "Marca": "marca",
            "Modelo": "modelo",
            "Nombre propietario": "nombre_propietario",
            "Cédula propietario": "cedula_propietario",
            "Capacidad": "capacidad",
            "Litraje": "litraje",
            "Sindicato / Grupo": "sindicato",
            "Modalidad": "modalidad",
            "Grupo": "grupo",
            "Combustible": "combustible",
            "Línea asignada": "linea_id",
            "Descripción": "descripcion"
        }

        for campo, key in map_fields.items():
            widget = self.widgets_campos[campo]
            valor = v.get(key)
            if valor is None:
                continue
            if isinstance(widget, QLineEdit):
                widget.setText(str(valor))
            elif isinstance(widget, QSpinBox):
                try:
                    widget.setValue(int(valor))
                except Exception:
                    widget.setValue(0)
            elif isinstance(widget, QComboBox):
                index = widget.findData(valor)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    index = widget.findText(str(valor))
                    if index >= 0:
                        widget.setCurrentIndex(index)

    def guardar(self):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debe iniciar sesión.")
            return

        campo = self.combo_campo.currentText()
        widget = self.widgets_campos[campo]

        if isinstance(widget, QLineEdit):
            valor = widget.text().strip()
        elif isinstance(widget, QSpinBox):
            valor = widget.value()
        elif isinstance(widget, QComboBox):
            valor = widget.currentData() or widget.currentText()
        else:
            valor = None

        if valor in ("", None):
            QMessageBox.warning(self, "Dato requerido", f"Debe ingresar un valor para {campo}.")
            return

        motivo = self.input_motivo.text().strip()
        if not motivo:
            QMessageBox.warning(self, "Dato requerido", "Debe ingresar la razón del cambio.")
            return

        campos_api = {
            "Placa": "placa",
            "Marca": "marca",
            "Modelo": "modelo",
            "Nombre propietario": "nombre_propietario",
            "Cédula propietario": "cedula_propietario",
            "Capacidad": "capacidad",
            "Litraje": "litraje",
            "Sindicato / Grupo": "sindicato",
            "Modalidad": "modalidad",
            "Grupo": "grupo",
            "Combustible": "combustible",
            "Línea asignada": "linea_id",
            "Descripción": "descripcion"
        }

        data = {
            "campo": campos_api[campo],
            "valor": valor,
            "descripcion": motivo
        }
        headers = {"Authorization": f"Bearer {token}"}

        try:
            vid = self.vehiculo.get("id_vehiculo", self.vehiculo.get("id"))
            r = requests.put(f"{API_BASE}/api/vehiculos/{vid}", json=data, headers=headers, timeout=8)
            if r.status_code in (200, 201):
                QMessageBox.information(self, "Éxito", f"{campo} actualizado correctamente.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", f"Error al actualizar ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
