from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QInputDialog, QScrollArea, QGridLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
import requests
from app_state import API_BASE, GlobalState
from dialogs.usuario_dialog import UsuarioDialog


class UsuariosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usuarios")
        self.resize(920, 560)
        self.setup_ui()
        self.cargar_usuarios()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        lbl = QLabel("Usuarios")
        lbl.setStyleSheet("font-weight: bold; font-size: 16px;")
        top.addWidget(lbl)
        # top.addStretch()
        btn_add = QPushButton("Nuevo Usuario")
        btn_add.clicked.connect(self.agregar_usuario)
        top.addWidget(btn_add)
        layout.addLayout(top)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

    def _auth_headers(self):
        token = getattr(GlobalState, "token", None)
        return {"Authorization": f"Bearer {token}"} if token else {}

    def cargar_usuarios(self):
        try:
            r = requests.get(f"{API_BASE}/api/auth/usuarios", headers=self._auth_headers(), timeout=6)
            if r.ok:
                usuarios = r.json() or []
                usuarios = [u for u in usuarios if (u.get("rol","").lower() not in ("servicio", "servicio tecnico", "tecnico"))]
                self.mostrar_usuarios(usuarios)
            else:
                QMessageBox.warning(self, "Error", f"No se pudieron cargar usuarios ({r.status_code})")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

    def mostrar_usuarios(self, usuarios):
        self.clear_grid()
        cols = 3
        is_admin = getattr(GlobalState, "is_admin", False)

        admins = [u for u in usuarios if (u.get("rol","").lower() == "admin")]
        others = [u for u in usuarios if (u.get("rol","").lower() != "admin")]
        ordered = admins + others

        for idx, u in enumerate(ordered):
            row = idx // cols
            col = idx % cols
            card = self._make_card(u, is_admin)
            self.grid.addWidget(card, row, col)

    def _make_card(self, u, is_admin):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame{background:#fff; border:1px solid #ddd; border-radius:6px; padding:8px;}")
        frame.setFixedSize(400, 250)
        frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        v = QVBoxLayout(frame)
        v.setContentsMargins(8,8,8,8)

        uid = u.get("id_usuario", u.get("id", ""))
        nombre = u.get("nombre", "")
        email = u.get("email", "")
        rol = (u.get("rol","") or "").lower()

        if rol == "admin":
            lbl_admin = QLabel("Usuario Administrador")
            lbl_admin.setStyleSheet("font-weight:bold; font-size:14px; color:#c0392b;")
            lbl_admin.setAlignment(Qt.AlignCenter)
            v.addWidget(lbl_admin)
            # if nombre:
            #     v.addWidget(QLabel(nombre))
            if email:
                lbl_e = QLabel(f"Correo: {email}")
                lbl_e.setStyleSheet("color:#555; font-size:12px;")
                v.addWidget(lbl_e)
            h = QHBoxLayout()
            btn_edit = QPushButton("Editar")
            btn_edit.setFixedHeight(28)
            btn_edit.clicked.connect(lambda _, _id=uid: self.editar_usuario(_id))
            h.addWidget(btn_edit)
            v.addLayout(h)
        else:
            lbl_nom = QLabel(f"<b>{nombre}</b>")
            lbl_nom.setStyleSheet("font-size:14px;")
            lbl_nom.setAlignment(Qt.AlignCenter)
            v.addWidget(lbl_nom)
            lbl_id = QLabel(f"Cédula: {uid}")
            lbl_id.setStyleSheet("color:#333; font-size:11px;")
            v.addWidget(lbl_id)
  
            lbl_email = QLabel(f"Correo: {email}")
            lbl_email.setStyleSheet("color:#555; font-size:12px;")
            v.addWidget(lbl_email)

            h = QHBoxLayout()
            btn_edit = QPushButton("Editar")
            btn_delete = QPushButton("Eliminar")
            btn_edit.setFixedHeight(28)
            btn_delete.setFixedHeight(28)
            btn_edit.clicked.connect(lambda _, _id=uid: self.editar_usuario(_id))
            btn_delete.clicked.connect(lambda _, _id=uid: self.eliminar_usuario(_id))
            h.addWidget(btn_edit)
            h.addWidget(btn_delete)
            v.addLayout(h)

        return frame

    def agregar_usuario(self):
        dlg = UsuarioDialog(self, modo="add")
        if dlg.exec():
            payload = dlg.get_payload()
            if not payload or not payload.get("nombre") or not payload.get("email") or not payload.get("password"):
                QMessageBox.warning(self, "Campos incompletos", "Nombre, email y password son obligatorios.")
                return
            try:
                r = requests.post(f"{API_BASE}/api/auth/usuarios", json=payload, headers=self._auth_headers(), timeout=8)
                if r.status_code in (200, 201):
                    QMessageBox.information(self, "Éxito", "Usuario creado.")
                    self.cargar_usuarios()
                else:
                    detalle = r.text
                    try: detalle = r.json()
                    except Exception: pass
                    QMessageBox.warning(self, "Error", f"No se pudo crear usuario ({r.status_code}): {detalle}")
            except requests.RequestException as e:
                QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def editar_usuario(self, id_usuario):
        try:
            r = requests.get(f"{API_BASE}/api/auth/usuarios/{id_usuario}", headers=self._auth_headers(), timeout=6)
            if not r.ok:
                QMessageBox.warning(self, "Error", "No se pudo obtener usuario")
                return
            usuario = r.json() or {}
            dlg = UsuarioDialog(self, modo="edit", usuario=usuario)
            if dlg.exec():
                payload = dlg.get_payload()
                if not payload:
                    QMessageBox.warning(self, "Error", "Payload vacío")
                    return
                try:
                    r2 = requests.put(f"{API_BASE}/api/auth/editar/{id_usuario}", json=payload, headers=self._auth_headers(), timeout=8)
                    if r2.status_code == 200:
                        QMessageBox.information(self, "Éxito", "Usuario actualizado.")
                        self.cargar_usuarios()
                    else:
                        detalle = r2.text
                        try: detalle = r2.json()
                        except Exception: pass
                        QMessageBox.warning(self, "Error", f"No se pudo actualizar ({r2.status_code}): {detalle}")
                except requests.RequestException as e:
                    QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")

    def eliminar_usuario(self, id_usuario):
        token = getattr(GlobalState, "token", None)
        if not token:
            QMessageBox.warning(self, "No autorizado", "Debes iniciar sesión.")
            return
        resp = QMessageBox.question(self, "Confirmar eliminación",
                                    "¿Está seguro de eliminar este usuario?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        try:
            r = requests.delete(f"{API_BASE}/api/auth/eliminar/{id_usuario}", headers=self._auth_headers(), timeout=8)
            if r.status_code == 200:
                QMessageBox.information(self, "Éxito", "Usuario eliminado.")
                self.cargar_usuarios()
            else:
                detalle = r.text
                try: detalle = r.json()
                except Exception: pass
                QMessageBox.warning(self, "Error", f"No se pudo eliminar ({r.status_code}): {detalle}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar: {e}")