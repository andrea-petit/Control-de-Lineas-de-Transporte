import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from styles import estilos_menu, btnStyle, estilos_login
from main_ import *

SERVER_IP = "192.168.0.103"
PORT = 5000

def detect_api_url():
    try:
        r = requests.get(f"http://127.0.0.1:{PORT}/api/auth/ping", timeout=0.8)
        if r.ok:
            return f"http://127.0.0.1:{PORT}"
    except:
        pass
    try:
        r = requests.get(f"http://{SERVER_IP}:{PORT}/api/auth/ping", timeout=1.0)
        if r.ok:
            return f"http://{SERVER_IP}:{PORT}"
    except:
        pass
    return f"http://{SERVER_IP}:{PORT}"

API_BASE = detect_api_url()

class LoginWindow(QMainWindow):
    def setup_ui(self):
        self.setFixedSize(480,410)
        self.setWindowTitle("Login | Control de Lineas")
        self.setStyleSheet("background: url(./frontend/Fondo.jpg)")


        self.frameTitle = QFrame(self)
        self.frameTitle.setGeometry(30,40,420,70)
        self.frameTitle.setStyleSheet(estilos_login)
        self.titulo = QLabel("SISTEMA DE CONTROL DE TRANSPORTE", self.frameTitle)
        self.titulo.setGeometry(0,0,400,70)
        self.titulo.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.titulo.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.frameLogo = QFrame(self.frameTitle)
        self.frameLogo.setGeometry(15,-21,90,130)
        self.frameLogo.setStyleSheet("border-image: url(./frontend/Logo.png) 0 0 0 0 stretch stretch;")

        self.frameInputs = QFrame(self)
        self.frameInputs.setGeometry(30,140,420,230)
        self.frameInputs.setStyleSheet("background: white; border-radius: 10px")

        self.Id_usuario = QLineEdit()
        self.Id_usuario.setPlaceholderText("Ingresa tu Cédula")
        self.Id_usuario.setStyleSheet(estilos_login)

        self.Password = QLineEdit()
        self.Password.setPlaceholderText("Ingresa tu Constraseña")
        self.Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Password.setStyleSheet(estilos_login)

        self.btnLogin = QPushButton("Iniciar Sesión", objectName="btnLogin")
        #self.btnRegister = QPushButton("Registrarse(Prueba)", objectName="btnRegister")


        self.btnLogin.setStyleSheet(btnStyle)
        #self.btnRegister.setStyleSheet(btnStyle)
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        #self.btnRegister.setCursor(Qt.PointingHandCursor)



        self.btnLogin.clicked.connect(self.do_login)
        #self.btnRegister.clicked.connect(self.do_register)

        # ---- Reemplazo: crear un widget contenedor dentro de frameInputs y asignarle el layout ----
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16,16,16,16)
        self.layout.setSpacing(15)
        self.layout.addWidget(self.Id_usuario)
        self.layout.addWidget(self.Password)
        self.layout.addWidget(self.btnLogin)
        #self.layout.addWidget(self.btnRegister)
        #self.layout.addWidget(self.textBtn)
        self.layout.addStretch()

        # hacer que el widget sea hijo del frameInputs para que se muestre dentro del frame
        self.widget = QWidget(self.frameInputs)
        self.widget.setLayout(self.layout)
        # ocupar todo el frame (puedes ajustar si usas layouts en lugar de geometrías)
        self.widget.setGeometry(0, 0, self.frameInputs.width(), self.frameInputs.height())
        



    def do_register(self):
        #esto no sirve pero si lo quito no lo puedo correr por el boton <3
        email = self.Id_usuario.text().strip()
        pw = self.Password.text().strip()
        if not email or not pw:
            QMessageBox.warning(self, "Error", "Completa ambos campos")
            return
        payload = {"nombre": email.split("@")[0], "email": email, "password": pw, "rol": "usuario"}
        try:
            r = requests.post(f"{API_BASE}/api/auth/register", json=payload, timeout=3)
            QMessageBox.information(self, "Registro", str(r.json()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def do_login(self):
        id_usuario = self.Id_usuario.text().strip()
        pw = self.Password.text().strip()

        if id_usuario == "admin" and pw == "admin":
            QMessageBox.information(self, "Bienvenida", "Hola Admin")
            self.close()
            self.menu_window = MenuWindow()
            self.menu_window.menu_ui()
            self.menu_window.show()

        if not id_usuario or not pw:
            QMessageBox.warning(self, "Error", "Completa ambos campos")
            return
        payload = {"id_usuario": id_usuario, "password": pw}
        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json=payload, timeout=3)

            #if r.status_code == 200:
                #data = r.json()
                #QMessageBox.information(self, "Bienvenida", f"Hola {data['usuario']['nombre']} (rol: {data['usuario']['rol']})")
                # Aquí abrirías el dashboard real
            #else:
                #QMessageBox.warning(self, "Login fallido", str(r.json()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.setup_ui()
    window.show()
    sys.exit(app.exec())
