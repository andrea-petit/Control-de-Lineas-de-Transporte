import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState
from dialogs.vehiculo_dialog import VehiculoDialog


class VehiculosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vehículos")
        self.resize(1100, 620)
        self.setup_ui()
        self.cargar_lineas() 

    def setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        lbl = QLabel("Seleccionar Línea:")
        lbl.setStyleSheet("font-weight:bold;")
        self.combo_lineas = QComboBox()
        self.combo_lineas.setMinimumWidth(520)
        self.combo_lineas.setStyleSheet("""
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
        self.combo_lineas.currentIndexChanged.connect(self.cargar_vehiculos_por_linea)
        top.addWidget(lbl)
        top.addWidget(self.combo_lineas)
        top.addStretch()
        layout.addLayout(top)

        self.label_titulo = QLabel("Vehículos")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px; color: #002b80;")
        layout.addWidget(self.label_titulo)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("background-color: #f4f7ff; gridline-color: #dcdcdc;")

        columns = [
            "Id", "Placa", "Marca", "Modelo", "Propietario", "Cédula",
            "Capacidad", "Litraje", "Sindicato", "Modalidad", "Grupo",
            "Combustible", "Línea", "Estado", "Acciones"
        ]
        self.tabla.setColumnCount(len(columns))
        self.tabla.setHorizontalHeaderLabels(columns)
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setColumnHidden(0, True)
        # anchos recomendados
        widths = [60, 110, 120, 120, 200, 120, 80, 90, 120, 100, 100, 100, 160, 160]
        for idx, w in enumerate(widths):
            try:
                self.tabla.setColumnWidth(idx, w)
            except Exception:
                pass


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

        # botones
        btns = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Vehículo")
        self.btn_agregar.clicked.connect(self.agregar_vehiculo)
        btns.addWidget(self.btn_agregar)
        # btns.addStretch()
        layout.addLayout(btns)

        # paleta/estilo coherente con lineas
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#f4f7ff"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def cargar_lineas(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/lineas", headers=headers, timeout=6)
            if r.status_code == 200:
                lineas = r.json()
                self.combo_lineas.clear()
                self.combo_lineas.addItem("Todas", None)
                for l in lineas:
                    # usar clave 'id' tal como devuelve linea_routes
                    self.combo_lineas.addItem(l.get("nombre_organizacion", "Sin nombre"), l.get("id"))
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar las líneas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_vehiculos_por_linea(self):
        linea_id = self.combo_lineas.currentData()
        nombre = self.combo_lineas.currentText()
        if linea_id:
            self.label_titulo.setText(f"Vehículos - Línea: {nombre}")
            url = f"{API_BASE}/api/vehiculos/linea/{linea_id}"
        else:
            self.label_titulo.setText("Vehículos - Todas las líneas")
            url = f"{API_BASE}/api/vehiculos"

        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                vehiculos = r.json()
                self.mostrar_vehiculos(vehiculos)
            else:
                QMessageBox.warning(self, "Error", f"No se pudieron cargar vehículos ({r.status_code})")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def mostrar_vehiculos(self, vehiculos):
        self.tabla.setRowCount(0)
        for row, v in enumerate(vehiculos):
            vid = v.get("id_vehiculo", v.get("id"))
            self.tabla.insertRow(row)
            # vid = v.get("id_vehiculo", v.get("id"))
            placa = v.get("placa", "")
            marca = v.get("marca", "")
            modelo = v.get("modelo", "")
            propietario = v.get("nombre_propietario", "")
            cedula = v.get("cedula_propietario", "")
            capacidad = str(v.get("capacidad", "") or "")
            litraje = str(v.get("litraje", "") or "")
            sindicato = v.get("sindicato", "")
            modalidad = v.get("modalidad", "")
            grupo = v.get("grupo", "")
            combustible = v.get("combustible", "")
            linea_nombre = v.get("linea_nombre_organizacion") or v.get("nombre_organizacion") or str(v.get("linea_id", v.get("id_linea", "")))
            estado = v.get("estado", "")



            items = [
                str(vid or ""),
                placa,
                marca,
                modelo,
                propietario,
                str(cedula),
                capacidad,
                litraje,
                sindicato,
                modalidad,
                grupo,
                combustible,
                str(linea_nombre),
                estado
            ]

            for col, text in enumerate(items):
                it = QTableWidgetItem(text)
                # centrar columnas numéricas / id / capacidad
                if col in (0, 6, 7):
                    it.setTextAlignment(Qt.AlignCenter)
                if col == 13:  # estado
                    if estado.lower() == "inactivo":
                        it.setBackground(QColor("#f87171"))  # rojo claro
                    elif estado.lower()== "deshabilitado":
                        it.setBackground(QColor("#f8ef71"))
                self.tabla.setItem(row, col, it)

            # acciones (editar / eliminar)
            btn_editar = QPushButton("Editar")
            btn_eliminar = QPushButton("Eliminar")
            for btn in (btn_editar, btn_eliminar):
                btn.setFixedSize(70, 28)
                btn_editar.setStyleSheet("background-color: #2a4d69; color: white; border-radius: 4px;")
                btn_eliminar.setStyleSheet("background-color: #2a4d69; color: white; border-radius: 4px;")
                btn.setCursor(Qt.PointingHandCursor)

            btn_editar.clicked.connect(lambda _, _id=vid: self.editar_vehiculo(_id))
            btn_eliminar.clicked.connect(lambda _, _id=vid: self.eliminar_vehiculo(_id))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.addWidget(btn_editar)
            action_layout.addWidget(btn_eliminar)
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.tabla.setCellWidget(row, len(items), action_widget)

    def agregar_vehiculo(self):
        dlg = VehiculoDialog(self)
        if dlg.exec():
            self.cargar_vehiculos_por_linea()

    def editar_vehiculo(self, id_vehiculo):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/vehiculos/{id_vehiculo}", headers=headers, timeout=6)
            if r.status_code == 200:
                veh = r.json()
                dlg = VehiculoDialog(self, veh)
                if dlg.exec():
                    self.cargar_vehiculos_por_linea()
            else:
                QMessageBox.warning(self, "Error", "No se pudo obtener el vehículo")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def eliminar_vehiculo(self, id_vehiculo):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debes iniciar sesión.")
            return

        resp = QMessageBox.question(self, "Confirmar eliminación",
                                    "¿Está seguro de eliminar este vehículo?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return

        descripcion, ok = QInputDialog.getText(self, "Descripción de eliminación",
                                               "Ingrese motivo / descripción (obligatorio):")
        if not ok or not descripcion.strip():
            QMessageBox.warning(self, "Descripción requerida", "Debe ingresar una descripción para eliminar.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"descripcion": descripcion.strip()}
        try:
            r = requests.delete(f"{API_BASE}/api/vehiculos/{id_vehiculo}", headers=headers, json=payload, timeout=8)
            if r.status_code == 200:
                QMessageBox.information(self, "Éxito", "Vehículo eliminado correctamente.")
                self.cargar_vehiculos_por_linea()
            else:
                try:
                    detalle = r.json()
                except Exception:
                    detalle = r.text
                QMessageBox.warning(self, "Error al eliminar", f"{r.status_code}: {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

