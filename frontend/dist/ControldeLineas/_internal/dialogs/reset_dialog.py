import requests
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from app_state import API_BASE, GlobalState, resources_path
from styles import reset_dialog
from dialogs.alert_dialog import AlertDialog

class RecuperarPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recuperar Contraseña")
        self.setWindowIcon(QIcon(resources_path("icons/clave.png")))
        self.resize(420, 200)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.paso = 1
        self.id_usuario = None
        self.otp_enviado = None

        self.init_paso1()
        self.setStyleSheet(reset_dialog)

    def init_paso1(self):
        self.limpiar_layout()
        self.label2 = QLabel("Ingresa tu cédula:")
        self.input_cedula = QLineEdit()
        self.input_cedula.setValidator(QIntValidator(0, 999999999))
        
        self.btn_enviar = QPushButton("Enviar código")
        self.btn_enviar.clicked.connect(self.enviar_otp)
        self.btn_cancelar = QPushButton("Cancelar")
        self.label= QLabel("Se enviará un código de verificación a tu correo", objectName="info_label")
        self.btn_cancelar.setObjectName("cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.input_cedula)
        btns = QHBoxLayout()
        btns.addWidget(self.btn_enviar)
        btns.addWidget(self.btn_cancelar)
        self.layout.addWidget(self.label)
        self.layout.addLayout(btns)


    def enviar_otp(self):
        cedula = self.input_cedula.text().strip()
        if not cedula:
            AlertDialog.warning(self, "Error", "Debes ingresar la cédula")
            return
        try:
            r = requests.get(f"{API_BASE}/api/auth/email/{cedula}", timeout=6)
            if r.ok:
                self.id_usuario = cedula
                AlertDialog.information(self, "Éxito", "Código enviado a tu correo")
                self.init_paso2()
            else:
                detalle = r.json().get("error", r.text)
                AlertDialog.warning(self, "Error", detalle)
        except requests.RequestException as e:
            AlertDialog.critical(self, "Error", f"No se pudo conectar: {e}")


    def init_paso2(self):
        self.limpiar_layout()
        self.label = QLabel("Ingresa el código recibido:")
        self.label_info = QLabel("Tu código expira en 5 minutos")
        self.input_otp = QLineEdit()
        self.btn_verificar = QPushButton("Verificar")
        self.btn_verificar.clicked.connect(self.verificar_otp)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.label_info)
        self.layout.addWidget(self.input_otp)
        btns = QHBoxLayout()
        btns.addWidget(self.btn_verificar)
        btns.addWidget(self.btn_cancelar)
        self.layout.addLayout(btns)

    def verificar_otp(self):
        otp = self.input_otp.text().strip()
        if not otp:
            AlertDialog.warning(self, "Error", "Debes ingresar el OTP")
            return
        try:
            r = requests.post(f"{API_BASE}/api/auth/verificar_otp", json={
                "id_usuario": self.id_usuario,
                "otp": otp
            }, timeout=6)
            if r.ok:
                AlertDialog.information(self, "Éxito", "OTP verificado")
                self.init_paso3()
            else:
                detalle = r.json().get("error", r.text)
                AlertDialog.warning(self, "Error", detalle)
        except requests.RequestException as e:
            AlertDialog.critical(self, "Error", f"No se pudo conectar: {e}")

    def init_paso3(self):
        self.limpiar_layout()
        self.label = QLabel("Ingresa tu nueva contraseña:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.btn_reset = QPushButton("Cambiar contraseña")
        self.btn_reset.clicked.connect(self.reset_password)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_pass)
        btns = QHBoxLayout()
        btns.addWidget(self.btn_reset)
        btns.addWidget(self.btn_cancelar)
        self.layout.addLayout(btns)

    def reset_password(self):
        new_pass = self.input_pass.text().strip()
        if not new_pass:
            AlertDialog.warning(self, "Error", "Debes ingresar la nueva contraseña")
            return
        try:
            r = requests.post(f"{API_BASE}/api/auth/reset_password", json={
                "id_usuario": self.id_usuario,
                "new_password": new_pass
            }, timeout=6)
            if r.ok:
                AlertDialog.information(self, "Éxito", "Contraseña cambiada correctamente")
                self.accept()
            else:
                detalle = r.json().get("error", r.text)
                AlertDialog.warning(self, "Error", detalle)
        except requests.RequestException as e:
            AlertDialog.critical(self, "Error", f"No se pudo conectar: {e}")

    def limpiar_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
