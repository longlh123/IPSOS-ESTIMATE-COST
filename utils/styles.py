from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt

def apply_application_style(app: QApplication):
    # Set default font
    default_font = QFont('Arial', 11)  # Increased base font size
    app.setFont(default_font)
    
    # Create and set application palette for colors
    palette = QPalette()
    
    # Set window background color to light blue-gray
    palette.setColor(QPalette.Window, QColor(240, 244, 248))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    
    # Set button colors
    palette.setColor(QPalette.Button, QColor(52, 152, 219))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    
    # Set input field colors
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 250, 252))
    
    # Set highlight colors
    palette.setColor(QPalette.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)
    
    # Set global stylesheet for widgets
    app.setStyleSheet("""
        QWidget {
            font-size: 11pt;
        }
        
        QGroupBox {
            font-size: 12pt;
            font-weight: bold;
            border: 2px solid #BDC3C7;
            border-radius: 5px;
            margin-top: 1em;
            padding-top: 1em;
        }
        
        QGroupBox::title {
            color: #2C3E50;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        
        QPushButton {
            min-height: 35px;
            min-width: 100px;
            padding: 5px 15px;
            background-color: #3498DB;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #2980B9;
        }
        
        QPushButton:pressed {
            background-color: #2574A9;
        }
        
        QLineEdit, QSpinBox, QComboBox {
            min-height: 30px;
            padding: 5px;
            border: 2px solid #BDC3C7;
            border-radius: 4px;
            background-color: white;
        }
        
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #3498DB;
        }
        
        QTableWidget {
            border: 2px solid #BDC3C7;
            border-radius: 4px;
            gridline-color: #ECF0F1;
        }
        
        QHeaderView::section {
            background-color: #3498DB;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
        
        QScrollBar:vertical {
            border: none;
            background-color: #F0F0F0;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #BDC3C7;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #95A5A6;
        }
        
        QLabel {
            color: #2C3E50;
            font-size: 11pt;
        }
    """)