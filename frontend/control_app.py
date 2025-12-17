import sys, socket, os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import styles
import requests
from app_state import API_BASE, GlobalState, resources_path
from dialogs.reset_dialog import RecuperarPasswordDialog
from dialogs.alert_dialog import AlertDialog


class LoginWindow(QMainWindow):
    def setup_ui(self):
        self.setFixedSize(490,480)
        self.setFixedSize(520,460)
        self.setWindowTitle("Login | Control de Lineas | I.M.T.T")
        self.setWindowIcon(QIcon(resources_path("icons/bus.png").replace(os.sep, '/')))
        self.setStyleSheet(f"background: url({resources_path('img/Fondo.jpg').replace(os.sep, '/')})")

        self.frameTitle = QFrame(self)
        self.frameTitle.setGeometry(33,22,460,80)
        self.frameTitle.setStyleSheet(styles.estilos_login)

        title_layout = QHBoxLayout(self.frameTitle)
        title_layout.setContentsMargins(8, 8, 8, 8)
        title_layout.setSpacing(12)

        self.frameLogoLeft = QLabel()
        self.frameLogoLeft.setFixedSize(80, 55)
        self.frameLogoLeft.setStyleSheet(f"border-image: url({resources_path('img/LogoIMTT TR.png').replace(os.sep, '/')}) 0 0 0 0 stretch stretch;")
        self.frameLogoLeft.setScaledContents(True)

        title_layout.addWidget(self.frameLogoLeft)
        title_layout.setAlignment(self.frameLogoLeft, Qt.AlignVCenter)

        self.titulo = QLabel("SISTEMA DE CONTROL\n DE TRANSPORTE")
        self.titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        self.titulo.setAlignment(Qt.AlignCenter)

        self.frameLogoRight = QLabel()
        self.frameLogoRight.setFixedSize(85,55)
        self.frameLogoRight.setStyleSheet(f"border-image: url({resources_path('img/LogoCariruB.png').replace(os.sep, '/')}) 0 0 0 0 stretch stretch;")
        self.frameLogoRight.setScaledContents(True)

        title_layout.addWidget(self.frameLogoLeft, 0, Qt.AlignVCenter)
        title_layout.addWidget(self.titulo, 1)
        title_layout.addWidget(self.frameLogoRight, 0, Qt.AlignVCenter)

        self.frameInputs = QFrame(self)
        self.frameInputs.setGeometry(33,122,460,312)
        self.frameInputs.setStyleSheet("background: white; border-radius: 10px")

        self.Id_usuario = QLineEdit()
        self.Id_usuario.setValidator(QIntValidator(0, 999999999))
        self.Id_usuario.setPlaceholderText("Ingresa tu Cédula")
        self.Id_usuario.setStyleSheet(styles.estilos_login)

        self.Password = QLineEdit()
        self.Password.setPlaceholderText("Ingresa tu Contraseña")
        self.Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Password.setStyleSheet(styles.estilos_login)

        self.tipo_usuario = QComboBox()
        self.tipo_usuario.addItems(["Usuario", "Admin", "Servicio Técnico"])
        self.tipo_usuario.setStyleSheet(styles.qcombostyle)   
        self.tipo_usuario.currentIndexChanged.connect(self.cambio_tipo_usuario)

        self.btnLogin = QPushButton("Iniciar Sesión", objectName="btnLogin")
        self.btnLogin.setStyleSheet('''
                                    QPushButton {
                                        background: #012d51;
                                        color: white;
                                        padding: 15px;
                                        border-radius: 10px;
                                        font-size: 13px;
                                        
                                    }

                                    QPushButton:hover {
                                        background: #024a7a
                                    }

                                    QPushButton:pressed {
                                        background: #011826;
                                    }''')
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        self.btnLogin.clicked.connect(self.do_login)

        self.olvidaste_btn = QPushButton("¿Olvidaste tu contraseña?")
        self.olvidaste_btn.setStyleSheet('''
                                        QPushButton {
                                        color: black;
                                        font-size: 15px;
                                        font-weight: 400;
                                        border-bottom: solid 2px black;
                                        margin-top: -2px;
                                        }
                                        QPushButton::hover{
                                        color: blue;
                                        }
''')
        self.olvidaste_btn.setCursor(Qt.PointingHandCursor)
        self.olvidaste_btn.clicked.connect(self.mostrar_recuperacion)


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(25,20,25,0)
        self.layout.setSpacing(16)
        self.layout.addWidget(self.tipo_usuario)
        self.layout.addWidget(self.Id_usuario)
        self.layout.addWidget(self.Password)
        self.layout.addWidget(self.btnLogin)
        self.layout.addWidget(self.olvidaste_btn)
        self.layout.addStretch()

        self.widget = QWidget(self.frameInputs)
        self.widget.setLayout(self.layout)
        self.widget.setGeometry(0, 0, self.frameInputs.width(), self.frameInputs.height())

    def cambio_tipo_usuario(self):
        if self.tipo_usuario.currentText() == "Admin":
            self.Id_usuario.setText("Administrador")
            self.Id_usuario.setAlignment(Qt.AlignCenter)
            self.Id_usuario.setDisabled(True)
        elif self.tipo_usuario.currentText() == "Servicio Técnico":
            self.Id_usuario.setText("Servicio Técnico")
            self.Id_usuario.setAlignment(Qt.AlignCenter)
            self.Id_usuario.setDisabled(True)
        else:
            self.Id_usuario.clear()
            self.Id_usuario.setAlignment(Qt.AlignLeft)
            self.Id_usuario.setEnabled(True)

    def do_login(self):
        if self.tipo_usuario.currentText() == "Admin":
            cedula = "1"
        elif self.tipo_usuario.currentText()== "Servicio Técnico":
            cedula= "2"
        else:
            cedula = self.Id_usuario.text().strip()

        pwd = self.Password.text().strip()
        if not cedula or not pwd:
            AlertDialog.warning(self, "Aviso", "Ingrese cédula y contraseña")
            return

        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json={"id_usuario": cedula, "password": pwd}, timeout=6)
        except Exception as e:
            AlertDialog.critical(self, "Error", f"No se pudo conectar al servidor: {e}")
            return

        if not r.ok:
            try:
                msg = r.json()
            except:
                msg = r.text
            AlertDialog.warning(self, "Login fallido", str(msg))
            return

        data = r.json()
        token = data.get("access_token")
        rol = data.get("rol", "usuario")

        if not token:
            AlertDialog.critical(self, "Error", "Respuesta inválida del servidor (no token)")
            return

        GlobalState.token = token
        GlobalState.usuario = data.get("username")
        GlobalState.role= rol
        GlobalState.is_admin = (rol.lower() == "admin")

        AlertDialog.information(self, "Bienvenido", "Login correcto")
        
        try:
            if self.tipo_usuario.currentText() == "Servicio Técnico":
                from windows.mantenimiento_window import MantenimientoWindow
                self.hide()
                self.mantenimiento_window = MantenimientoWindow()
                self.mantenimiento_window.show()
            else:
                from main_ import MenuWindow
                self.hide()
                self.main_window = MenuWindow()
                try:
                    self.main_window.menu_ui()
                except Exception:
                    pass
                self.main_window.show()
        except Exception as e:
            AlertDialog.critical(self, "Error", f"No se pudo abrir la ventana: {e}")
            return

    def mostrar_recuperacion(self):
        dlg = RecuperarPasswordDialog()
        dlg.exec()  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resources_path("img/autobus.png"))) 
    window = LoginWindow()
    window.setup_ui()
    window.show()
    sys.exit(app.exec())


