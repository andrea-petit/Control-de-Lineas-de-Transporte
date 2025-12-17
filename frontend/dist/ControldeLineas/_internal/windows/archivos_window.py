import os
import io
import re
import requests
from datetime import datetime
from app_state import API_BASE

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QGroupBox
)
from PySide6.QtCore import QObject, Signal, Qt, QThread
from PySide6.QtGui import QIcon
from styles import estilos_archivos

API_BASE_URL = API_BASE
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MUNICIPIOS_MAP = {
    "": [],  
    "Carirubana": ["Carirubana"],
    "Los Taques / Falcón": ["Los Taques", "Falcón"]
}


class WorkerSignals(QObject):
    finished = Signal(bool, str, object)


class ReportWorker(QObject):
    signals = WorkerSignals()

    def run_pdf(self, municipios, combustible, grupo=None):
        try:
            params = {
                "municipios": ",".join(municipios) if municipios else None,
                "combustible": combustible,
                "grupo": grupo
            }
            r = requests.get(f"{API_BASE_URL}/api/reportes/pdf", params=params)
            if r.status_code != 200:
                raise Exception(r.text)
            buf = io.BytesIO(r.content)
            self.signals.finished.emit(True, "PDF generado", buf)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

    def run_xlsx(self, municipios, combustible, grupo=None):
        try:
            params = {
                "municipios": ",".join(municipios) if municipios else None,
                "combustible": combustible,
                "grupo": grupo
            }
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
        self.setWindowTitle("Generador de reportes - Control de Lineas")
        self.resize(950, 650)
        self._active_threads = []
        self._build_ui()
        self.list_files()
        
        self.setStyleSheet(estilos_archivos)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        gb_filters = QGroupBox("Opciones de Reporte")
        fl = QHBoxLayout()
        fl.setSpacing(15)
        fl.setContentsMargins(15, 25, 15, 15)
        gb_filters.setLayout(fl)
        layout.addWidget(gb_filters)

        self.cmb_municipios = QComboBox()
        self.cmb_municipios.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #cfd8dc; border-radius: 5px; padding: 6px 10px;")
        self.cmb_municipios.addItems(list(MUNICIPIOS_MAP.keys()))
        self.cmb_grupo = QComboBox()
        self.cmb_grupo.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #cfd8dc; border-radius: 5px; padding: 6px 10px;")
        self.cmb_grupo.addItems(["Todos", "A", "B", "C"])

        self.cmb_comb = QComboBox()
        self.cmb_comb.setStyleSheet("background-color: #ffffff; color: black; border: 1px solid #cfd8dc; border-radius: 5px; padding: 6px 10px;")
        self.cmb_comb.addItems(["", "Diésel", "Gasolina"])

        fl.addWidget(QLabel("Municipio:"))
        fl.addWidget(self.cmb_municipios)
        fl.addWidget(QLabel("Combustible:"))
        fl.addWidget(self.cmb_comb)
        fl.addWidget(QLabel("Grupo:"))
        fl.addWidget(self.cmb_grupo)

        hb = QHBoxLayout()
        hb.setSpacing(10)
        layout.addLayout(hb)

        self.btn_pdf = QPushButton("Generar PDF")
        self.btn_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.on_generate_pdf)

        self.btn_xlsx = QPushButton("Generar Excel")
        self.btn_xlsx.setCursor(Qt.PointingHandCursor)
        self.btn_xlsx.clicked.connect(self.on_generate_xlsx)

        btn_refresh = QPushButton("Refrescar lista")
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.clicked.connect(self.list_files)

        hb.addWidget(self.btn_pdf)
        hb.addWidget(self.btn_xlsx)
        hb.addStretch()
        hb.addWidget(btn_refresh)

        lbl_list = QLabel("Archivos Generados:")
        lbl_list.setStyleSheet("font-weight: bold; font-size: 15px; margin-top: 10px;")
        layout.addWidget(lbl_list)
        
        self.lst_files = QListWidget()
        layout.addWidget(self.lst_files)

        bottom = QHBoxLayout()
        bottom.setSpacing(10)
        
        btn_open = QPushButton("Abrir Archivo")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.clicked.connect(self.open_selected_file)
        
        btn_del = QPushButton("Eliminar Seleccionado")
        btn_del.setObjectName("btn_delete")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.clicked.connect(self.delete_selected_file)

        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("lbl_status")

        btn_close = QPushButton("Cerrar Ventana")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.close)

        bottom.addWidget(btn_open)
        bottom.addWidget(btn_del)
        bottom.addWidget(self.lbl_status)
        bottom.addStretch()
        bottom.addWidget(btn_close)

        layout.addLayout(bottom)

    def collect_filters(self):
        m = MUNICIPIOS_MAP.get(self.cmb_municipios.currentText(), [])
        m = m if m else None

        c = self.cmb_comb.currentText().strip() or None
        c = c if c not in ("", "Todos") else None

        g = self.cmb_grupo.currentText().strip() or None
        g = g if g not in ("", "Todos") else None

        return m, c, g

    def build_default_filename(self, ext):
        municipio_txt = self.cmb_municipios.currentText().strip().lower()
        municipio = municipio_txt if municipio_txt else "todos"

        comb_txt = self.cmb_comb.currentText().strip().lower()
        combustible = comb_txt if comb_txt else "todos"

        grupo_txt = self.cmb_grupo.currentText().strip().lower()
        grupo = grupo_txt if grupo_txt and grupo_txt != "todos" else "todos"

        def clean(text):
            text = text.replace(" ", "_")
            text = re.sub(r"[^a-z0-9_]", "", text)
            return text

        municipio = clean(municipio)
        combustible = clean(combustible)
        grupo = clean(grupo)

        fecha = datetime.now().strftime("%Y-%m-%d")

        if municipio == "todos" and combustible == "todos" and grupo == "todos":
            name = f"reporte_todos_{fecha}"
        else:
            name = f"reporte_{municipio}_{combustible}_{grupo}_{fecha}"

        return f"{name}{ext}"

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
        m, c, g = self.collect_filters()
        self.lbl_status.setText("Generando PDF...")
        self._run_worker("run_pdf", (m, c, g), self.on_finished_save)

    def on_generate_xlsx(self):
        m, c, g = self.collect_filters()
        self.lbl_status.setText("Generando Excel...")
        self._run_worker("run_xlsx", (m, c, g), self.on_finished_save)

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

        default_name = self.build_default_filename(ext)

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            default_name,
            f"Archivos (*{ext})"
        )

        if not fname:
            return

        if not fname.lower().endswith(ext):
            fname += ext

        with open(fname, "wb") as f:
            f.write(buf.read())

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

