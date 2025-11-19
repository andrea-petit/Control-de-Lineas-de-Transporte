from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
import requests

from app_state import API_BASE, GlobalState
from dialogs.vehiculo_dialog import VehiculoDialog
from dialogs.chofer_asignado_dialog import ChoferAsignadoDialog  


class VehiculosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehículos")
        self.resize(1100, 620)
        self.vehiculos_cache = []
        self.setup_ui()
        self.cargar_lineas()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        lbl = QLabel("Seleccionar Línea:")
        lbl.setStyleSheet("font-weight:bold;")
        self.combo_lineas = QComboBox()
        self.combo_lineas.setMinimumWidth(420)
        self.combo_lineas.currentIndexChanged.connect(self.cargar_vehiculos_por_linea)

        top.addWidget(lbl)
        top.addWidget(self.combo_lineas)
        top.addStretch()
        layout.addLayout(top)

        self.label_titulo = QLabel("Vehículos")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight:bold; font-size:16px; margin:8px;")
        layout.addWidget(self.label_titulo)

        self.tabla = QTableWidget()
        columnas = [
            "ID", "Placa", "Marca", "Modelo", "Propietario", "Cédula",
            "Capacidad", "Litraje", "Sindicato", "Modalidad",
            "Grupo", "Combustible", "Línea", "Estado",
            "Acciones"
        ]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.setColumnHidden(0, True)

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
                border: 1px solid #c7cdd8;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.tabla)

        btns = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Vehículo")
        self.btn_agregar.clicked.connect(self.agregar_vehiculo)
        btns.addWidget(self.btn_agregar)
        btns.addStretch()
        layout.addLayout(btns)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#f4f7ff"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)


    def cargar_lineas(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"}
        try:
            r = requests.get(f"{API_BASE}/api/lineas", headers=headers, timeout=6)
            if r.ok:
                lineas = r.json()
                self.combo_lineas.clear()
                self.combo_lineas.addItem("Todas", None)
                for l in lineas:
                    self.combo_lineas.addItem(l["nombre_organizacion"], l["id"])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_vehiculos_por_linea(self):
        linea_id = self.combo_lineas.currentData()

        if linea_id:
            self.label_titulo.setText(f"Vehículos - Línea {self.combo_lineas.currentText()}")
            url = f"{API_BASE}/api/vehiculos/linea/{linea_id}"
        else:
            self.label_titulo.setText("Vehículos - Todas las líneas")
            url = f"{API_BASE}/api/vehiculos"

        headers = {"Authorization": f"Bearer {getattr(GlobalState, 'token', None)}"} if getattr(GlobalState, "token", None) else {}
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.ok:
                datos = r.json() or []
                self.vehiculos_cache = datos
                self.mostrar_vehiculos(datos)
            else:
                detalle = r.text
                try:
                    detalle = r.json()
                except Exception:
                    pass
                QMessageBox.warning(self, "Error", f"No se pudieron cargar vehículos ({r.status_code}): {detalle}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
            self.tabla.setRowCount(0)


    def mostrar_vehiculos(self, vehiculos):
        self.tabla.setRowCount(0)

        for row, v in enumerate(vehiculos):
            vid = v.get("id_vehiculo") or v.get("id")
            linea = v.get("nombre_linea") or v.get("nombre_organizacion", "")
            chofer_id = v.get("chofer_id")

            datos = [
                str(vid),
                v.get("placa", ""),
                v.get("marca", ""),
                v.get("modelo", ""),
                v.get("nombre_propietario", ""),
                str(v.get("cedula_propietario", "")),
                str(v.get("capacidad", "")),
                str(v.get("litraje", "")),
                v.get("sindicato", ""),
                v.get("modalidad", ""),
                v.get("grupo", ""),
                v.get("combustible", ""),
                linea,
                v.get("estado", "")
            ]

            self.tabla.insertRow(row)
            for col, val in enumerate(datos):
                item = QTableWidgetItem(val)
                if col in (0, 6, 7):
                    item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, col, item)

            btn_editar = QPushButton("Editar")
            btn_eliminar = QPushButton("Eliminar")
            btn_chofer = QPushButton("Chofer")

            btn_editar.clicked.connect(lambda _, _id=vid: self.editar_vehiculo(_id))
            btn_eliminar.clicked.connect(lambda _, _id=vid: self.eliminar_vehiculo(_id))
            btn_chofer.clicked.connect(lambda _, _id=vid: self.manejar_chofer(_id))

            cont = QHBoxLayout()
            cont.setContentsMargins(0, 0, 0, 0)
            cont.addWidget(btn_editar)
            cont.addWidget(btn_eliminar)
            cont.addWidget(btn_chofer)

            w = QWidget()
            w.setLayout(cont)
            self.tabla.setCellWidget(row, len(datos), w)


    def manejar_chofer(self, id_vehiculo):
        existente = None
        try:
            veh = next((x for x in getattr(self, "vehiculos_cache", []) 
                        if (x.get("id_vehiculo") or x.get("id")) == id_vehiculo), None)
            if veh is not None:
                existente = veh.get("chofer") or None
                if existente is None and veh.get("choferes"):
                    chs = veh.get("choferes") or []
                    if isinstance(chs, (list, tuple)) and chs:
                        existente = chs[0]
        except Exception:
            existente = None

        if existente is None:
            try:
                headers = {"Authorization": f"Bearer {GlobalState.token}"} if getattr(GlobalState, "token", None) else {}
                
                r = requests.get(f"{API_BASE}/api/vehiculos/{id_vehiculo}/chofer", headers=headers, timeout=4)
                if r.ok:
                    existente = r.json()
                else:
                    r2 = requests.get(f"{API_BASE}/api/vehiculos/{id_vehiculo}", headers=headers, timeout=4)
                    if r2.ok:
                        veh_full = r2.json()
                        existente = veh_full.get("chofer") or (veh_full.get("choferes") or [None])[0]
            except requests.RequestException:
                existente = None

        try:
            dlg = ChoferAsignadoDialog(parent=self, id_vehiculo=id_vehiculo, chofer_existente=existente)
            if dlg.exec():
                self.cargar_vehiculos_por_linea()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el diálogo de chofer: {e}")

    def agregar_vehiculo(self):
        dlg = VehiculoDialog(self)
        if dlg.exec():
            self.cargar_vehiculos_por_linea()

    def editar_vehiculo(self, id_vehiculo):
        headers = {"Authorization": f"Bearer {GlobalState.token}"}
        try:
            r = requests.get(f"{API_BASE}/api/vehiculos/{id_vehiculo}", headers=headers)
            if r.ok:
                dlg = VehiculoDialog(self, r.json())
                if dlg.exec():
                    self.cargar_vehiculos_por_linea()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def eliminar_vehiculo(self, id_vehiculo):
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar vehículo?",
                                    QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        descripcion, ok = QInputDialog.getText(self, "Motivo", "Descripción obligatoria:")
        if not ok or not descripcion.strip():
            return

        headers = {"Authorization": f"Bearer {GlobalState.token}"}
        payload = {"descripcion": descripcion.strip()}

        try:
            r = requests.delete(f"{API_BASE}/api/vehiculos/{id_vehiculo}",
                                headers=headers, json=payload)
            if r.ok:
                QMessageBox.information(self, "OK", "Vehículo eliminado.")
                self.cargar_vehiculos_por_linea()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

