from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from app_state import resources_path

class AlertDialog(QDialog):
    def __init__(self, parent=None, title="Aviso", message="", icon_path=None, confirmation=False, ok_text="OK", cancel_text="Cancelar"):
        if icon_path is None:
            icon_path = resources_path("frontend/img/alert.png")
        super().__init__(parent)
        self.setWindowTitle(title)
        
        # Attempt to set window icon, handle potential path issues
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
             # Fallback or try relative check
             pass

        self.setFixedSize(360, 160)
        self.setStyleSheet("background: white; color: black; font-family: 'Segoe UI', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Message Area
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Button Area
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setStyleSheet('''
            QPushButton {
                background: #012d51;
                color: white;
                padding: 8px 30px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #024a7a;
            }
            QPushButton:pressed {
                background: #011826;
            }
        ''')
        self.ok_btn.clicked.connect(self.accept)
        
        if confirmation:
            self.cancel_btn = QPushButton(cancel_text)
            self.cancel_btn.setCursor(Qt.PointingHandCursor)
            self.cancel_btn.setStyleSheet('''
                QPushButton {
                    background: #e74c3c;
                    color: white;
                    padding: 8px 30px;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: #c0392b;
                }
                QPushButton:pressed {
                    background: #922b21;
                }
            ''')
            self.cancel_btn.clicked.connect(self.reject)
            btn_layout.addWidget(self.cancel_btn)

        self.ok_btn.setText(ok_text)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

    @staticmethod
    def show_alert(parent, title, message):
        dlg = AlertDialog(parent, title, message)
        return dlg.exec()

    @staticmethod
    def warning(parent, title, message):
        # Could add specific styling or icon for warning
        return AlertDialog.show_alert(parent, title, message)

    @staticmethod
    def information(parent, title, message):
        return AlertDialog.show_alert(parent, title, message)

    @staticmethod
    def critical(parent, title, message):
        return AlertDialog.show_alert(parent, title, message)

    @staticmethod
    def question(parent, title, message):
        dlg = AlertDialog(parent, title, message, confirmation=True, ok_text="Sí", cancel_text="No")
        return dlg.exec() == QDialog.Accepted
