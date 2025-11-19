import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from styles import estilos_menu, btnStyle, estilos_login
import requests
from app_state import API_BASE, GlobalState
from dialogs.reset_dialog import RecuperarPasswordDialog

class LoginWindow(QMainWindow):
    def setup_ui(self):
        self.setFixedSize(490,435)
        self.setWindowTitle("Login | Control de Lineas")
        self.setWindowIcon(QIcon("frontend/img/bus.png"))
        self.setStyleSheet("background: url(./frontend/img/Fondo.jpg)")

        self.frameTitle = QFrame(self)
        self.frameTitle.setGeometry(35,20,420,90)
        self.frameTitle.setStyleSheet(estilos_login)
        self.titulo = QLabel("SISTEMA DE CONTROL DE TRANSPORTE", self.frameTitle)
        self.titulo.setGeometry(0,0,400,90)
        self.titulo.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.titulo.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.frameLogo = QFrame(self.frameTitle)
        self.frameLogo.setGeometry(15,-12,90,130)
        self.frameLogo.setStyleSheet("border-image: url(./frontend/img/Logo.png) 0 0 0 0 stretch stretch;")

        self.frameInputs = QFrame(self)
        self.frameInputs.setGeometry(35,133,420,280)
        self.frameInputs.setStyleSheet("background: white; border-radius: 10px")

        self.Id_usuario = QLineEdit()
        self.Id_usuario.setPlaceholderText("Ingresa tu Cédula")
        self.Id_usuario.setStyleSheet(estilos_login)

        self.Password = QLineEdit()
        self.Password.setPlaceholderText("Ingresa tu Contraseña")
        self.Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Password.setStyleSheet(estilos_login)

        self.tipo_usuario = QComboBox()
        self.tipo_usuario.addItems(["Usuario", "Admin", "Servicio Técnico"])
        self.tipo_usuario.setStyleSheet(estilos_login)
        self.tipo_usuario.currentIndexChanged.connect(self.cambio_tipo_usuario)

        self.btnLogin = QPushButton("Iniciar Sesión", objectName="btnLogin")
        self.btnLogin.setStyleSheet(btnStyle)
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        self.btnLogin.clicked.connect(self.do_login)

        self.olvidaste_btn = QPushButton("¿Olvidaste tu contraseña?")
        self.olvidaste_btn.setStyleSheet(btnStyle)
        self.olvidaste_btn.setCursor(Qt.PointingHandCursor)
        self.olvidaste_btn.clicked.connect(self.mostrar_recuperacion)


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(25,25,25,25)
        self.layout.setSpacing(15)
        #self.layout.addWidget(QLabel("Tipo de usuario:"))
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


        alert = QDialog(self)
        alert.setWindowTitle("Warning...!!!")
        alert.setWindowIcon(QIcon("frontend/img/bus.png"))
        alert.setFixedSize(340,100)
        alert.setStyleSheet("background: white; color: black;")
        #alert_frame = QFrame(alert)
        #alert_frame.setGeometry(0, 0, 340, 100)
        #alert_icon = QLabel(alert_frame)
        #alert_icon.setGeometry(20, 15, 50, 50)
        #alert_icon.setStyleSheet("border-image: url(./frontend/img/alert.png) 0 0 0 0 stretch stretch;")
        v = QVBoxLayout(alert)
        h = QHBoxLayout()
        v.addStretch()
        alert_label = QLabel("Aviso, Ingrese cédula y contraseña")
        alert_label.setStyleSheet("font-size:14px; font-weight:bold;")
        v.addWidget(alert_label, 0, Qt.AlignCenter)
        h.addStretch()
        alert_btn = QPushButton("OK")
        alert_btn.setCursor(Qt.PointingHandCursor)
        alert_btn.setStyleSheet(btnStyle)
        alert_btn.clicked.connect(alert.accept)
        h.addWidget(alert_btn)
        h.addStretch()
        v.addLayout(h)

        if self.tipo_usuario.currentText() == "Admin":
            cedula = "1"
        elif self.tipo_usuario.currentText()== "Servicio Técnico":
            cedula= "2"
        else:
            cedula = self.Id_usuario.text().strip()

        pwd = self.Password.text().strip()
        if not cedula or not pwd:
            alert.exec()
            #QMessageBox.warning(self, "Aviso", "Ingrese cédula y contraseña")
            return

        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json={"id_usuario": cedula, "password": pwd}, timeout=6)
        except Exception as e:
            alert_label.setText("No se pudo conectar al servidor.")
            alert.show()
            #QMessageBox.critical(self, "Error", f"No se pudo conectar al servidor: {e}")
            return

        if not r.ok:
            try:
                msg = r.json()
            except:
                msg = r.text
            alert_label.setText("Login fallido: " + str(msg))
            alert.show()
            #QMessageBox.warning(self, "Login fallido", str(msg))
            return

        data = r.json()
        token = data.get("access_token")
        rol = data.get("rol", "usuario")

        if not token:
            alert_label.setText("Respuesta inválida del servidor (no token).")
            alert.show()
            #QMessageBox.critical(self, "Error", "Respuesta inválida del servidor (no token)")
            return

        GlobalState.token = token
        GlobalState.is_admin = (rol.lower() == "admin")

        alert_label.setText("Login correcto.")
        alert.show()
        #QMessageBox.information(self, "OK", "Login correcto")
        
        if alert.exec() == QDialog.Accepted:
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
                alert_label.setText("No se pudo abrir la ventana: " + str(e))
                alert.show()
                return

    def mostrar_recuperacion(self):
        dlg = RecuperarPasswordDialog()
        dlg.exec()  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("frontend/img/autobus.png")) 
    window = LoginWindow()
    window.setup_ui()
    window.show()
    sys.exit(app.exec())

