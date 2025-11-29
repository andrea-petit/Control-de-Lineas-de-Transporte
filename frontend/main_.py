import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from windows.lineas_window import LineasWindow
from windows.vehiculos_window import VehiculosWindow
from windows.chofer_window import ChoferesWindow
from windows.cambios_window import CambiosWindow
from windows.mantenimiento_window import MantenimientoWindow
from windows.usuarios_window import UsuariosWindow
from app_state import API_BASE, GlobalState 

from styles import *


class MenuWindow(QMainWindow):
    def menu_ui(self):
        self.setGeometry(150, 40, 1050, 670)
        self.setWindowTitle("Menu | Control de Lineas")
        self.setWindowIcon(QIcon("frontend/img/autobus.png"))

        self.showMaximized()

        self.frame_window = QFrame()
        self.frame_window.setLayout(QVBoxLayout())
        self.frame_buttons = QFrame()
        # header frame (se usa para el título y controles superiores)
        self.frame_header = QFrame()

        # panel de botones: ancho máximo inicial y estado collapsed
        self.frame_buttons.setMaximumWidth(240)
        self.frame_buttons.setMinimumWidth(55)   # ancho cuando está retraído
        self.buttons_collapsed = False
        self._panel_anim = None

        # botón pequeño en el header para volver a abrir/ocultar el panel
        self.menu_toggle_btn = QPushButton("☰")
        self.menu_toggle_btn.setFixedSize(36, 36)
        self.menu_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.menu_toggle_btn.setToolTip("Mostrar/ocultar menú")
        self.menu_toggle_btn.clicked.connect(self.toggle_buttons_panel)

        self.root_layout = QHBoxLayout()
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0,0,0,0)
        self.right_layout.setSpacing(12)
        self.frame_header.setFixedHeight(60)
        self.frame_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.right_layout.addWidget(self.frame_header)
        self.right_layout.addWidget(self.frame_window)

        self.root_layout.addWidget(self.frame_buttons, 10)
        self.root_layout.addWidget(self.right_container, 90)

        self.root_layout.setContentsMargins(12,12,12,12)
        self.root_layout.setSpacing(15)

        self.frame_buttons.setMaximumHeight(670)
        self.frame_buttons.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.widget = QWidget(objectName="centralwidget")
        self.widget.setLayout(self.root_layout)


        self.setCentralWidget(self.widget)
        self.setup_buttons_frames()
        self.setStyleSheet(estilos_menu)


    def setup_buttons_frames(self):
        self.button1 = QPushButton("Lineas")
        self.button2 = QPushButton("Vehiculos")
        self.button3 = QPushButton("Choferes")
        self.button4 = QPushButton("Historial de Cambios")
        self.button5 = QPushButton("Generar Archivo")
        self.button6 = QPushButton("Administrar Usuarios")
        
        
        #self.button5 = QPushButton("cerrar Sesion")
        #self.button5.clicked.connect(self.close)

        self.button1.clicked.connect(self.abrir_lineas)
        self.button2.clicked.connect(self.cargar_vehiculos_por_linea)
        self.button3.clicked.connect(self.abrir_choferes)
        self.button4.clicked.connect(self.abrir_cambios)
        self.button6.clicked.connect(self.abrir_usuarios)

        self.button6.setVisible(GlobalState.is_admin)
        
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(6, 6, 6, 6)
        self.buttons_layout.setSpacing(18)


        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5, self.button6):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(btnStyle)
            self.buttons_layout.addWidget(btn)
        self.frame_buttons.setLayout(self.buttons_layout)
        # empuja los botones hacia arriba y deja espacio abajo para el label de usuario
        self.buttons_layout.addStretch()
        

        header_layout = QHBoxLayout(self.frame_header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(12)

        # añadir el botón toggle al header (izquierda)
        header_layout.addWidget(self.menu_toggle_btn, 0, Qt.AlignVCenter)

        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)


        title = QLabel("Instituto Municipal de Tránsito y Transporte")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #111;")
        title.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(title)
        
        header_layout.addWidget(title_container, Qt.AlignVCenter)
        header_layout.addStretch(0)


    def toggle_buttons_panel(self, collapsed=None):
        """
        Animación para retraer/expandir el panel de botones.
        Si collapsed es None invierte el estado, si es True fuerza retraer.
        """
        if collapsed is None:
            collapsed = not getattr(self, "buttons_collapsed", False)

        start = self.frame_buttons.width()
        end = self.frame_buttons.minimumWidth() if collapsed else 240

        # cancelar animación anterior si existe
        if self._panel_anim is not None and self._panel_anim.state() == QPropertyAnimation.Running:
            self._panel_anim.stop()

        anim = QPropertyAnimation(self.frame_buttons, b"maximumWidth", self)
        anim.setDuration(240)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.start()
        self._panel_anim = anim
        self.buttons_collapsed = collapsed

        # opcional: cambiar visibilidad del texto de los botones mientras está retraído
        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5, self.button6):
            if collapsed:
                btn.setText("")   # deja solo iconos si los fueras a añadir
                btn.setToolTip(getattr(btn, "text_orig", btn.objectName()))
            else:
                # restaurar textos (si quieres mantener los textos estáticos, guarda previamente)
                # aquí asumimos que no has guardado los textos, así que ponemos ejemplo fijo:
                btn.setText(btn.property("full_text") if btn.property("full_text") else btn.text())

    # Llamar a toggle al abrir una sección para retraer el menú automáticamente
    def abrir_lineas(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.lineas_window = LineasWindow()
        layout.addWidget(self.lineas_window)
        # retraer panel al seleccionar
        self.toggle_buttons_panel(collapsed=True)

    def cargar_vehiculos_por_linea(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.vehiculos_window = VehiculosWindow()
        layout.addWidget(self.vehiculos_window)
        pass
        self.toggle_buttons_panel(collapsed=True)

    def abrir_choferes(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.choferes_window = ChoferesWindow()
        layout.addWidget(self.choferes_window)
        self.toggle_buttons_panel(collapsed=True)

    def abrir_cambios(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.cambios_window = CambiosWindow()
        layout.addWidget(self.cambios_window)
        self.toggle_buttons_panel(collapsed=True)

    def abrir_usuarios(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.usuarios_window = UsuariosWindow()
        layout.addWidget(self.usuarios_window)
        self.toggle_buttons_panel(collapsed=True)


if __name__ == "__main__":
    from control_app import LoginWindow 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("frontend/img/bus.png")) 
    window = MenuWindow()
    window.menu_ui()
    window.show()
    sys.exit(app.exec())
