from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt
import requests
from app_state import API_BASE, GlobalState


class MantenimientoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mantenimiento / Servicio Técnico")
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
        layout.addLayout(logs_header)

        self.lista_logs = QListWidget()
        layout.addWidget(self.lista_logs)

        acciones = QHBoxLayout()
        self.input_log = QLineEdit()
        self.input_log.setPlaceholderText("Mensaje para registrar en logs")
        acciones.addWidget(self.input_log)

        btn_registrar = QPushButton("Registrar log")
        btn_registrar.clicked.connect(self.post_log)
        acciones.addWidget(btn_registrar)

        btn_db = QPushButton("Probar DB")
        btn_db.clicked.connect(self.probar_db)
        acciones.addWidget(btn_db)

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
            self.resumen.setPlainText(f"No se pudo conectar al servidor: {e}")

    def cargar_logs(self):
        count = int(self.spin_count.value())
        try:
            r = requests.get(f"{API_BASE}/api/mantenimiento/logs", params={"count": count}, timeout=6)
            if r.ok:
                payload = r.json()
                logs = payload.get("logs") if isinstance(payload, dict) else payload
                self.lista_logs.clear()
                for l in logs or []:
                    self.lista_logs.addItem(QListWidgetItem(str(l)))
            else:
                QMessageBox.warning(self, "Error", f"No se pudieron cargar logs ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def post_log(self):
        msg = self.input_log.text().strip()
        if not msg:
            QMessageBox.warning(self, "Aviso", "Ingrese un mensaje para registrar.")
            return
        headers = self._auth_headers()
        payload = {"mensaje": msg, "nivel": "info"}
        try:
            r = requests.post(f"{API_BASE}/api/mantenimiento/logs", json=payload, headers=headers, timeout=8)
            if r.status_code in (200, 201):
                QMessageBox.information(self, "Éxito", "Log registrado.")
                self.input_log.clear()
                self.cargar_logs()
            else:
                detalle = r.text
                try: detalle = r.json()
                except Exception: pass
                QMessageBox.warning(self, "Error", f"No se pudo registrar log ({r.status_code}): {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def probar_db(self):
        try:
            r = requests.get(f"{API_BASE}/api/mantenimiento/db_ping", timeout=6)
            if r.ok:
                payload = r.json()
                ok = payload.get("db_ok")
                msg = payload.get("mensaje")
                QMessageBox.information(self, "DB Ping", f"OK: {ok}\n{msg}")
            else:
                QMessageBox.warning(self, "Error", f"DB ping falló ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")