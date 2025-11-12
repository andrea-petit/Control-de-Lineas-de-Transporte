import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from styles import estilos_menu, btnStyle, estilos_login
import requests
from app_state import API_BASE, GlobalState

class LoginWindow(QMainWindow):
    def setup_ui(self):
        self.setFixedSize(490,410)
        self.setWindowTitle("Login | Control de Lineas")
        self.setWindowIcon(QIcon("frontend/img/autobus.png"))
        self.setStyleSheet("background: url(./frontend/img/Fondo.jpg)")

        self.frameTitle = QFrame(self)
        self.frameTitle.setGeometry(30,40,420,70)
        self.frameTitle.setStyleSheet(estilos_login)
        self.titulo = QLabel("SISTEMA DE CONTROL DE TRANSPORTE", self.frameTitle)
        self.titulo.setGeometry(0,0,400,70)
        self.titulo.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.titulo.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.frameLogo = QFrame(self.frameTitle)
        self.frameLogo.setGeometry(15,-21,90,130)
        self.frameLogo.setStyleSheet("border-image: url(./frontend/img/Logo.png) 0 0 0 0 stretch stretch;")

        self.frameInputs = QFrame(self)
        self.frameInputs.setGeometry(30,150,420,230)
        self.frameInputs.setStyleSheet("background: white; border-radius: 10px")

        self.Id_usuario = QLineEdit()
        self.Id_usuario.setPlaceholderText("Ingresa tu Cédula")
        self.Id_usuario.setStyleSheet(estilos_login)

        self.Password = QLineEdit()
        self.Password.setPlaceholderText("Ingresa tu Contraseña")
        self.Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Password.setStyleSheet(estilos_login)

        self.tipo_usuario = QComboBox()
        self.tipo_usuario.addItems(["Usuario", "Admin"])
        self.tipo_usuario.setStyleSheet(estilos_login)
        self.tipo_usuario.currentIndexChanged.connect(self.cambio_tipo_usuario)

        self.btnLogin = QPushButton("Iniciar Sesión", objectName="btnLogin")
        self.btnLogin.setStyleSheet(btnStyle)
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        self.btnLogin.clicked.connect(self.do_login)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16,16,16,16)
        self.layout.setSpacing(15)
        self.layout.addWidget(QLabel("Tipo de usuario:"))
        self.layout.addWidget(self.tipo_usuario)
        self.layout.addWidget(self.Id_usuario)
        self.layout.addWidget(self.Password)
        self.layout.addWidget(self.btnLogin)
        self.layout.addStretch()

        self.widget = QWidget(self.frameInputs)
        self.widget.setLayout(self.layout)
        self.widget.setGeometry(0, 0, self.frameInputs.width(), self.frameInputs.height())

    def cambio_tipo_usuario(self):
        if self.tipo_usuario.currentText() == "Admin":
            self.Id_usuario.setText("Administrador")
            self.Id_usuario.setDisabled(True)
        else:
            self.Id_usuario.clear()
            self.Id_usuario.setEnabled(True)

    def do_login(self):
        if self.tipo_usuario.currentText() == "Admin":
            cedula = "1"
        else:
            cedula = self.Id_usuario.text().strip()

        pwd = self.Password.text().strip()
        if not cedula or not pwd:
            QMessageBox.warning(self, "Aviso", "Ingrese cédula y contraseña")
            return

        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json={"id_usuario": cedula, "password": pwd}, timeout=6)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar al servidor: {e}")
            return

        if not r.ok:
            try:
                msg = r.json()
            except:
                msg = r.text
            QMessageBox.warning(self, "Login fallido", str(msg))
            return

        data = r.json()
        token = data.get("access_token")
        rol = data.get("rol", "usuario")

        if not token:
            QMessageBox.critical(self, "Error", "Respuesta inválida del servidor (no token)")
            return

        GlobalState.token = token
        GlobalState.is_admin = (rol.lower() == "admin")

        QMessageBox.information(self, "OK", "Login correcto")
        
        try:
            from main_ import MenuWindow
        except Exception:
            QMessageBox.critical(self, "Error", "No se pudo abrir la ventana principal (import failed).")
            return

        self.hide()
        self.main_window = MenuWindow()
        try:
            self.main_window.menu_ui()
        except Exception:
            pass
        self.main_window.show()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("frontend/img/autobus.png")) 
    window = LoginWindow()
    window.setup_ui()
    window.show()
    sys.exit(app.exec())
