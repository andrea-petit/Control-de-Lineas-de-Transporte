import os
import io
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QTextEdit, QGroupBox
)
from PySide6.QtCore import QObject, Signal, Qt, QThread

# importa las funciones del controlador (ajusta si tu estructura de paquetes difiere)
try:
    from backend.controllers.archivos_controllers import (
        generar_plantilla_pdf_bytes,
        generar_plantilla_excel_bytes,
        obtener_vehiculos_por_municipios,
        listar_archivos,
        obtener_ruta_archivo,
        eliminar_archivo
    )
except Exception as e:
    generar_plantilla_pdf_bytes = generar_plantilla_excel_bytes = None
    obtener_vehiculos_por_municipios = listar_archivos = obtener_ruta_archivo = eliminar_archivo = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

class WorkerSignals(QObject):
    finished = Signal(bool, str, object)  # success, message, data

class ReportWorker(QObject):
    signals = None
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    # Estos métodos se ejecutan dentro de un QThread
    def run_pdf(self, municipios, combustible, fd, fh):
        try:
            buf = generar_plantilla_pdf_bytes(municipios=municipios, combustible=combustible,
                                              fecha_desde=fd, fecha_hasta=fh)
            self.signals.finished.emit(True, "PDF generado", buf)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

    def run_xlsx(self, municipios, combustible, fd, fh):
        try:
            buf = generar_plantilla_excel_bytes(municipios=municipios, combustible=combustible,
                                                fecha_desde=fd, fecha_hasta=fh)
            self.signals.finished.emit(True, "Excel generado", buf)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

    def run_preview(self, municipios, combustible, fd, fh, max_limit=200):
        try:
            regs = obtener_vehiculos_por_municipios(municipios=municipios, combustible=combustible,
                                                    fecha_desde=fd, fecha_hasta=fh, max_limit=max_limit)
            self.signals.finished.emit(True, "Preview listo", regs)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

    def run_list_files(self):
        try:
            files = listar_archivos()
            self.signals.finished.emit(True, "Files listos", files)
        except Exception as e:
            self.signals.finished.emit(False, str(e), None)

class ReportGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de reportes - PySide6")
        self.resize(1000, 640)
        self._active_threads = []
        if _IMPORT_ERROR:
            QMessageBox.critical(self, "Import error", f"Error importando controlador:\n{_IMPORT_ERROR}")
        self._build_ui()
        self.list_files()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # filtros
        gb_filters = QGroupBox("Filtros")
        fl = QHBoxLayout()
        gb_filters.setLayout(fl)
        layout.addWidget(gb_filters)

        self.ent_municipios = QLineEdit()
        self.ent_municipios.setPlaceholderText("Municipios (coma sep): Carirubana,Taques,Falcon")
        self.cmb_comb = QComboBox()
        self.cmb_comb.addItems(["", "diesel", "gasolina"])
        self.ent_fd = QLineEdit()
        self.ent_fd.setPlaceholderText("Fecha desde (YYYY-MM-DD)")
        self.ent_fh = QLineEdit()
        self.ent_fh.setPlaceholderText("Fecha hasta (YYYY-MM-DD)")

        fl.addWidget(QLabel("Municipios:"))
        fl.addWidget(self.ent_municipios)
        fl.addWidget(QLabel("Combustible:"))
        fl.addWidget(self.cmb_comb)
        fl.addWidget(QLabel("Desde:"))
        fl.addWidget(self.ent_fd)
        fl.addWidget(QLabel("Hasta:"))
        fl.addWidget(self.ent_fh)

        # botones
        hb = QHBoxLayout()
        layout.addLayout(hb)

        self.btn_pdf = QPushButton("Generar plantilla PDF")
        self.btn_pdf.clicked.connect(self.on_generate_pdf)
        self.btn_xlsx = QPushButton("Generar plantilla Excel")
        self.btn_xlsx.clicked.connect(self.on_generate_xlsx)
        self.btn_preview = QPushButton("Preview registros")
        self.btn_preview.clicked.connect(self.on_preview)
        btn_refresh = QPushButton("Refrescar archivos")
        btn_refresh.clicked.connect(self.list_files)

        hb.addWidget(self.btn_pdf)
        hb.addWidget(self.btn_xlsx)
        hb.addWidget(self.btn_preview)
        hb.addStretch()
        hb.addWidget(btn_refresh)

        # desactivar botones si import falló
        if _IMPORT_ERROR:
            self.btn_pdf.setEnabled(False)
            self.btn_xlsx.setEnabled(False)
            self.btn_preview.setEnabled(False)

        # panel principal
        main_h = QHBoxLayout()
        layout.addLayout(main_h, stretch=1)

        # preview (texto)
        vleft = QVBoxLayout()
        main_h.addLayout(vleft, stretch=3)
        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        vleft.addWidget(QLabel("Preview / Mensajes"))
        vleft.addWidget(self.txt_preview)

        # lista de archivos
        vright = QVBoxLayout()
        main_h.addLayout(vright, stretch=2)
        vright.addWidget(QLabel("Archivos (uploads)"))
        self.lst_files = QListWidget()
        vright.addWidget(self.lst_files)

        fh_buttons = QHBoxLayout()
        btn_open = QPushButton("Abrir")
        btn_open.clicked.connect(self.open_selected_file)
        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.delete_selected_file)
        fh_buttons.addWidget(btn_open)
        fh_buttons.addWidget(btn_del)
        vright.addLayout(fh_buttons)

        # estado / salir
        bottom = QHBoxLayout()
        layout.addLayout(bottom)
        self.lbl_status = QLabel("")
        bottom.addWidget(self.lbl_status)
        bottom.addStretch()
        btn_close = QPushButton("Salir")
        btn_close.clicked.connect(self.close)
        bottom.addWidget(btn_close)

    def collect_filters(self):
        municipios = self.ent_municipios.text().strip() or None
        combustible = self.cmb_comb.currentText().strip() or None
        fd = self.ent_fd.text().strip() or None
        fh = self.ent_fh.text().strip() or None
        return municipios, combustible, fd, fh

    def _validate_dates(self, fd, fh):
        if not fd and not fh:
            return True, None
        fmt = "%Y-%m-%d"
        try:
            if fd:
                datetime.strptime(fd, fmt)
            if fh:
                datetime.strptime(fh, fmt)
            return True, None
        except Exception:
            return False, "Formato de fecha inválido. Usa YYYY-MM-DD."

    def _run_worker_in_thread(self, method_name, args, finished_slot):
        """Crea QThread, instancia ReportWorker, mueve y ejecuta método. Mantiene referencia."""
        thread = QThread()
        worker = ReportWorker()
        worker.moveToThread(thread)

        # conectar terminado: cuando worker emite finished, cerrar thread
        worker.signals.finished.connect(finished_slot)
        worker.signals.finished.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)

        # cuando thread arranca, ejecutar método
        def on_started():
            # ejecutar método y dejar que emita finished
            fn = getattr(worker, method_name, None)
            if fn:
                fn(*args)
            else:
                worker.signals.finished.emit(False, f"Método {method_name} no encontrado", None)

        thread.started.connect(on_started)
        # guardar referencias para evitar GC
        self._active_threads.append((thread, worker))
        thread.start()

        # limpiar referencia cuando termine
        def clean_up(*_):
            # remover de lista
            try:
                self._active_threads.remove((thread, worker))
            except ValueError:
                pass
        thread.finished.connect(clean_up)

    # UI handlers
    def on_generate_pdf(self):
        municipios, combustible, fd, fh = self.collect_filters()
        ok, err = self._validate_dates(fd, fh)
        if not ok:
            QMessageBox.warning(self, "Fecha inválida", err)
            return
        self.lbl_status.setText("Generando PDF...")
        self._run_worker_in_thread('run_pdf', (municipios, combustible, fd, fh), self.on_worker_finished_save)

    def on_generate_xlsx(self):
        municipios, combustible, fd, fh = self.collect_filters()
        ok, err = self._validate_dates(fd, fh)
        if not ok:
            QMessageBox.warning(self, "Fecha inválida", err)
            return
        self.lbl_status.setText("Generando Excel...")
        self._run_worker_in_thread('run_xlsx', (municipios, combustible, fd, fh), self.on_worker_finished_save)

    def on_preview(self):
        municipios, combustible, fd, fh = self.collect_filters()
        ok, err = self._validate_dates(fd, fh)
        if not ok:
            QMessageBox.warning(self, "Fecha inválida", err)
            return
        self.lbl_status.setText("Generando preview...")
        self._run_worker_in_thread('run_preview', (municipios, combustible, fd, fh), self.on_worker_finished_preview)

    def list_files(self):
        self.lbl_status.setText("Listando archivos...")
        self._run_worker_in_thread('run_list_files', (), self.on_worker_finished_list)

    # slots
    def on_worker_finished_save(self, success, msg, data):
        if not success:
            QMessageBox.critical(self, "Error", msg)
            self.lbl_status.setText("Error")
            return
        buf = data
        if not isinstance(buf, io.BytesIO):
            QMessageBox.warning(self, "Atención", "Respuesta inesperada del controlador.")
            self.lbl_status.setText("Listo")
            return

        # detectar tipo a partir de bytes
        buf.seek(0)
        head = buf.read(4)
        buf.seek(0)
        ext = ''
        if head.startswith(b'%PDF'):
            ext = '.pdf'
        elif head.startswith(b'PK\x03\x04'):
            ext = '.xlsx'
        else:
            ext = ''

        default = f"plantilla_uso_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{ext}"
        filters = "PDF (*.pdf);;Excel (*.xlsx);;Todos (*)"
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", default, filters)
        if not fname:
            self.lbl_status.setText("Cancelado")
            return
        # asegurar extensión si no la seleccionó
        if ext and not fname.lower().endswith(ext):
            fname = fname + ext
        try:
            with open(fname, "wb") as f:
                buf.seek(0)
                f.write(buf.read())
            QMessageBox.information(self, "Guardado", f"Archivo guardado:\n{fname}")
            self.lbl_status.setText("Listo")
            self.list_files()
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))
            self.lbl_status.setText("Error")

    def on_worker_finished_preview(self, success, msg, data):
        if not success:
            QMessageBox.critical(self, "Error", msg)
            self.lbl_status.setText("Error")
            return
        regs = data or []
        if not regs:
            self.txt_preview.setPlainText("No se encontraron registros.")
            self.lbl_status.setText("Listo")
            return
        lines = []
        for r in regs:
            lines.append(
                " | ".join([
                    str(r.get('placa','')),
                    str(r.get('nombre_propietario','')),
                    str(r.get('nombre_chofer','')),
                    f"litros:{r.get('litraje',0):.2f}",
                    f"estado:{r.get('estado','')}"
                ])
            )
        self.txt_preview.setPlainText("\n".join(lines))
        self.lbl_status.setText(f"Preview {len(regs)} registros")

    def on_worker_finished_list(self, success, msg, data):
        if not success:
            QMessageBox.critical(self, "Error", msg)
            self.lbl_status.setText("Error")
            return
        files = data or []
        self.lst_files.clear()
        for f in files:
            item = QListWidgetItem(f"{f['filename']}    ({f['size']} bytes)")
            item.setData(Qt.UserRole, f)  # almacenar dict completo
            self.lst_files.addItem(item)
        self.lbl_status.setText(f"{len(files)} archivos")

    def selected_filename(self):
        item = self.lst_files.currentItem()
        if not item:
            return None
        data = item.data(Qt.UserRole)
        if isinstance(data, dict) and 'filename' in data:
            return data['filename']
        # fallback: parse text
        text = item.text()
        return text.split()[0]

    def open_selected_file(self):
        fn = self.selected_filename()
        if not fn:
            QMessageBox.warning(self, "Atención", "Selecciona un archivo primero.")
            return
        try:
            path = obtener_ruta_archivo(fn)
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_selected_file(self):
        fn = self.selected_filename()
        if not fn:
            QMessageBox.warning(self, "Atención", "Selecciona un archivo primero.")
            return
        if QMessageBox.question(self, "Confirmar", f"Eliminar {fn}?", QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        try:
            ok = eliminar_archivo(fn)
            if ok:
                QMessageBox.information(self, "Eliminado", "Archivo eliminado.")
                self.list_files()
            else:
                QMessageBox.warning(self, "Atención", "No se pudo eliminar.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    gui = ReportGUI()
    gui.show()
    sys.exit(app.exec())