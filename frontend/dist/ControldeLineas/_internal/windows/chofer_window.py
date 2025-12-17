import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QWidgetItem, QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState
from dialogs.chofer_dialog import ChoferDialog
from styles import estilos_paginas

class ChoferesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choferes")
        self.resize(980, 580)
        self.setup_ui()
        self.setStyleSheet(estilos_paginas)
        self.cargar_todos_choferes()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        top = QHBoxLayout()

        search_layout = QHBoxLayout()
        search_layout.setSpacing(6)
        self.txt_search_placa = QLineEdit()
        self.txt_search_placa.setPlaceholderText("Buscar por placa (ej: ABC123)")
        self.txt_search_placa.setFixedWidth(200)
        self.txt_search_placa.returnPressed.connect(self.buscar_por_placa)
        btn_search = QPushButton("Buscar")
        btn_search.setFixedHeight(28)
        btn_search.clicked.connect(self.buscar_por_placa)
        btn_clear = QPushButton("Limpiar")
        btn_clear.setFixedHeight(28)
        btn_clear.clicked.connect(self.clear_search)
        search_layout.addWidget(self.txt_search_placa)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_clear)

        top.addLayout(search_layout)
        top.addStretch()
        layout.addLayout(top)

        self.label_titulo = QLabel("Choferes")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setObjectName("titulo")
        layout.addWidget(self.label_titulo)

        self.tabla = QTableWidget()
        cols = ["ID", "Nombre", "Cédula", "Vehículo", "Acciones"]
        self.tabla.setColumnCount(len(cols))
        self.tabla.setHorizontalHeaderLabels(cols)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)  # Deshabilitar edición directa
        self.tabla.setColumnWidth(0,60)
        self.tabla.setColumnWidth(1,260)
        self.tabla.setColumnWidth(2,140)
        self.tabla.setColumnWidth(3,240)
        self.tabla.setColumnWidth(4,550)
        self.tabla.setColumnHidden(0, True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        layout.addWidget(self.tabla)


    def cargar_todos_choferes(self):
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
            btn_editar.setObjectName("btn_editar")
            btn_editar.setStyleSheet(estilos_paginas)
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setObjectName("btn_eliminar")
            btn_eliminar.setStyleSheet(estilos_paginas)
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
            self.cargar_todos_choferes()

    def editar_chofer(self, id_chofer):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/choferes/{id_chofer}", headers=headers, timeout=6)
            if r.ok:
                dlg = ChoferDialog(self, r.json())
                if dlg.exec():
                    self.cargar_todos_choferes()
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
                self.cargar_todos_choferes()
            else:
                detalle = r.text
                try: detalle = r.json()
                except: pass
                QMessageBox.warning(self, "Error", f"{r.status_code}: {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def buscar_por_placa(self):
        placa = (self.txt_search_placa.text() or "").strip()
        if not placa:
            QMessageBox.warning(self, "Placa requerida", "Ingrese la placa a buscar.")
            return
        headers = {"Authorization": f"Bearer {getattr(GlobalState, 'token', None)}"} if getattr(GlobalState, "token", None) else {}
        try:
            r = requests.get(f"{API_BASE}/api/choferes/buscar/{placa}", headers=headers, timeout=6)
            if r.ok:
                datos = r.json() or []
                if isinstance(datos, dict):
                    datos = [datos]
                self.label_titulo.setText(f"Choferes - Placa: {placa}")
                self.mostrar_choferes(datos)
                return
        except Exception:
            pass
        try:
            r2 = requests.get(f"{API_BASE}/api/vehiculos/placa/{placa}/chofer", headers=headers, timeout=6)
            if r2.ok:
                datos = r2.json()
                datos = [datos] if isinstance(datos, dict) else (datos or [])
                self.label_titulo.setText(f"Choferes - Placa: {placa}")
                self.mostrar_choferes(datos)
                return
        except Exception:
            pass

        QMessageBox.information(self, "No encontrado", f"No se encontraron choferes para la placa '{placa}'.")

    def clear_search(self):
        self.txt_search_placa.clear()
        self.cargar_todos_choferes()