import re
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QHBoxLayout, QPushButton,
    QMessageBox, QInputDialog
)
from app_state import API_BASE, GlobalState

EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class UsuarioDialog(QDialog):

    def __init__(self, parent=None, modo="add", usuario=None):
        super().__init__(parent)
        self.modo = modo
        self.usuario = usuario or {}
        self.payload = None
        self.setWindowTitle("Crear Usuario" if modo == "add" else "Editar Usuario")
        self.resize(480, 220)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        if self.modo == "add":
            self.txt_id = QLineEdit(str(self.usuario.get("id_usuario", "")))
            self.txt_nombre = QLineEdit(self.usuario.get("nombre", ""))
            self.txt_email = QLineEdit(self.usuario.get("email", ""))
            self.txt_password = QLineEdit()
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.txt_password.setPlaceholderText("Min 6 caracteres")
            self.txt_password2 = QLineEdit()
            self.txt_password2.setEchoMode(QLineEdit.Password)
            self.txt_password2.setPlaceholderText("Confirmar contraseña")
            layout.addRow("Cédula del usuario:", self.txt_id)
            layout.addRow("Nombre:", self.txt_nombre)
            layout.addRow("Correo:", self.txt_email)
            layout.addRow("Contraseña:", self.txt_password)
            layout.addRow("Confirmar contraseña:", self.txt_password2)

            btns = QHBoxLayout()
            btn_verify = QPushButton("Crear nuevo usuario")
            btn_cancel = QPushButton("Cancelar")
            btn_verify.clicked.connect(self._on_create_clicked)
            btn_cancel.clicked.connect(self.reject)
            btns.addWidget(btn_verify)
            btns.addWidget(btn_cancel)
            layout.addRow(btns)

        else:
            from PySide6.QtWidgets import QComboBox
            self.combo_campo = QComboBox()
            self.combo_campo.addItem("Nombre", "nombre")
            self.combo_campo.addItem("Email", "email")
            self.input_valor = QLineEdit()
            self.input_valor.setPlaceholderText("Nuevo valor...")
            layout.addRow("Campo a editar:", self.combo_campo)
            layout.addRow("Nuevo valor:", self.input_valor)
            btns = QHBoxLayout()
            btn_save = QPushButton("Guardar cambio")
            btn_cancel = QPushButton("Cancelar")
            btn_save.clicked.connect(self._on_edit_ok)
            btn_cancel.clicked.connect(self.reject)
            btns.addWidget(btn_save)
            btns.addWidget(btn_cancel)
            layout.addRow(btns)

    def _validate_fields(self):
        nombre = self.txt_nombre.text().strip()
        email = self.txt_email.text().strip()
        password = self.txt_password.text()
        password2 = self.txt_password2.text()
        if not nombre or not email or not password:
            QMessageBox.warning(self, "Campos incompletos", "Nombre, email y password son obligatorios.")
            return False
        if len(password) < 6:
            QMessageBox.warning(self, "Password corto", "La contraseña debe tener al menos 6 caracteres.")
            return False
        if password != password2:
            QMessageBox.warning(self, "Contraseñas no coinciden", "Las contraseñas no coinciden.")
            return False
        if not EMAIL_RE.match(email):
            QMessageBox.warning(self, "Email inválido", "Ingrese un correo con formato válido.")
            return False
        return True

    def _on_create_clicked(self):
        if not self._validate_fields():
            return

        email = self.txt_email.text().strip()

        confirm, ok = QInputDialog.getText(self, "Confirmar correo",
                                           "Reingrese el correo para confirmar:")
        if not ok or confirm.strip().lower() != email.lower():
            QMessageBox.warning(self, "Confirmación requerida", "El correo no coincide. Verifique e intente nuevamente")
            return

        self.payload = {
            "id": self.txt_id.text().strip() or None,
            "nombre": self.txt_nombre.text().strip(),
            "email": email,
            "password": self.txt_password.text(),
            "rol": "usuario"
        }
        QMessageBox.information(self, "Confirmado", "Correo confirmado!")
        self.accept()

    def _on_edit_ok(self):
        valor = self.input_valor.text().strip()
        if not valor:
            QMessageBox.warning(self, "Campo vacío", "Ingrese el nuevo valor.")
            return
        self.payload = {"campo": self.combo_campo.currentData(), "valor": valor}
        self.accept()

    def get_payload(self):
        return self.payload