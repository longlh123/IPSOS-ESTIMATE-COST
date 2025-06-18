from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton

class CustomFieldWidget(QWidget):
    def __init__(self, field_name, field_type, parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self.field_type = field_type
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        self.name_label = QLabel(self.field_name)
        
        if self.field_type == "string":
            self.field_widget = QLineEdit()
        elif self.field_type == "number":
            self.field_widget = QSpinBox()
            self.field_widget.setRange(0, 99999)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.deleteLater)
        
        layout.addWidget(self.name_label)
        layout.addWidget(self.field_widget)
        layout.addWidget(delete_btn)
        self.setLayout(layout)

    def get_value(self):
        if self.field_type == "string":
            return self.field_widget.text()
        elif self.field_type == "number":
            return self.field_widget.value()

    def set_value(self, value):
        if self.field_type == "string":
            self.field_widget.setText(str(value))
        elif self.field_type == "number":
            self.field_widget.setValue(int(value))