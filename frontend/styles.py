from app_state import resources_path
import os

estilos_menu = '''
    #centralwidget {
    background: #0B2E73;
    }

    QFrame {
    background: white;
    border-radius: 5px;
    }

    QPushButton {
    background: lightblue;
    color: black;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    }

'''

estilos_login = '''
    QWidget {
    background: #0B2E73;
    }

    QFrame {
    background: white;
    border-radius: 10px;
    color: black;
    font-size: 15px; 
    font-weight: bold; 
    text-align: center;
    }

    #frameTitle {
    margin-top: 100px;
    border-radius: 10px;
    }

    QLineEdit {
    background: #ADD8E6;
    color: black;
    padding: 12px;
    font-size: 15px;
    border-radius: 10px;
    border: 2px solid #89acb7;
    }
    
    QLineEdit:hover {
        background: #9ec7d3;
        border: 2px solid #708d96;
    }

    QLineEdit::placeholder {
    color: gray;
    }

    QComboBox {
    background: #012d51;
    color: white;
    padding: 11px;
    font-size: 15px;
    border-radius: 10px;
    }

    
'''



btnStyle = '''
    QPushButton {
        background: #012d51;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-size: 12.5px;
    }

    QPushButton:hover {
        background: #024a7a
    }

    QPushButton:pressed {
        background: #011826;
    }
'''

qcombostyle = '''
    QComboBox {
        background-color: #00457a;
        font-size: 14px;
        font-weight: 600;
        color: white;
        padding: 10px;
        border: 2px solid #003a5b;
        border-radius: 8px;
        min-width: 150px;
    }

    QComboBox:hover { 
        background-color: #003e6d;
        border-color: #00263a; 
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        color: white;
        width: 30px;
        border-left: none;
        background: transparent;
    }

    QComboBox::down-arrow {
        image: url(''' + resources_path('frontend/img/flecha5.png').replace(os.sep, '/') + ''');
        width: 15px;
        height: 15px;
    }

    QComboBox QAbstractItemView {
        background: #023a66;
        color: white;
        selection-background-color: #015a8a;
        selection-color: #ffffff;
        padding: 4px;
        border-radius: 20px;
    }

    QComboBox QAbstractItemView::item {
        height: 30px;
        padding-left: 8px;
    }
'''

reset_dialog = '''
    QDialog { 
        background-color: #f7faff;
    }
    
    QLabel {
        font-size: 14px;
        font-weight: bold; 
        color: #2a4d69;
        margin-bottom: -20px;
    }
    
    #info_label {
        margin-top: -40px;
        margin-bottom: -20px;
        font-size: 12px;
    }
    
    QLineEdit {
        border: 1px solid #a3c2ff;
        border-radius: 6px;
        padding: 6px;
        background-color: #ffffff;
        color: black;
    }
    
    QLineEdit:focus {
        border: 1px solid #4a90e2;
        background-color: #f0f6ff; 
    }
    
    QPushButton {
        background: #012d51;
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-size: 13px;
    }

    QPushButton:hover {
        background: #024a7a
    }

    QPushButton:pressed {
        background: #011826;
    }
    
    QPushButton#cancelar { 
        background-color: #e74c3c; 
    }
    
    QPushButton#cancelar:hover {
        background-color: #c0392b; 
    }
    
'''

