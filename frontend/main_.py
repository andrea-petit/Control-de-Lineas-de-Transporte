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
from app_state import API_BASE, GlobalState, resources_path
from windows.archivos_window import ReportGUI
from styles import *
from dialogs.alert_dialog import AlertDialog


class MenuWindow(QMainWindow):
    def menu_ui(self):
        self.setGeometry(150, 40, 1050, 670)
        self.setWindowTitle("Menu | Control de Lineas")
        self.setWindowIcon(QIcon(resources_path("frontend/icons/bus.png")))

        self.showMaximized()

        self.frame_window = QFrame()
        self.frame_window.setLayout(QVBoxLayout())
        self.frame_buttons = QFrame()
        
        self.frame_header = QFrame()

        # panel de botones: ancho máximo inicial y estado collapsed
        self.frame_buttons.setMaximumWidth(240)
        self.frame_buttons.setMinimumWidth(65)   # ancho cuando está retraído
        self.buttons_collapsed = False
        self._panel_anim = None

        # botón pequeño en el header para volver a abrir/ocultar el panel
        self.menu_toggle_btn = QPushButton("☰")
        self.menu_toggle_btn.setStyleSheet("background-color: transparent; border: none;")
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

        self.root_layout.addWidget(self.frame_buttons, 13)
        self.root_layout.addWidget(self.right_container, 87)

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
        self.button1 = QPushButton("Líneas")
        self.button2 = QPushButton("Vehículos")
        self.button3 = QPushButton("Choferes")
        self.button4 = QPushButton("Historial de Cambios")
        self.button5 = QPushButton("Generar Archivo")
        self.button6 = QPushButton("Administrar Usuarios")
        self.btn_logout = QPushButton("Cerrar sesión")
        
        icons = {
            self.button1: resources_path("frontend/icons/lineas3.png"),
            self.button2: resources_path("frontend/icons/vehiculos2.png"),
            self.button3: resources_path("frontend/icons/choferes3.png"),
            self.button4: resources_path("frontend/icons/historial2.png"),
            self.button5: resources_path("frontend/icons/archivo2.png"),
            self.button6: resources_path("frontend/icons/adminuser2.png"),
            self.btn_logout: resources_path("frontend/icons/cerrar-sesion.png"),
        }
        for btn, path in icons.items():
            icon = QIcon(path) if path and QIcon(path) else QIcon()
            # guardar icono y texto original para restaurar después
            btn.setProperty("full_text", btn.text())
            btn.setProperty("full_icon", icon)
            # no establecemos icono aquí para que, con el panel expandido, no se vea
            btn.setIcon(QIcon())
            btn.setIconSize(QSize(28, 28))
            # mantener texto alineado a la izquierda por defecto
            btn.setStyleSheet(btn.styleSheet() + " QPushButton { text-align: center; }")
        

        #self.button5 = QPushButton("cerrar Sesion")
        #self.button5.clicked.connect(self.close)

        self.button1.clicked.connect(self.abrir_lineas)
        self.button2.clicked.connect(self.cargar_vehiculos_por_linea)
        self.button3.clicked.connect(self.abrir_choferes)
        self.button4.clicked.connect(self.abrir_cambios)
        self.button6.clicked.connect(self.abrir_usuarios)
        self.button5.clicked.connect(self.abrir_archivos)
        self.btn_logout.clicked.connect(self.logout)

        # guardar el texto "completo" original en una propiedad para poder restaurarlo
        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5, self.button6, self.btn_logout):
            btn.setProperty("full_text", btn.text())

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

        # Mostrar nombre y rol del usuario en la parte inferior
        username = getattr(GlobalState, "username", getattr(GlobalState, "usuario", "Invitado"))
        role = getattr(GlobalState, "role", "Usuario")
        self.user_label = QLabel()
        self.user_label.setTextFormat(Qt.RichText)
        self.user_label.setText(f"<div style='text-align:center; color:black;'><b>{username}</b><br><span style='font-size:11px;color:black;'>{role}</span></div>")
        self.user_label.setAlignment(Qt.AlignCenter)
        self.user_label.setStyleSheet("padding: 4px;")
        self.buttons_layout.addWidget(self.user_label)

        # Botón de cerrar sesión (debajo del user_label)
        
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setFixedHeight(44)
        self.btn_logout.setStyleSheet(btnStyle)
        self.btn_logout.clicked.connect(self.logout)
        self.buttons_layout.addWidget(self.btn_logout)

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

        # Botón Acerca de en el header (derecha)
        self.btn_about = QPushButton("Acerca de")
        self.btn_about.setCursor(Qt.PointingHandCursor)
        self.btn_about.setIcon(QIcon(resources_path("frontend/icons/info.png")))
        self.btn_about.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #eee;
            }
        """)
        self.btn_about.clicked.connect(self.mostrar_acerca_de)
        header_layout.addWidget(self.btn_about, 0, Qt.AlignVCenter)


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

        # cambiar texto / icono según estado
        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5, self.button6, self.btn_logout):
            full = btn.property("full_text") or ""
            icon = btn.property("full_icon") or QIcon()
            if collapsed:
                # ocultar texto y mostrar icono centrado
                btn.setProperty("collapsed_text", btn.text() or full)
                btn.setText("")                 # quitar texto
                btn.setIcon(icon)               # mostrar icono
                btn.setToolTip(full)
                btn.setStyleSheet(btn.styleSheet() + " QPushButton { text-align: center; }")
            else:
                # restaurar texto y ocultar icono
                btn.setText(full)
                btn.setIcon(QIcon())            # ocultar icono cuando esté expandido
                btn.setToolTip("")
                btn.setStyleSheet(btn.styleSheet() + " QPushButton { text-align: center; }")

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
        
    def abrir_archivos(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        self.archivos_window = ReportGUI()
        layout.addWidget(self.archivos_window)
        self.toggle_buttons_panel(collapsed=True)

    def mostrar_acerca_de(self):
        if self.frame_window.layout() is None:
            self.frame_window.setLayout(QVBoxLayout())
        layout = self.frame_window.layout()
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        
        # Area de desplazamiento para asegurar que todo sea visible
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        center_widget = QWidget()
        center_widget.setStyleSheet("background: transparent;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setContentsMargins(10, 10, 10, 10)

        container = QWidget()
        container.setMaximumWidth(700)  # Más ancho para mejor distribución
        container.setMinimumWidth(500)
        container.setStyleSheet("""
            QWidget {
                background-color: #ffffff; 
                border-radius: 15px; 
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        v_layout = QVBoxLayout(container)
        v_layout.setAlignment(Qt.AlignCenter)
        v_layout.setContentsMargins(40, 40, 40, 40)
        v_layout.setSpacing(15)

        lbl_titulo = QLabel("Sistema de Control de Líneas de Transporte")
        lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #012d51; margin-bottom: 15px;")
        lbl_titulo.setAlignment(Qt.AlignCenter)

        lbl_desc = QLabel(
            "Este sistema permite la gestión integral de líneas de transporte, vehículos, choferes y reportes. \nDesarrollado para optimizar el control y seguimiento de las operaciones."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("font-size: 16px; color: #444; line-height: 100%;")
        lbl_desc.setAlignment(Qt.AlignCenter)

        # Sección de créditos
        lbl_unefa = QLabel("Realizado por los estudiantes de la UNEFA:")
        lbl_unefa.setStyleSheet("font-size: 18px; font-weight: bold; color: #012d51; margin-top: 40px;")
        lbl_unefa.setAlignment(Qt.AlignCenter)

        # Usar un Grid para los nombres para ahorrar espacio vertical y que se vean todos bien
        names_widget = QWidget()
        names_layout = QGridLayout(names_widget)
        
        estudiantes = [
            "Andrea Petit", "Andres Arias",
            "Veronika Arias", "Elijah Reyes",
            "Jeanniret Robles"
        ]
        
        row, col = 0, 0
        for name in estudiantes:
            l = QLabel(name)
            l.setStyleSheet("font-size: 16px; color: #333; font-weight: 500;")
            l.setAlignment(Qt.AlignCenter)
            names_layout.addWidget(l, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        lbl_credits = QLabel("© 2025 Instituto Municipal de Tránsito y Transporte")
        lbl_credits.setStyleSheet("font-size: 13px; color: #888; margin-top: 30px;")
        lbl_credits.setAlignment(Qt.AlignCenter)

        v_layout.addWidget(lbl_titulo)
        v_layout.addWidget(lbl_desc)
        v_layout.addWidget(lbl_unefa)
        v_layout.addWidget(names_widget)
        v_layout.addWidget(lbl_credits)

        center_layout.addWidget(container)
        
        scroll.setWidget(center_widget)
        layout.addWidget(scroll)
        
        self.toggle_buttons_panel(collapsed=True)

    def logout(self):
        """
        Limpia el estado global, abre la ventana de login y cierra el menú.
        """
        # limpiar estado de la aplicación
        GlobalState.token = None
        GlobalState.usuario = None
        GlobalState.is_admin = False
        for attr in ("current_user_id", "username", "role"):
            if hasattr(GlobalState, attr):
                setattr(GlobalState, attr, None)

        # intentar abrir la ventana de login
        try:
            from control_app import LoginWindow
            self.login = LoginWindow()
            # si tu LoginWindow expone setup_ui, ejecutarlo
            if hasattr(self.login, "setup_ui"):
                self.login.setup_ui()
            self.login.show()
        except Exception as e:
            AlertDialog.critical(self, "Error", f"No se pudo abrir Login: {e}")
        # cerrar ventana de menú
        self.close()


if __name__ == "__main__":
    from control_app import LoginWindow 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resources_path("frontend/img/bus.png"))) 
    window = MenuWindow()
    window.menu_ui()
    window.show()
    sys.exit(app.exec())
