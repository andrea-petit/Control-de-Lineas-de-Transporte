from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from app_state import API_BASE, GlobalState
from dialogs.lineas_dialog import LineaDialog
import requests


class LineasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Líneas de Transporte")
        self.resize(900, 600)
        self.setup_ui()
        self.cargar_municipios()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)


        top_layout = QHBoxLayout()

        lbl_muni = QLabel("Seleccionar Municipio:")
        lbl_muni.setStyleSheet("font-weight: bold; font-size: 14px; color: #003366;")

        self.combo_municipios = QComboBox()
        self.combo_municipios.setMinimumWidth(300)
        self.combo_municipios.setStyleSheet("""
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
        self.combo_municipios.currentIndexChanged.connect(self.cargar_lineas)

        top_layout.addWidget(lbl_muni)
        top_layout.addWidget(self.combo_municipios)
        top_layout.addStretch()
        layout.addLayout(top_layout)



        self.label_titulo = QLabel("")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px; color: #002b80;")
        layout.addWidget(self.label_titulo)

    

    
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)  
        self.tabla.setHorizontalHeaderLabels(["Nombre de Organización", "Acciones"])
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.setColumnWidth(0, 730)
        self.tabla.setColumnWidth(1, 475)  

        # self.tabla.setStyleSheet("""
        #     QHeaderView::section {
        #         background-color: #b3ccff;
        #         color: #002b80;
        #         font-weight: bold;
        #         padding: 5px;
        #     }
        #     QTableWidget {
        #         background-color: #f8fbff;
        #         border: 1px solid #a3c2ff;
        #         gridline-color: #a3c2ff;
        #     }
        # """)

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


        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Línea")
        self.btn_agregar.setFixedWidth(160)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #4d79ff;
                color: white;
                font-weight: bold;
                padding: 8px 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3355cc;
            }
        """)
        self.btn_agregar.clicked.connect(self.agregar_linea)

        btn_layout.addWidget(self.btn_agregar)
        # btn_layout.addStretch()
        layout.addLayout(btn_layout)

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#eaf1ff"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def cargar_municipios(self):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/municipios/nombres", headers=headers)
            if r.status_code == 200:
                municipios = r.json()
                self.combo_municipios.clear()
                for m in municipios:
                    self.combo_municipios.addItem(m['nombre'], m.get('id_municipio', m.get('id')))
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar los municipios")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def cargar_lineas(self):
        id_municipio = self.combo_municipios.currentData()
        nombre_municipio = self.combo_municipios.currentText()
        if not id_municipio:
            return

        self.label_titulo.setText(f"Líneas de transporte - Municipio {nombre_municipio}")

        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/lineas/municipio/{id_municipio}", headers=headers)
            if r.status_code == 200:
                lineas = r.json()
                self.mostrar_lineas(lineas)
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar las líneas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def mostrar_lineas(self, lineas):
        self.tabla.setRowCount(0)
        for row, l in enumerate(lineas):
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(l['nombre_organizacion']))

            btn_editar = QPushButton("Editar")
            btn_eliminar = QPushButton("Eliminar")

            for btn in (btn_editar, btn_eliminar):
                btn.setFixedSize(50, 28)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4d79ff;
                        color: white;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #3355cc;
                    }
                """)

            btn_editar.clicked.connect(lambda _, lid=l['id']: self.editar_linea(lid))
            btn_eliminar.clicked.connect(lambda _, lid=l['id']: self.eliminar_linea(lid))

            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(6)
            action_layout.addWidget(btn_editar)
            action_layout.addWidget(btn_eliminar)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.tabla.setCellWidget(row, 1, action_widget)

    def agregar_linea(self):
        dlg = LineaDialog(self)
        if dlg.exec():
            self.cargar_lineas()

    def editar_linea(self, id_linea):
        headers = {"Authorization": f"Bearer {GlobalState.token}"} if GlobalState.token else {}
        try:
            r = requests.get(f"{API_BASE}/api/lineas/{id_linea}", headers=headers)
            if r.status_code == 200:
                linea = r.json()
 
                dlg = LineaDialog(self, linea)
                if dlg.exec():
                    self.cargar_lineas()
            else:
                QMessageBox.warning(self, "Error", "No se pudo obtener la línea")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def eliminar_linea(self, linea_id):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debes iniciar sesión.")
            return

        resp = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Está seguro que desea eliminar la línea seleccionada?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resp != QMessageBox.Yes:
            return

        descripcion, ok = QInputDialog.getText(
            self, "Descripción de eliminación",
            "Ingrese motivo / descripción (obligatorio):"
        )
        if not ok or not descripcion.strip():
            QMessageBox.warning(self, "Descripción requerida", "Debe ingresar una descripción para eliminar.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"descripcion": descripcion.strip()}
        try:
            r = requests.delete(f"{API_BASE}/api/lineas/{linea_id}", headers=headers, json=payload, timeout=8)
            if r.status_code == 200:
                QMessageBox.information(self, "Éxito", "Línea eliminada correctamente.")
                self.cargar_lineas()
            else:
                detalle = r.text
                QMessageBox.warning(self, "Error al eliminar", f"{r.status_code}: {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

