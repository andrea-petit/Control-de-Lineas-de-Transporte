import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from control_app import *

from styles import estilos_menu


class MenuWindow(QMainWindow):
    def menu_ui(self):
        self.setGeometry(150, 40, 1050, 670)
        self.setWindowTitle("Menu | Control de Lineas")

        self.showMaximized()

        self.frame_window = QFrame()
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
        self.button2 = QPushButton("Propietarios")
        self.button3 = QPushButton("Choferes")
        self.button4 = QPushButton("Vehiculos")
        self.button5 = QPushButton("")
        #self.button5 = QPushButton("cerrar Sesion")
        #self.button5.clicked.connect(self.close)
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.menu_ui()
    window.show()
    sys.exit(app.exec())
