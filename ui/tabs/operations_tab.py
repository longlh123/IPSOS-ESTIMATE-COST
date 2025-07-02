# ui/tabs/qc_tab.py
# -*- coding: utf-8 -*-
"""
QC Method tab for the Project Cost Calculator application.
Manages QC methods, teams, and rates.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QHeaderView,
    QMessageBox, QScrollArea, QFrame, QSpinBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal, Slot

from models.project_model import ProjectModel
from config.predefined_values import *
from components.validation_field import FieldValidator
from ui.events.wheelBlocker import WheelBlocker
from ui.widgets.generic_editor_widget import GenericEditorWidget
from ui.helpers.form_helpers import (create_header_label, create_input_field, create_combobox, create_multiselected_field, create_textedit_field, 
                                     create_radiobuttons_group, create_spinbox_field
                                     )
from ui.helpers.form_events import bind_input_handler, bind_combobox_handler, bind_multiselection_handler, bind_textedit_handler, bind_radiogroup_handler, bind_spinbox_handler


class OperationsTab(QWidget):
    """
    Tab for managing QC methods, teams, and rates.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        self.validator = FieldValidator()

        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create a widget for the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Create the four regions
        self.wheel_blocker = WheelBlocker()

        self.region_clt = self.create_region_clt()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_clt.findChildren(QSpinBox) + self.region_clt.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
        
        self.region_device = self.create_region_device()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_device.findChildren(QSpinBox) + self.region_device.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        self.region_printer = self.create_region_printer()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_printer.findChildren(QSpinBox) + self.region_printer.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
        

        self.region_qc_methods = self.create_region_qc_method()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_qc_methods.findChildren(QSpinBox) + self.region_qc_methods.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        # # Add regions to layout
        scroll_layout.addWidget(self.region_clt)
        scroll_layout.addWidget(self.region_device)
        scroll_layout.addWidget(self.region_printer)
        scroll_layout.addWidget(self.region_qc_methods)

        scroll_layout.addStretch()
        
        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)

        # Initial update from model
        self.update_from_model()

    def update_region_visibility(self):
        """Show/hide regions based on project type selection."""
        project_type = self.project_model.general.get("project_type", "")
        
        # Show/hide HUT region
        # if hasattr(self, 'region_hut'):
        #     self.region_hut.setVisible("HUT" in project_type)
        
        # Show/hide CLT region  
        if hasattr(self, 'region_clt'):
            self.region_clt.setVisible("CLT" in project_type)

    def handle_project_type_changed(self, value: str):
        self.region_clt.setVisible("CLT" in value)

    def create_region_clt(self):
        """Create the CLT (Central Location Test) region."""
        group_box = QGroupBox("CLT (Central Location Test)")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        create_header_label(layout, "CLT Settings", row=0, col=0, rowspan=1, colspan=4)

        # Assistant Set Up Days - NEW FIELD
        create_spinbox_field(layout, self, "clt_assistant_setup_days", "Assistant set up needs:", range=(0, 30), suffix="", row=1, col=0)

        bind_spinbox_handler(self, "clt_assistant_setup_days", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Failure Rate
        create_spinbox_field(layout, self, "clt_failure_rate", "Failure Rate:", range=(0, 999), suffix="%", row=2, col=0)

        bind_spinbox_handler(self, "clt_failure_rate", validator=self.validator, update_func=self.project_model.update_clt_settings)

        #--Số ngày dán mẫu
        create_spinbox_field(layout, self, "clt_dan_mau_days", "Số ngày dán mẫu:", range=(0, 30), suffix=" day(s)", row=3, col=0)

        bind_spinbox_handler(self, "clt_dan_mau_days", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Sample size target per day
        create_spinbox_field(layout, self, "clt_sample_size_per_day", "Sample Size Target per Day:", range=(0, 100), suffix="", row=4, col=0)

        bind_spinbox_handler(self, "clt_sample_size_per_day", validator=self.validator, update_func=self.project_model.update_clt_settings)

        create_header_label(layout, "NGỒI BÀN Settings", row=5, col=0, rowspan=1, colspan=4)

        # Number of desk-based interviewers (NGỒI BÀN)
        create_spinbox_field(layout, self, "clt_desk_interviewers_count", "Số lượng PVV tham gia dự án (NGỒI BÀN):", range=(0, 999), suffix="", row=6, col=0)

        bind_spinbox_handler(self, "clt_desk_interviewers_count", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Number of provincial desk-based interviewers
        create_spinbox_field(layout, self, "clt_provincial_desk_interviewers_count", "Số lượng PVV đi tỉnh (NGỒI BÀN):", range=(0, 999), suffix="", row=6, col=2)

        bind_spinbox_handler(self, "clt_provincial_desk_interviewers_count", validator=self.validator, update_func=self.project_model.update_clt_settings)

        return group_box
    
    def create_region_printer(self):
        """Create the Printer region."""
        group_box = QGroupBox("Printer")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        # BACKWHITE page count
        create_spinbox_field(layout, self, "bw_page_count", "Số trang photo trắng đen:", range=(0, 999), suffix=" (pages)", row=0, col=0)
        
        bind_spinbox_handler(self, "bw_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # SHOWPHOTO page count
        create_spinbox_field(layout, self, "showphoto_page_count", "Số trang showphoto:", range=(0, 999), suffix=" (pages)", row=0, col=2)
        
        bind_spinbox_handler(self, "showphoto_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # SHOWCARD page count
        create_spinbox_field(layout, self, "showcard_page_count", "Số trang showcard:", range=(0, 999), suffix=" (pages)", row=1, col=0)
        
        bind_spinbox_handler(self, "showcard_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # DROPCARD page count
        create_spinbox_field(layout, self, "dropcard_page_count", "Số trang dropcard:", range=(0, 999), suffix=" (pages)", row=1, col=2)
        
        bind_spinbox_handler(self, "dropcard_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # COLOR page count
        create_spinbox_field(layout, self, "color_page_count", "Số trang in màu \ in concept:", range=(0, 999), suffix=" (pages)", row=2, col=0)
        
        bind_spinbox_handler(self, "color_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # DECAL page count
        create_spinbox_field(layout, self, "decal_page_count", "Số decal dán mẫu:", range=(0, 999), suffix=" (pages)", row=2, col=2)
        
        bind_spinbox_handler(self, "decal_page_count", validator=self.validator, update_func=self.project_model.update_general)
        
        # Laminated page count
        create_spinbox_field(layout, self, "laminated_page_count", "Số trang ép plastic:", range=(0, 999), suffix=" (pages)", row=3, col=0)
        
        bind_spinbox_handler(self, "laminated_page_count", validator=self.validator, update_func=self.project_model.update_general)

        # Hồ sơ biểu mẫu
        create_spinbox_field(layout, self, "interview_form_package_count", "Hồ sơ biểu mẫu:", range=(0, 999), suffix=" (pages)", row=3, col=2)
        
        bind_spinbox_handler(self, "interview_form_package_count", validator=self.validator, update_func=self.project_model.update_general)

        # Đóng cuốn
        create_spinbox_field(layout, self, "stimulus_material_production_count", "Chi phí đóng cuốn:", range=(0, 999), suffix=" (pages)", row=4, col=0)
        
        bind_spinbox_handler(self, "stimulus_material_production_count", validator=self.validator, update_func=self.project_model.update_general)

        return group_box
    
    def create_region_qc_method(self):
        group_box = QGroupBox("QC Method")

        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        qc_method_label = QLabel("QC Method:")
        qc_method_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(qc_method_label, 4, 0)

        self.qc_methods = GenericEditorWidget(
            title="QC Method",
            field_config = [
                { "name": "team", "label": "Team", "widget": QComboBox, "options" : TEAMS, "required": True, "duplicated" : True },
                { "name": "qc_method", "label": "QC Method", "widget": QComboBox, "options": QC_METHODS, "required": True, "duplicated" : True},
                { "name": "qc_rate", "label" : "Rate", "widget" : QSpinBox, "min": 0, "max": 100, "suffix": "%", "required": True, "min_range" : 1 } 
            ]
        )

        self.qc_methods.selectionChanged.connect(
            lambda items : self.project_model.update_qc_methods(items)
        )
        
        layout.addWidget(self.qc_methods, 4, 1, 1, 3)

        return group_box
    
    def create_region_device(self):
        group_box = QGroupBox("Device")

        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch

        # Tablet/Laptop selection
        create_combobox(layout, self, "device_type", "Thuê tablet / laptop:", items=DEVIVE_TYPES, row=0, col=0)

        bind_combobox_handler(self, "device_type", validator=self.validator, update_func=self.project_model.update_general)

        # Tablet usage duration - only shown when "Tablet < 9 inch" is selected
        create_combobox(layout, self, "tablet_usage_duration", "Thời gian sử dụng tablet:", items=TABLET_USAGE_DURATIONS, row=0, col=2)

        bind_combobox_handler(self, "tablet_usage_duration", validator=self.validator, update_func=self.project_model.update_general)

        return group_box
    
    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""

        self.clt_assistant_setup_days_spinbox.setValue(self.project_model.clt_settings["clt_assistant_setup_days"])

        self.clt_failure_rate_spinbox.setValue(self.project_model.clt_settings.get("clt_failure_rate", 0))
        self.project_model.set_selected_failure_rate_costs(self.project_model.clt_settings.get("clt_failure_rate", 0) != 0)

        self.clt_dan_mau_days_spinbox.setValue(self.project_model.clt_settings["clt_dan_mau_days"])
        self.clt_sample_size_per_day_spinbox.setValue(self.project_model.clt_settings["clt_sample_size_per_day"])

        #QC Method
        self.qc_methods.set_selected_items(self.project_model.qc_methods)

        self.project_model.set_selected_qc_method_costs()

        value = self.project_model.general["device_type"]
        
        self.device_type_combobox.blockSignals(True)

        if value and value in DEVIVE_TYPES:
            self.device_type_combobox.setCurrentText(value)
        else:
            self.device_type_combobox.setCurrentIndex(0)

        self.project_model.set_selected_device_cost(value)

        self.device_type_combobox.blockSignals(False)
        
        value = self.project_model.general["tablet_usage_duration"]

        self.tablet_usage_duration_combobox.blockSignals(True)

        if value and value in TABLET_USAGE_DURATIONS:
            self.tablet_usage_duration_combobox.setCurrentText(value)
        else:
            self.tablet_usage_duration_combobox.setCurrentIndex(0)
        
        self.tablet_usage_duration_combobox.setEnabled(self.project_model.general["device_type"] == "Tablet < 9 inch")

        self.tablet_usage_duration_combobox.blockSignals(False)

        # Update Printer
        self.bw_page_count_spinbox.setValue(self.project_model.general["bw_page_count"])
        self.showphoto_page_count_spinbox.setValue(self.project_model.general["showphoto_page_count"])
        self.showcard_page_count_spinbox.setValue(self.project_model.general["showcard_page_count"])
        self.dropcard_page_count_spinbox.setValue(self.project_model.general["dropcard_page_count"])
        self.color_page_count_spinbox.setValue(self.project_model.general["color_page_count"])
        self.decal_page_count_spinbox.setValue(self.project_model.general["decal_page_count"])
        self.laminated_page_count_spinbox.setValue(self.project_model.general["laminated_page_count"])
        self.interview_form_package_count_spinbox.setValue(self.project_model.general["interview_form_package_count"])
        self.stimulus_material_production_count_spinbox.setValue(self.project_model.general["stimulus_material_production_count"])

        self.project_model.set_selected_stationary_costs()

        self.update_region_visibility()