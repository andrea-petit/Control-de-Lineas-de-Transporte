from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QSpinBox, QMessageBox
)

from PySide6.QtGui import QIcon

from PySide6.QtCore import Qt
import requests
from app_state import API_BASE, GlobalState, resources_path


class MantenimientoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mantenimiento / Servicio Técnico")
        self.setWindowIcon(QIcon(resources_path("frontend/icons/bus.png")))
        self.resize(900, 600)
        self.setup_ui()
        self.cargar_resumen()
        self.cargar_logs()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Panel de Mantenimiento")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        header.addWidget(title)
        header.addStretch()

        btn_refresh = QPushButton("Refrescar resumen")
        btn_refresh.clicked.connect(self.cargar_resumen)
        header.addWidget(btn_refresh)

        layout.addLayout(header)

        self.resumen = QTextEdit()
        self.resumen.setReadOnly(True)
        self.resumen.setFixedHeight(160)
        layout.addWidget(self.resumen)

        logs_header = QHBoxLayout()
        logs_header.addWidget(QLabel("Logs recientes:"))
        logs_header.addStretch()

        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 1000)
        self.spin_count.setValue(100)
        logs_header.addWidget(QLabel("Cantidad:"))
        logs_header.addWidget(self.spin_count)

        btn_load = QPushButton("Cargar logs")
        btn_load.clicked.connect(self.cargar_logs)
        logs_header.addWidget(btn_load)

        btn_clean = QPushButton("Limpiar logs")
        btn_clean.clicked.connect(self.limpiar_logs)
        logs_header.addWidget(btn_clean)

        layout.addLayout(logs_header)

        self.lista_logs = QListWidget()
        layout.addWidget(self.lista_logs)

        acciones = QHBoxLayout()

        btn_db = QPushButton("Probar DB")
        btn_db.clicked.connect(self.probar_db)
        acciones.addWidget(btn_db)

        acciones.addStretch()

        layout.addLayout(acciones)

    def _auth_headers(self):
        token = getattr(GlobalState, "token", None)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def cargar_resumen(self):
        try:
            r = requests.get(f"{API_BASE}/api/mantenimiento/resumen", timeout=6)
            if r.ok:
                data = r.json()
                texto = (
                    f"Fecha: {data.get('fecha')}\n"
                    f"IP Servidor: {data.get('ip_servidor')}\n"
                    f"DB conectada: {data.get('db_conectada')}\n"
                    f"Mensaje DB: {data.get('mensaje_db')}\n"
                )
                self.resumen.setPlainText(texto)

                logs = data.get("logs_recientes") or []
                self.lista_logs.clear()
                for l in logs:
                    self.lista_logs.addItem(QListWidgetItem(l))
            else:
                self.resumen.setPlainText(f"Error cargando resumen ({r.status_code})")
        except requests.RequestException as e:
            self.resumen.setPlainText(f"No se pudo conectar al servidor:\n{e}")

    def cargar_logs(self):
        count = int(self.spin_count.value())
        try:
            r = requests.get(f"{API_BASE}/api/mantenimiento/logs", params={"count": count}, timeout=6)
            if r.ok:
                payload = r.json()
                logs = payload.get("logs") or []
                self.lista_logs.clear()
                for l in logs:
                    self.lista_logs.addItem(QListWidgetItem(str(l)))
            else:
                QMessageBox.warning(self, "Error", f"No se pudieron cargar logs ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar:\n{e}")

    def limpiar_logs(self):
        try:
            r = requests.delete(
                f"{API_BASE}/api/mantenimiento/borrar_logs",
                headers=self._auth_headers(),
                timeout=6
            )
            if r.ok:
                QMessageBox.information(self, "Éxito", "Logs eliminados.")
                self.lista_logs.clear()
            else:
                QMessageBox.warning(self, "Error", "No se pudieron eliminar los logs.")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar:\n{e}")

    def probar_db(self):
        try:
            r = requests.get(f"{API_BASE}/api/mantenimiento/db_ping", timeout=6)
            if r.ok:
                data = r.json()
                QMessageBox.information(
                    self,
                    "Conexión a la BD",
                    f"OK: {data.get('db_ok')}\n{data.get('mensaje')}"
                )
            else:
                QMessageBox.warning(self, "Error", f"DB ping falló ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar:\n{e}")
