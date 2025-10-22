import sys, socket, requests
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QVBoxLayout

SERVER_IP = "192.168.0.105"
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

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Control Líneas")
        self.setFixedSize(360,180)
        self.info = QLabel(f"Conectando a: {API_BASE}")
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
        layout.addWidget(self.info)
        layout.addLayout(form)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

    def do_register(self):
        email = self.email.text().strip()
        pw = self.pw.text().strip()
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
        email = self.email.text().strip()
        pw = self.pw.text().strip()
        if not email or not pw:
            QMessageBox.warning(self, "Error", "Completa ambos campos")
            return
        payload = {"email": email, "password": pw}
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
    w = LoginWindow()
    w.show()
    sys.exit(app.exec())
