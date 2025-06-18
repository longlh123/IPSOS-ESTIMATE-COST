from PySide6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QSpinBox, QComboBox, QCheckBox,
                             QPushButton)
import pandas as pd
import os

class DynamicField(QWidget):
    def __init__(self, field_config, parent=None):
        super().__init__(parent)
        self.field_config = field_config
        self.layout = QHBoxLayout()
        self.widget = self.create_widget()
        label = QLabel(field_config.get('placeholder', ''))
        label.setMinimumWidth(120)  # Set minimum width for labels
        self.layout.addWidget(label)
        self.layout.addWidget(self.widget)
        self.setLayout(self.layout)

    def create_widget(self):
        field_type = self.field_config['type']
        if field_type == 'string':
            widget = QLineEdit()
            widget.setPlaceholderText(self.field_config.get('placeholder', ''))
            widget.setMinimumWidth(200)  # Set minimum width for input fields
        elif field_type == 'number':
            widget = QSpinBox()
            widget.setMinimum(self.field_config.get('min', 0))
            widget.setMaximum(self.field_config.get('max', 99999))
            widget.setMinimumWidth(200)  # Set minimum width for spinboxes
        elif field_type == 'combobox':
            widget = QComboBox()
            widget.setMinimumWidth(200)  # Set minimum width for comboboxes
            self.load_combobox_data(widget)
        elif field_type == 'checkboxgroup':
            widget = QWidget()
            layout = QVBoxLayout()
            self.checkboxes = []
            self.load_checkbox_data(layout)
            widget.setLayout(layout)
        else:
            widget = QLabel("Unsupported field type")

        widget.setEnabled(not self.field_config.get('disabled', False))
        return widget

    def load_combobox_data(self, combobox):
        try:
            if all(key in self.field_config for key in ['excelSheet', 'displayColumn', 'valueColumn']):
                excel_path = os.path.join('excel', 'DefinedInfo.xlsx')
                df = pd.read_excel(excel_path, sheet_name=self.field_config['excelSheet'], skiprows=1)
                display_values = df.iloc[:, 0].tolist()
                combobox.addItems(display_values)
        except Exception as e:
            print(f"Error loading combobox data: {str(e)}")
    
    def load_checkbox_data(self, layout):
        try:
            if all(key in self.field_config for key in ['excelSheet', 'displayColumn', 'valueColumn']):
                excel_path = os.path.join('excel', 'DefinedInfo.xlsx')
                df = pd.read_excel(excel_path, sheet_name=self.field_config['excelSheet'], skiprows=1)
                for value in df.iloc[:, 0]:
                    checkbox = QCheckBox(str(value))
                    checkbox.setStyleSheet("""
                        QCheckBox {
                            spacing: 10px;
                            font-size: 11pt;
                        }
                        QCheckBox::indicator {
                            width: 20px;
                            height: 20px;
                        }
                    """)
                    self.checkboxes.append(checkbox)
                    layout.addWidget(checkbox)
        except Exception as e:
            print(f"Error loading checkbox data: {str(e)}")

    def get_value(self):
        if self.field_config['type'] == 'string':
            return self.widget.text()
        elif self.field_config['type'] == 'number':
            return self.widget.value()
        elif self.field_config['type'] == 'combobox':
            return self.widget.currentText()
        elif self.field_config['type'] == 'checkboxgroup':
            return [cb.text() for cb in self.checkboxes if cb.isChecked()]
        return None

    def set_value(self, value):
        if self.field_config['type'] == 'string':
            self.widget.setText(str(value))
        elif self.field_config['type'] == 'number':
            self.widget.setValue(int(value))
        elif self.field_config['type'] == 'combobox':
            index = self.widget.findText(str(value))
            if index >= 0:
                self.widget.setCurrentIndex(index)
        elif self.field_config['type'] == 'checkboxgroup':
            for checkbox in self.checkboxes:
                checkbox.setChecked(checkbox.text() in value)

class DynamicGroup(QGroupBox):
    def __init__(self, group_name, group_config, parent=None):
        super().__init__(group_name, parent)
        self.group_config = group_config
        self.fields = {}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Add spacing between fields
        
        # Add standard fields
        fields_widget = QWidget()
        fields_layout = QVBoxLayout()
        fields_layout.setSpacing(10)  # Add spacing between fields
        
        for field_name, field_config in self.group_config['fields'].items():
            field_container = QWidget()
            container_layout = QHBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            field_widget = DynamicField(field_config)
            self.fields[field_name] = field_widget
            
            container_layout.addWidget(field_widget)
            container_layout.addStretch()  # Add stretch to push fields to the left
            field_container.setLayout(container_layout)
            fields_layout.addWidget(field_container)

        fields_widget.setLayout(fields_layout)
        layout.addWidget(fields_widget)

        # Add custom fields section if needed
        if self.group_config.get('customFields'):
            custom_section = QGroupBox("Custom Fields")
            custom_section.setStyleSheet("""
                QGroupBox {
                    margin-top: 20px;
                    padding-top: 20px;
                }
            """)
            custom_layout = QVBoxLayout()
            add_button = QPushButton("Add Custom Field")
            add_button.clicked.connect(self.add_custom_field)
            custom_layout.addWidget(add_button)
            custom_section.setLayout(custom_layout)
            layout.addWidget(custom_section)

        layout.addStretch()  # Add stretch at the bottom to push content up
        self.setLayout(layout)

    def add_custom_field(self):
        # Implementation for adding custom fields
        pass

    def get_data(self):
        data = {}
        for field_name, field_widget in self.fields.items():
            data[field_name] = field_widget.get_value()
        return data

    def set_data(self, data):
        for field_name, value in data.items():
            if field_name in self.fields:
                self.fields[field_name].set_value(value)