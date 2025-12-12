import os
import io
import requests
from app_state import API_BASE

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGroupBox
)
from PySide6.QtCore import QObject, Signal, Qt, QThread

API_BASE_URL = API_BASE
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Mapa de combo a lista de municipios reales
MUNICIPIOS_MAP = {
    "": [],
    "Carirubana": ["Carirubana"],
    "Los Taques / Falcón": ["Los Taques", "Falcón"]
}


class WorkerSignals(QObject):
    finished = Signal(bool, str, object)


class ReportWorker(QObject):
    signals = WorkerSignals()

    def run_pdf(self, municipios, combustible):
        try:
            params = {"municipios": ",".join(municipios) if municipios else None,
                      "combustible": combustible}
            r = requests.get(f"{API_BASE_URL}/api/reportes/pdf", params=params)
            if r.status_code != 200:
                raise Exception(r.text)
            buf = io.BytesIO(r.content)
            self.signals.finished.emit(True, "PDF generado", buf)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

    def run_xlsx(self, municipios, combustible):
        try:
            params = {"municipios": ",".join(municipios) if municipios else None,
                      "combustible": combustible}
            r = requests.get(f"{API_BASE_URL}/api/reportes/xlsx", params=params)
            if r.status_code != 200:
                raise Exception(r.text)
            buf = io.BytesIO(r.content)
            self.signals.finished.emit(True, "Excel generado", buf)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)


class ReportGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de reportes - PySide6")
        self.resize(900, 600)
        self._active_threads = []
        self._build_ui()
        self.list_files()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Filtros
        gb_filters = QGroupBox("Filtros")
        fl = QHBoxLayout()
        gb_filters.setLayout(fl)
        layout.addWidget(gb_filters)

        # Municipio como drop-down
        self.cmb_municipios = QComboBox()
        self.cmb_municipios.addItems(list(MUNICIPIOS_MAP.keys()))

        # Combustible
        self.cmb_comb = QComboBox()
        self.cmb_comb.addItems(["", "diesel", "gasolina"])

        fl.addWidget(QLabel("Municipio:"))
        fl.addWidget(self.cmb_municipios)
        fl.addWidget(QLabel("Combustible:"))
        fl.addWidget(self.cmb_comb)

        # Botones PDF / Excel
        hb = QHBoxLayout()
        layout.addLayout(hb)

        self.btn_pdf = QPushButton("Generar PDF")
        self.btn_pdf.clicked.connect(self.on_generate_pdf)

        self.btn_xlsx = QPushButton("Generar Excel")
        self.btn_xlsx.clicked.connect(self.on_generate_xlsx)

        btn_refresh = QPushButton("Refrescar archivos")
        btn_refresh.clicked.connect(self.list_files)

        hb.addWidget(self.btn_pdf)
        hb.addWidget(self.btn_xlsx)
        hb.addStretch()
        hb.addWidget(btn_refresh)

        # Lista de archivos
        layout.addWidget(QLabel("Archivos"))
        self.lst_files = QListWidget()
        layout.addWidget(self.lst_files)

        fh_buttons = QHBoxLayout()
        btn_open = QPushButton("Abrir")
        btn_open.clicked.connect(self.open_selected_file)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_selected_file)

        fh_buttons.addWidget(btn_open)
        fh_buttons.addWidget(btn_del)
        layout.addLayout(fh_buttons)

        # Estado + salir
        bottom = QHBoxLayout()
        layout.addLayout(bottom)

        self.lbl_status = QLabel("")
        bottom.addWidget(self.lbl_status)
        bottom.addStretch()

        btn_close = QPushButton("Salir")
        btn_close.clicked.connect(self.close)
        bottom.addWidget(btn_close)

    def collect_filters(self):
        # Obtener lista de municipios reales del combo
        m = MUNICIPIOS_MAP.get(self.cmb_municipios.currentText(), [])
        c = self.cmb_comb.currentText().strip() or None
        return m, c

    def _run_worker(self, method_name, args, finished_slot):
        thread = QThread()
        worker = ReportWorker()
        worker.moveToThread(thread)

        worker.signals.finished.connect(finished_slot)
        worker.signals.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)

        def on_start():
            fn = getattr(worker, method_name)
            fn(*args)

        thread.started.connect(on_start)
        self._active_threads.append((thread, worker))
        thread.start()

    def on_generate_pdf(self):
        m, c = self.collect_filters()
        self.lbl_status.setText("Generando PDF...")
        self._run_worker("run_pdf", (m, c), self.on_finished_save)

    def on_generate_xlsx(self):
        m, c = self.collect_filters()
        self.lbl_status.setText("Generando Excel...")
        self._run_worker("run_xlsx", (m, c), self.on_finished_save)

    def on_finished_save(self, ok, msg, data):
        self.lbl_status.setText("")
        if not ok:
            QMessageBox.critical(self, "Error", msg)
            return

        buf = data
        buf.seek(0)
        head = buf.read(4)
        buf.seek(0)
        ext = ".pdf" if head.startswith(b"%PDF") else ".xlsx"

        # Guardar archivo donde el usuario indique
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", f"reporte{ext}")
        if not fname:
            return

        with open(fname, "wb") as f:
            f.write(buf.read())

        # Copiar automáticamente a uploads/
        base_name = os.path.basename(fname)
        upload_path = os.path.join(UPLOAD_FOLDER, base_name)
        try:
            with open(fname, "rb") as f_src, open(upload_path, "wb") as f_dst:
                f_dst.write(f_src.read())
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo copiar a uploads: {e}")

        QMessageBox.information(self, "Guardado", f"Archivo guardado:\n{fname}")
        self.list_files()

    def list_files(self):
        self.lst_files.clear()
        for fn in os.listdir(UPLOAD_FOLDER):
            path = os.path.join(UPLOAD_FOLDER, fn)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                item = QListWidgetItem(f"{fn} ({size} bytes)")
                item.setData(Qt.UserRole, {"filename": fn})
                self.lst_files.addItem(item)

    def selected_filename(self):
        item = self.lst_files.currentItem()
        return item.data(Qt.UserRole)["filename"] if item else None

    def open_selected_file(self):
        fn = self.selected_filename()
        if not fn:
            return
        path = os.path.join(UPLOAD_FOLDER, fn)
        if os.path.exists(path):
            os.startfile(path)

    def delete_selected_file(self):
        fn = self.selected_filename()
        if not fn:
            return
        path = os.path.join(UPLOAD_FOLDER, fn)
        try:
            os.remove(path)
            self.list_files()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
