import os
import json
import pandas as pd
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QScrollArea, QMessageBox, QFileDialog)
from components.province import ProvinceGroup
from components.dynamic_components import DynamicGroup
from components.rate_card import RateCardWindow

class ProjectForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.groups = {}
        self.setup_ui()

    def load_config(self):
        try:
            with open('form_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading configuration: {str(e)}")
            return {}

    def setup_ui(self):
        self.setWindowTitle('Project Information Form')
        
        # Create central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # Add spacing between elements

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)  # Add spacing between groups

        # Create groups from configuration
        for group_name, group_config in self.config.items():
            if group_name == "Province":
                group = ProvinceGroup(group_name, group_config)
            else:
                group = DynamicGroup(group_name, group_config)
            self.groups[group_name] = group
            scroll_layout.addWidget(group)

        # Add buttons with improved styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # Add spacing between buttons
        
        buttons = [
            ("Load", self.load_form),
            ("Save", self.save_form),
            ("Estimate Level", self.estimate_level),
            ("Estimate Cost", lambda: None)  # Placeholder for estimate cost
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)  # Make buttons taller
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)

        # Set layouts
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        main_layout.addLayout(button_layout)
        
        # Add padding to main layout
        main_layout.setContentsMargins(20, 20, 20, 20)

    def get_form_data(self):
        data = {}
        for group_name, group in self.groups.items():
            data[group_name] = group.get_data()
        return data

    def set_form_data(self, data):
        for group_name, group_data in data.items():
            if group_name in self.groups:
                self.groups[group_name].set_data(group_data)

    def save_form(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Form Data", "", "JSON Files (*.json)")
            if file_name:
                data = self.get_form_data()
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Success", "Form saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving form: {str(e)}")

    def load_form(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Load Form Data", "", "JSON Files (*.json)")
            if file_name:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.set_form_data(data)
                QMessageBox.information(self, "Success", "Form loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading form: {str(e)}")

    def estimate_level(self):
        try:
            # Get values from form
            team = self.groups["Details"].fields["Team"].get_value()
            nganh_hang = self.groups["Details"].fields["NganhHang"].get_value()
            project_type = self.groups["Details"].fields["ProjectType"].get_value()
            loi = self.groups["Details"].fields["LOI"].get_value()
            do_tuoi = self.groups["Details"].fields["DoTuoi"].get_value()
            gioi_tinh = self.groups["Details"].fields["GioiTinh"].get_value()
            thu_nhap = self.groups["Details"].fields["ThuNhap"].get_value()
            
            # Read profile.xlsx
            profile_path = os.path.join('excel', 'profile.xlsx')
            df = pd.read_excel(profile_path, sheet_name="THU THẬP THÔNG TIN", skiprows=4)
            
            # Find matching row
            matching_row = df[
                (df.iloc[:, 1].str.lower() == team.lower()) &
                (df.iloc[:, 2].str.lower() == nganh_hang.lower()) &
                (df.iloc[:, 3].str.lower() == project_type.lower()) &
                (df.iloc[:, 4].str.lower() == loi.lower()) &
                (df.iloc[:, 5].str.lower() == do_tuoi.lower()) &
                (df.iloc[:, 7].str.lower() == gioi_tinh.lower()) &
                (df.iloc[:, 10].str.lower() == thu_nhap.lower())
            ]
            
            if matching_row.empty:
                QMessageBox.warning(self, "Warning", "No matching profile found!")
                return
                
            # Get rate card value
            rate_value = matching_row.iloc[0, 0]
            
            # Create and show rate card window
            self.rate_card_window = RateCardWindow(rate_value)
            self.rate_card_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error calculating rate card: {str(e)}")