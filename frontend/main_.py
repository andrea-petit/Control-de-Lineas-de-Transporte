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
        self.frame_header = QFrame()
        self.frame_buttons = QFrame()

        self.root_layout = QHBoxLayout()
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0,0,0,0)
        self.right_layout.setSpacing(12)
        self.frame_header.setFixedHeight(60)
        self.frame_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.right_layout.addWidget(self.frame_header)
        self.right_layout.addWidget(self.frame_window)

        self.root_layout.addWidget(self.frame_buttons, 15)
        self.root_layout.addWidget(self.right_container, 85)

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
        self.button2 = QPushButton("Propietarios")
        self.button3 = QPushButton("Choferes")
        self.button4 = QPushButton("Vehiculos")
        self.button5 = QPushButton("")
        self.button6 = QPushButton("")
        #self.button5 = QPushButton("cerrar Sesion")
        #self.button5.clicked.connect(self.close)


        #layout horizontal con separación y márgenes
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(4, 4, 4, 4)
        self.buttons_layout.setSpacing(10)


        for btn in (self.button1, self.button2, self.button3, self.button4, self.button5, self.button6):
            btn.setCursor(Qt.PointingHandCursor)
            self.buttons_layout.addWidget(btn)
        self.frame_buttons.setLayout(self.buttons_layout)
        self.buttons_layout.addStretch()


        header_layout = QHBoxLayout(self.frame_header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(12)


        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)


        title = QLabel("Institución Municipal de Tránsito y Transporte")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #111;")
        title.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(title)
        
        header_layout.addWidget(title_container, Qt.AlignVCenter)
        header_layout.addStretch(0)


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