estilos_archivos = """
    /* Fondo principal blanco/gris muy claro */
    QWidget {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', sans-serif;
    }

    /* GroupBox estilizado */
    QGroupBox {
        font-weight: bold;
        border: 1px solid #cfd8dc;
        border-radius: 8px;
        margin-top: 10px; /* para dejar espacio al título */
        padding-top: 15px;
        background-color: #ffffff;
        color: #37474f;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        color: #012d51;
        background-color: #f4f7f6; /* mismo que el fondo para "cortar" el borde */
    }

    /* Labels */
    QLabel {
        color: #455a64;
        font-size: 14px;
        font-weight: 500;
        background-color: transparent;
    }

    /* ListWidget */
    QListWidget {
        background-color: #ffffff;
        border: 1px solid #cfd8dc;
        border-radius: 8px;
        padding: 8px;
        font-size: 13px;
        color: #263238;
        outline: none;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #eceff1;
    }
    QListWidget::item:selected {
        background-color: #012d51;
        color: white;
        border-radius: 4px;
    }
    QListWidget::item:hover:!selected {
        background-color: #eceff1;
    }

    /* Combobox (estilo local para sobrescribir o complementar) */
    QComboBox {
        background-color: #ffffff;
        color: black;
        border: 1px solid #cfd8dc;
        border-radius: 5px;
        padding: 6px 10px;
        min-width: 120px;
        font-size: 13px;
    }
    QComboBox:hover {
        border-color: #012d51;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 30px; 
        border: none;
        background: transparent;
        color: black;
    }
    QComboBox::down-arrow {
        image: url(''' + resources_path('frontend/img/flecha5.png').replace(os.sep, '/') + '''); /* si tienes icono, si no, usa default */
        width: 12px;
        height: 12px;
        color: black;
    }
    /* Si no hay icono, Qt usa uno por defecto o podemos omitir la imagen */

    /* Botones generales */
    QPushButton {
        background-color: #012d51;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #024a7a;
    }
    QPushButton:pressed {
        background-color: #011826;
    }

    /* Boton Refrescar o secundarios si quieres diferenciar */
    QPushButton#btn_refresh {
        background-color: #546e7a;
    }
    QPushButton#btn_refresh:hover {
        background-color: #455a64;
    }

    /* Boton Eliminar (danger) */
    QPushButton#btn_delete {
        background-color: #d32f2f;
    }
    QPushButton#btn_delete:hover {
        background-color: #c62828;
    }
    
    /* Status Label */
    QLabel#lbl_status {
        color: #0277bd;
        font-style: italic;
    }
"""

estilos_formularios = """
    QDialog { 
        background-color: #f7faff;
        font-family: 'Segoe UI', sans-serif;
    }
    
    QLabel {
        font-size: 14px;
        font-weight: bold; 
        color: #2a4d69;
        margin-bottom: 2px;
        margin-top: 5px;
        background-color: #f7faff;
    }
    
    QLineEdit, QComboBox, QSpinBox, QTextEdit {
        border: 1px solid #a3c2ff;
        border-radius: 6px;
        padding: 8px;
        background-color: #ffffff;
        color: black;
        font-size: 13px;
    }
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
        border: 2px solid #4a90e2;
        background-color: #f0f6ff; 
    }

    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        color: black;
        width: 30px;
        border-left: none;
        background: transparent;
    }

    QComboBox::down-arrow {
        image: url(''' + resources_path('frontend/img/flecha5.png').replace(os.sep, '/') + ''');
        width: 15px;
        height: 15px;
    }
    
    QPushButton {
        background-color: #012d51;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
    }

    QPushButton:hover {
        background-color: #024a7a;
    }

    QPushButton:pressed {
        background-color: #011826;
    }
    
    QPushButton#cancelar { 
        background-color: #e74c3c; 
    }
    
    QPushButton#cancelar:hover {
        background-color: #c0392b; 
    }
"""

estilos_paginas = """
    QWidget {
        background-color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    QLabel {
        font-size: 14px;
        color: #333;
    }
    
    QLabel#titulo {
        font-size: 18px;
        font-weight: bold;
        color: #0b2e73;
        margin: 10px;
    }

    QComboBox {
        background-color: white;
        color: #333;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 5px;
        min-width: 150px;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }

    QLineEdit {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 5px 8px;
        font-size: 13px;
        background-color: white;
        color: #333;
    }
    QLineEdit:focus {
        border: 1px solid #4d79ff;
    }

    /* Tablas */
    QTableWidget {
        background-color: white;
        color: black;
        alternate-background-color: #f9f9f9;
        border: 1px solid #ddd;
        selection-background-color: #e6f0ff;
        selection-color: black;
        font-size: 13px;
    }

    QHeaderView::section {
        background-color: #f1f2f6;
        padding: 8px;
        border: 1px solid #ddd;
        font-weight: bold;
        color: #333;
    }

    /* Botones */
    QPushButton {
        background-color: #4d79ff;
        color: white;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 13px;
        font-weight: 600;
        border: none;
    }

    QPushButton:hover {
        background-color: #3355cc;
    }

    QPushButton#btn_editar {
        background-color: #4d79ff;
    }
    QPushButton#btn_editar:hover {
        background-color: #3355cc;
    }

    QPushButton#btn_eliminar {
        background-color: #e74c3c;
    }
    QPushButton#btn_eliminar:hover {
        background-color: #c0392b;
    }
"""