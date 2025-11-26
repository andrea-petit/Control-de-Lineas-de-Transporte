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
        font-size: 13px;
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
        color: #ffffff;
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
        width: 30px;
        border-left: none;
        background: transparent;
    }

    QComboBox::down-arrow {
        image: url(./frontend/img/flecha5.png);
        width: 15px;
        height: 15px;
    }

    QComboBox QAbstractItemView {
        background: #023a66;
        color: #ffffff;
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