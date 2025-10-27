import sys, socket, requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
#from __feature__ import true_property, snake_case

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

'''
class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setWindowTitle("Login - Control Líneas")
        self.setFixedSize(400,400)                  
        self.label = QLabel("Control de Lineas de Transporte")
        self.label.setStyleSheet('background: darkblue; color: white')
        self.label.setAlignment(Qt.AlignCenter)
        self.email = QLineEdit()
        self.email.setPlaceholderText("email")
        self.pw = QLineEdit()
        self.pw.setPlaceholderText("contraseña")
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_register = QPushButton("Registrar (prueba)")
        self.btn_login.clicked.connect(self.do_login)
        self.btn_register.clicked.connect(self.do_register)

        layout = QVBoxLayout()
        form = QFormLayout()
        form.addRow("Email:", self.email)
        form.addRow("Contraseña:", self.pw)
        layout.addWidget(self.label)
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignJustify)
'''

class LoginWindow(QMainWindow):
    def setup_ui(self):
        self.setFixedSize(410,495)
        self.setWindowTitle("Login | Control de Lineas")
        self.setStyleSheet("background: #011628")


        self.frameTitle = QFrame(self)
        self.frameTitle.setGeometry(30,10,350,70)
        self.frameTitle.setStyleSheet("background: white; color: black; border-radius: 10px; margin-top: 20px")
        self.titulo = QLabel("SISTEMA DE CONTROL DE TRANSPORTE", self.frameTitle)
        self.titulo.setGeometry(0,0,350,70)
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet("font-size: 15px; font-weight: bold; text-align: center")


        self.frameInputs = QFrame(self)
        self.frameInputs.setGeometry(30,115,350,350)
        self.frameInputs.setStyleSheet("background: white; border-radius: 10px")

        self.Id_usuario = QLineEdit()
        self.Id_usuario.setPlaceholderText("Ingresa tu cédula")
        self.Id_usuario.setStyleSheet("background: LightBlue; color: black; padding: 10px; margin-top: 20px; font-size: 15px")

        self.Password = QLineEdit()
        self.Password.setPlaceholderText("Ingresa tu Constraseña")
        self.Password.setEchoMode(QLineEdit.EchoMode.Password)
        self.Password.setStyleSheet("background: LightBlue; color: black; padding: 10px; margin-bottom: 10px; margin-top: 10px; font-size: 15px")

        self.btnLogin = QPushButton("Iniciar Sesion")
        #self.btnLogin.setStyleSheet("background: #012d51; color: white; padding: 10px")
        self.btnRegister = QPushButton("Registrarse(Prueba)")
        #self.btnRegister.setStyleSheet("background: #012d51; color: white; padding: 10px")
        self.btnLogin.setObjectName("btnLogin")
        self.btnRegister.setObjectName("btnRegister")

        #self.textBtn = QLabel("CAREWEBO")
        #self.textBtn.setStyleSheet("font-size: 10px; color: black")
        #self.textBtn.setAlignment(Qt.AlignCenter)



        btnStyle = '''
        *{
            transition: all linear 0.5ms;
        }

        QPushButton {
            background: #012d51;
            color: white;
            padding: 10px;
            border-radius: 10px;
            border: none;
            transition: all linear 1s;
            font-size: 13px;
        }

        QPushButton:hover {
            background: #024a7a
        }

        QPushButton:pressed {
            background: #011826;
'''
        self.btnLogin.setStyleSheet(btnStyle)
        self.btnRegister.setStyleSheet(btnStyle)
        self.btnLogin.setCursor(Qt.PointingHandCursor)
        self.btnRegister.setCursor(Qt.PointingHandCursor)



        self.btnLogin.clicked.connect(self.do_login)
        self.btnRegister.clicked.connect(self.do_register)

        # ---- Reemplazo: crear un widget contenedor dentro de frameInputs y asignarle el layout ----
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16,16,16,16)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.Id_usuario)
        self.layout.addWidget(self.Password)
        self.layout.addWidget(self.btnLogin)
        self.layout.addWidget(self.btnRegister)
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
        if not id_usuario or not pw:
            QMessageBox.warning(self, "Error", "Completa ambos campos")
            return
        payload = {"id_usuario": id_usuario, "password": pw}
        try:
            r = requests.post(f"{API_BASE}/api/auth/login", json=payload, timeout=3)
            if r.status_code == 200:
                data = r.json()
                QMessageBox.information(self, "Bienvenida", f"Hola {data['usuario']['nombre']} (rol: {data['usuario']['rol']})")
                # Aquí abrirías el dashboard real
            else:
                QMessageBox.warning(self, "Login fallido", str(r.json()))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.setup_ui()
    window.show()
    sys.exit(app.exec())
