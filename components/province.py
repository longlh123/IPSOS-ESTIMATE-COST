from PySide6.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QSpinBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QWidget, QLineEdit)
import pandas as pd
import os
from .custom_field import CustomFieldWidget

class ProvinceTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Province Name", "Sampling", "Sample Size"])
        self.setFixedHeight(300)  # Set fixed height to 300px
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
    def add_row(self, province, sampling, sample_size):
        row_position = self.rowCount()
        self.insertRow(row_position)
        self.setItem(row_position, 0, QTableWidgetItem(str(province)))
        self.setItem(row_position, 1, QTableWidgetItem(str(sampling)))
        self.setItem(row_position, 2, QTableWidgetItem(str(sample_size)))

    def get_data(self):
        data = []
        for row in range(self.rowCount()):
            row_data = {
                "province": self.item(row, 0).text(),
                "sampling": self.item(row, 1).text(),
                "sample_size": self.item(row, 2).text()
            }
            data.append(row_data)
        return data

    def set_data(self, data):
        self.setRowCount(0)
        for row_data in data:
            self.add_row(
                row_data["province"],
                row_data["sampling"],
                row_data["sample_size"]
            )

class ProvinceGroup(QGroupBox):
    def __init__(self, group_name, group_config, parent=None):
        super().__init__(group_name, parent)
        self.group_config = group_config
        self.fields = {}
        self.custom_fields = {}
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Selection layout
        selection_layout = QHBoxLayout()
        
        # Province selection
        province_layout = QVBoxLayout()
        province_label = QLabel("Select Province:")
        self.province_combo = QComboBox()
        self.load_province_data()
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        selection_layout.addLayout(province_layout)
        
        # Sample type selection
        sample_layout = QVBoxLayout()
        sample_label = QLabel("Sample Type:")
        self.sample_combo = QComboBox()
        self.load_sample_data()
        sample_layout.addWidget(sample_label)
        sample_layout.addWidget(self.sample_combo)
        selection_layout.addLayout(sample_layout)
        
        # Sample size input
        size_layout = QVBoxLayout()
        size_label = QLabel("Sample Size:")
        self.size_input = QSpinBox()
        self.size_input.setRange(0, 99999)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_input)
        selection_layout.addLayout(size_layout)
        
        # Add button
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_to_table)
        selection_layout.addWidget(add_button)
        
        main_layout.addLayout(selection_layout)
        
        # Table
        self.table = ProvinceTable()
        main_layout.addWidget(self.table)
        
        # Custom fields section
        custom_section = QGroupBox("Custom Fields")
        custom_layout = QVBoxLayout()
        self.custom_fields_layout = QVBoxLayout()
        
        # Add custom field controls
        add_field_layout = QHBoxLayout()
        self.custom_field_name = QLineEdit()
        self.custom_field_name.setPlaceholderText("Field Name")
        self.custom_field_type = QComboBox()
        self.custom_field_type.addItems(["string", "number"])
        add_field_button = QPushButton("Add Custom Field")
        add_field_button.clicked.connect(self.add_custom_field)
        
        add_field_layout.addWidget(self.custom_field_name)
        add_field_layout.addWidget(self.custom_field_type)
        add_field_layout.addWidget(add_field_button)
        
        custom_layout.addLayout(add_field_layout)
        custom_layout.addLayout(self.custom_fields_layout)
        custom_section.setLayout(custom_layout)
        main_layout.addWidget(custom_section)
        
        self.setLayout(main_layout)

    def load_province_data(self):
        try:
            excel_path = os.path.join('excel', 'DefinedInfo.xlsx')
            df = pd.read_excel(excel_path, sheet_name='City', skiprows=1)
            self.province_combo.addItems(df.iloc[:, 0].tolist())
        except Exception as e:
            print(f"Error loading province data: {str(e)}")

    def load_sample_data(self):
        try:
            excel_path = os.path.join('excel', 'DefinedInfo.xlsx')
            df = pd.read_excel(excel_path, sheet_name='SampleType', skiprows=1)
            self.sample_combo.addItems(df.iloc[:, 0].tolist())
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")

    def add_to_table(self):
        province = self.province_combo.currentText()
        sample_type = self.sample_combo.currentText()
        sample_size = self.size_input.value()
        self.table.add_row(province, sample_type, sample_size)

    def add_custom_field(self):
        field_name = self.custom_field_name.text()
        field_type = self.custom_field_type.currentText()
        
        if field_name and field_name not in self.custom_fields:
            custom_field = CustomFieldWidget(field_name, field_type)
            self.custom_fields[field_name] = custom_field
            self.custom_fields_layout.addWidget(custom_field)
            self.custom_field_name.clear()

    def get_data(self):
        data = {
            "table_data": self.table.get_data(),
            "custom_fields": {}
        }
        
        for field_name, field_widget in self.custom_fields.items():
            data["custom_fields"][field_name] = {
                "type": field_widget.field_type,
                "value": field_widget.get_value()
            }
            
        return data

    def set_data(self, data):
        if "table_data" in data:
            self.table.set_data(data["table_data"])
            
        if "custom_fields" in data:
            for field_name, field_data in data["custom_fields"].items():
                if field_name not in self.custom_fields:
                    custom_field = CustomFieldWidget(field_name, field_data["type"])
                    self.custom_fields[field_name] = custom_field
                    self.custom_fields_layout.addWidget(custom_field)
                self.custom_fields[field_name].set_value(field_data["value"])