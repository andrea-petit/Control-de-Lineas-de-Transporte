import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from lineas_window import LineasWindow
from vehiculos_window import VehiculosWindow
from chofer_window import ChoferesWindow
from cambios_window import CambiosWindow

from styles import estilos_menu


class MenuWindow(QMainWindow):
    def menu_ui(self):
        self.setGeometry(150, 40, 1050, 670)
        self.setWindowTitle("Menu | Control de Lineas")
        self.setWindowIcon(QIcon("frontend/autobus.png"))

        self.showMaximized()

        self.frame_window = QFrame()
        self.frame_window.setLayout(QVBoxLayout())
        self.frame_buttons = QFrame()

        self.root_layout = QHBoxLayout()
        self.root_layout.addWidget(self.frame_buttons, 15)
        self.root_layout.addWidget(self.frame_window, 85)

        # márgenes y separación para que quede ajustado
        self.root_layout.setContentsMargins(12,12,12,12)
        self.root_layout.setSpacing(15)

        # limitar la altura del área de botones para que tengan una altura uniforme
        self.frame_buttons.setMaximumHeight(670)
        self.frame_buttons.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.widget = QWidget()
        self.widget.setLayout(self.root_layout)

        self.setCentralWidget(self.widget)
        self.setup_buttons_frames()
        self.setStyleSheet(estilos_menu)

    def setup_buttons_frames(self):
        self.button1 = QPushButton("Lineas")
        self.button2 = QPushButton("Vehiculos")
        self.button3 = QPushButton("Choferes")
        self.button4 = QPushButton("Cambios")
        self.button5 = QPushButton("")
        #self.button5 = QPushButton("cerrar Sesion")
        #self.button5.clicked.connect(self.close)

        self.button1.clicked.connect(self.abrir_lineas)
        self.button2.clicked.connect(self.cargar_vehiculos_por_linea)
        self.button3.clicked.connect(self.abrir_choferes)
        self.button4.clicked.connect(self.abrir_cambios)
        
        #layout horizontal con separación y márgenes
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(4, 4, 4, 4)
        self.buttons_layout.setSpacing(10)
        # que los botones ocupen el ancho disponible y tengan altura uniforme
        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFixedHeight(80)          # altura uniforme
            btn.setCursor(Qt.PointingHandCursor)
            self.buttons_layout.addWidget(btn)
        self.frame_buttons.setLayout(self.buttons_layout)


    #def close(self):
    #self.hide()
    #self.login_window = LoginWindow()
    #self.login_window.setup_ui()
    #self.login_window.show()

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

if __name__ == "__main__":
    from control_app import LoginWindow 
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("frontend/bus.png")) 
    window = MenuWindow()
    window.menu_ui()
    window.show()
    sys.exit(app.exec())
