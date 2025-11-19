import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState
from dialogs.chofer_dialog import ChoferDialog

class ChoferesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choferes")
        self.resize(980, 580)
        self.setup_ui()
        self.cargar_vehiculos()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        lbl = QLabel("Filtrar por Vehículo:")
        lbl.setStyleSheet("font-weight:bold;")
        self.combo_veh = QComboBox()
        self.combo_veh.setMinimumWidth(360)
        self.combo_veh.setStyleSheet("""
            QComboBox {
                background-color: #e6f0ff;
                border: 1px solid #a3c2ff;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                width: 25px;
            }
        """)
        self.combo_veh.currentIndexChanged.connect(self.cargar_choferes_por_vehiculo)
        top.addWidget(lbl)
        top.addWidget(self.combo_veh)
        top.addStretch()
        layout.addLayout(top)

        self.label_titulo = QLabel("Choferes")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight:bold; font-size:16px; margin:8px;")
        layout.addWidget(self.label_titulo)

        self.tabla = QTableWidget()
        cols = ["ID", "Nombre", "Cédula", "Vehículo", "Acciones"]
        self.tabla.setColumnCount(len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setColumnWidth(0,60)
        self.tabla.setColumnWidth(1,260)
        self.tabla.setColumnWidth(2,140)
        self.tabla.setColumnWidth(3,240)
        self.tabla.setColumnWidth(4,800)
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
                padding: 6px;
                border: 1px solid #c7cdd8;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.tabla)

        btns = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Chofer")
        self.btn_agregar.clicked.connect(self.agregar_chofer)
        btns.addWidget(self.btn_agregar)
        layout.addLayout(btns)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#f4f7ff"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def cargar_vehiculos(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/vehiculos", headers=headers, timeout=6)
            if r.ok:
                veh = r.json()
                self.combo_veh.clear()
                self.combo_veh.addItem("Todos", None)
                for v in veh:
                    label = f"{v.get('placa','')} - {v.get('marca','')}"
                    vid = v.get("id_vehiculo", v.get("id"))
                    self.combo_veh.addItem(label or str(vid), vid)
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar vehículos")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_choferes_por_vehiculo(self):
        vid = self.combo_veh.currentData()
        if vid:
            url = f"{API_BASE}/api/choferes/vehiculo/{vid}"
            self.label_titulo.setText(f"Choferes - Vehículo: {self.combo_veh.currentText()}")
        else:
            url = f"{API_BASE}/api/choferes"
            self.label_titulo.setText("Choferes - Todos")
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.ok:
                self.mostrar_choferes(r.json())
            else:
                QMessageBox.warning(self, "Error", f"No se pudieron cargar choferes ({r.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def mostrar_choferes(self, choferes):
        self.tabla.setRowCount(0)
        for row, c in enumerate(choferes):
            self.tabla.insertRow(row)
            cid = c.get("id_chofer", c.get("id"))
            nombre = c.get("nombre","")
            cedula = str(c.get("cedula",""))
            vehiculo = str(c.get("vehiculo_placa",""))
            marca_modelo = f"{c.get('vehiculo_marca','')} {c.get('vehiculo_modelo','')}".strip()
            self.tabla.setItem(row, 0, QTableWidgetItem(str(cid)))
            self.tabla.setItem(row, 1, QTableWidgetItem(nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(cedula))
            self.tabla.setItem(row, 3, QTableWidgetItem(vehiculo + (" - " + marca_modelo if marca_modelo else "")))

            btn_editar = QPushButton("Editar")
            btn_eliminar = QPushButton("Eliminar")
            for btn in (btn_editar, btn_eliminar):
                btn.setFixedSize(70,28)
                btn_editar.setStyleSheet("background-color: #2a4d69; color: white; border-radius: 4px;")
                btn_eliminar.setStyleSheet("background-color: #2a4d69; color: white; border-radius: 4px;")
                
                btn.setCursor(Qt.PointingHandCursor)


            btn_editar.clicked.connect(lambda _, _id=cid: self.editar_chofer(_id))
            btn_eliminar.clicked.connect(lambda _, _id=cid: self.eliminar_chofer(_id))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2,2,2,2)
            action_layout.addWidget(btn_editar)
            action_layout.addWidget(btn_eliminar)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.tabla.setCellWidget(row, 4, action_widget)

    def mostrar_choferes(self, choferes):
        self.tabla.setRowCount(0)
        for row, c in enumerate(choferes):
            self.tabla.insertRow(row)
            cid = c.get("id_chofer", c.get("id"))
            nombre = c.get("nombre","")
            cedula = str(c.get("cedula",""))
            vehiculo = str(c.get("vehiculo_placa",""))
            marca_modelo = f"{c.get('vehiculo_marca','')} {c.get('vehiculo_modelo','')}".strip()
            self.tabla.setItem(row, 0, QTableWidgetItem(str(cid)))
            self.tabla.setItem(row, 1, QTableWidgetItem(nombre))
            self.tabla.setItem(row, 2, QTableWidgetItem(cedula))
            self.tabla.setItem(row, 3, QTableWidgetItem(vehiculo + (" - " + marca_modelo if marca_modelo else "")))

            btn_editar = QPushButton("Editar")
            btn_eliminar = QPushButton("Eliminar")
            for btn in (btn_editar, btn_eliminar):
                btn.setFixedSize(70,28)
                btn.setCursor(Qt.PointingHandCursor)
            btn_editar.clicked.connect(lambda _, _id=cid: self.editar_chofer(_id))
            btn_eliminar.clicked.connect(lambda _, _id=cid: self.eliminar_chofer(_id))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2,2,2,2)
            action_layout.addWidget(btn_editar)
            action_layout.addWidget(btn_eliminar)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.tabla.setCellWidget(row, 4, action_widget)

    def agregar_chofer(self):
        dlg = ChoferDialog(self)
        if dlg.exec():
            self.cargar_choferes_por_vehiculo()

    def editar_chofer(self, id_chofer):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/choferes/{id_chofer}", headers=headers, timeout=6)
            if r.ok:
                dlg = ChoferDialog(self, r.json())
                if dlg.exec():
                    self.cargar_choferes_por_vehiculo()
            else:
                QMessageBox.warning(self, "Error", "No se pudo obtener chofer")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def eliminar_chofer(self, id_chofer):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debes iniciar sesión.")
            return
        resp = QMessageBox.question(self, "Confirmar eliminación",
                                    "¿Desea eliminar este chofer?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        descripcion, ok = QInputDialog.getText(self, "Descripción de eliminación",
                                               "Ingrese motivo / descripción (obligatorio):")
        if not ok or not descripcion.strip():
            QMessageBox.warning(self, "Descripción requerida", "Debe ingresar una descripción.")
            return
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"descripcion": descripcion.strip()}
        try:
            r = requests.delete(f"{API_BASE}/api/choferes/{id_chofer}", headers=headers, json=payload, timeout=8)
            if r.status_code == 200:
                QMessageBox.information(self, "Éxito", "Chofer eliminado.")
                self.cargar_choferes_por_vehiculo()
            else:
                detalle = r.text
                try: detalle = r.json()
                except: pass
                QMessageBox.warning(self, "Error", f"{r.status_code}: {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")