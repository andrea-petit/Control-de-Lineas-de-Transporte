import requests
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QWidget, QFormLayout
)
from PySide6.QtCore import Qt
from app_state import API_BASE, GlobalState
from styles import estilos_formularios


class ChoferAsignadoDialog(QDialog):
    def __init__(self, parent=None, vehiculo=None, id_vehiculo=None, chofer_existente=None):
        super().__init__(parent)

        def _extract_placa_from_dict(d):
            if not d or not isinstance(d, dict):
                return None
            candidates = [
                "placa", "placa_vehiculo", "numero_placa", "placaVehiculo",
                "plate", "plate_number", "registro", "placa_veh"
            ]
            for k in candidates:
                v = d.get(k)
                if v:
                    return str(v)
            for k in ("vehiculo", "vehicle", "data", "attributes"):
                sub = d.get(k)
                if isinstance(sub, dict):
                    p = _extract_placa_from_dict(sub)
                    if p:
                        return p
            return None

        self.id_vehiculo = id_vehiculo or (vehiculo.get("id_vehiculo") if isinstance(vehiculo, dict) else None)
        self.vehiculo = vehiculo or {}
        self.chofer = chofer_existente

        if (not self.chofer) or (not _extract_placa_from_dict(self.vehiculo)):
            try:
                headers = {"Authorization": f"Bearer {GlobalState.token}"} if getattr(GlobalState, "token", None) else {}
                if self.id_vehiculo:
                    r = requests.get(f"{API_BASE}/api/vehiculos/{self.id_vehiculo}", headers=headers, timeout=4)
                    if r.ok:
                        veh_full = r.json() or {}
                        self.vehiculo = {**(self.vehiculo or {}), **veh_full}
                        self.chofer = self.chofer or veh_full.get("chofer") or (veh_full.get("choferes") or [None])[0]
            except Exception:
                pass

        placa = _extract_placa_from_dict(self.vehiculo) or str(self.id_vehiculo or "")
        marca_modelo= self.vehiculo.get("marca", "") + " " + self.vehiculo.get("modelo", "")
        self.setWindowTitle(f"Chofer del Vehículo {marca_modelo}: {placa}")
        self.resize(420, 260)
        self.mode = "edit" if isinstance(self.chofer, dict) and (self.chofer.get("nombre") or self.chofer.get("cedula")) else "add"
        self.setup_ui(placa, marca_modelo)
        self.setStyleSheet(estilos_formularios)

    def setup_ui(self, placa, marca_modelo):
        layout = QVBoxLayout(self)

        lbl_title = QLabel(f"Vehículo: {marca_modelo}: {placa}")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        if self.mode == "add":
            form = QFormLayout()
            self.txt_nombre = QLineEdit()
            self.txt_cedula = QLineEdit()
            self.txt_telefono = QLineEdit()
            form.addRow("Nombre completo:", self.txt_nombre)
            form.addRow("Cédula:", self.txt_cedula)
            layout.addLayout(form)

            btns = QHBoxLayout()
            btn_add = QPushButton("Agregar")
            btn_cancel = QPushButton("Cancelar")
            btn_cancel.setObjectName("cancelar")
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_cancel.setCursor(Qt.PointingHandCursor)
            
            btn_add.clicked.connect(self.guardar)
            btn_cancel.clicked.connect(self.reject)
            btns.addWidget(btn_add)
            btns.addWidget(btn_cancel)
            layout.addLayout(btns)

        else:
            current_info = QWidget()
            fl = QFormLayout(current_info)
            nombre_actual = self.chofer.get("nombre", "")
            cedula_actual = str(self.chofer.get("cedula", ""))
            fl.addRow("Nombre actual:", QLabel(nombre_actual))
            fl.addRow("Cédula actual:", QLabel(cedula_actual))
            layout.addWidget(current_info)

            edit_row = QHBoxLayout()
            self.combo_campo = QComboBox()
            self.field_map = [("nombre", "Nombre"), ("cedula", "Cédula")]
            for key, label in self.field_map:
                self.combo_campo.addItem(label, key)
            self.input_nuevo = QLineEdit()
            self.input_nuevo.setPlaceholderText("Nuevo valor...")
            edit_row.addWidget(self.combo_campo)
            edit_row.addWidget(self.input_nuevo)
            layout.addLayout(edit_row)

            btns = QHBoxLayout()
            btn_save = QPushButton("Guardar cambio")
            btn_cancel = QPushButton("Cancelar")
            btn_cancel.setObjectName("cancelar")
            btn_save.setCursor(Qt.PointingHandCursor)
            btn_cancel.setCursor(Qt.PointingHandCursor)

            btn_save.clicked.connect(self.guardar)
            btn_cancel.clicked.connect(self.reject)
            btns.addWidget(btn_save)
            btns.addWidget(btn_cancel)
            layout.addLayout(btns)

    def guardar(self):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "Error", "Sesión no válida.")
            return
        headers = {"Authorization": f"Bearer {token}"}

        try:
            if self.mode == "add":
                nombre = self.txt_nombre.text().strip()
                cedula = self.txt_cedula.text().strip()
                telefono = self.txt_telefono.text().strip()
                if not nombre or not cedula:
                    QMessageBox.warning(self, "Campos incompletos", "Nombre y Cédula son obligatorios.")
                    return
                payload = {
                    "id_vehiculo": self.id_vehiculo,
                    "nombre": nombre,
                    "cedula": cedula,
                    "telefono": telefono,
                }
                r = requests.post(f"{API_BASE}/api/choferes", json=payload, headers=headers, timeout=8)
                if r.status_code in (200, 201):
                    QMessageBox.information(self, "Éxito", "Chofer agregado correctamente.")
                    self.accept()
                else:
                    detalle = r.text
                    try: detalle = r.json()
                    except Exception: pass
                    QMessageBox.warning(self, "Error", f"No se pudo agregar chofer ({r.status_code}): {detalle}")
            else:
                cid = self.chofer.get("id_chofer") or self.chofer.get("id")
                if not cid:
                    QMessageBox.warning(self, "Error", "Id de chofer no disponible para editar.")
                    return
                campo = self.combo_campo.currentData()
                valor = self.input_nuevo.text().strip()
                if not valor:
                    QMessageBox.warning(self, "Campo vacío", "Ingrese el nuevo valor para el campo seleccionado.")
                    return
                payload = {"campo": campo, "valor": valor}
                r = requests.put(f"{API_BASE}/api/choferes/{cid}", json=payload, headers=headers, timeout=8)
                if r.status_code == 200:
                    QMessageBox.information(self, "Éxito", "Chofer actualizado correctamente.")
                    self.accept()
                else:
                    detalle = r.text
                    try: detalle = r.json()
                    except Exception: pass
                    QMessageBox.warning(self, "Error", f"No se pudo actualizar chofer ({r.status_code}): {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")
