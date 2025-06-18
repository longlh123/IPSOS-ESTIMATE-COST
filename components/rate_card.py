from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class RateCardWindow(QWidget):
    def __init__(self, rate_value):
        super().__init__()
        self.setWindowTitle('Rate Card')
        self.setMinimumSize(500, 200)  # Increased window size
        self.setup_ui(rate_value)

    def setup_ui(self, rate_value):
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Add spacing between elements
        
        # Rate card value display
        rate_label = QLabel(f"Rate Card: {rate_value}")
        rate_label.setAlignment(Qt.AlignCenter)
        font = QFont('Arial', 16, QFont.Bold)  # Increased font size and made bold
        rate_label.setFont(font)
        rate_label.setStyleSheet("""
            QLabel {
                color: #2C3E50;
                padding: 20px;
                background-color: #ECF0F1;
                border-radius: 10px;
            }
        """)
        
        # Estimate Cost button
        estimate_btn = QPushButton("Estimate Cost")
        estimate_btn.setMinimumHeight(40)  # Make button taller
        estimate_btn.setFont(QFont('Arial', 12))  # Increased font size
        
        layout.addWidget(rate_label)
        layout.addWidget(estimate_btn)
        layout.setAlignment(Qt.AlignCenter)
        
        # Add some padding to the layout
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(layout)