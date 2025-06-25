# ui/tabs/general_tab.py
# -*- coding: utf-8 -*-
"""
General tab for the Project Cost Calculator application.
Contains four regions of input fields.
"""
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QGroupBox,
    QScrollArea, QSizePolicy, QPushButton, QFrame,
    QButtonGroup, QRadioButton, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal, Slot

from models.project_model import ProjectModel
from config.predefined_values import *
from ui.widgets.multi_select import MultiSelectWidget
from ui.widgets.target_audience_widget import TargetAudienceWidget
from ui.widgets.generic_editor_widget import GenericEditorWidget
from components.validation_field import FieldValidator
from ui.events.wheelBlocker import WheelBlocker 

class GeneralTab(QWidget):
    """
    Tab for general project information, divided into four regions.
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

        region_general_information = self.create_region_general_information()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in region_general_information.findChildren(QSpinBox) + region_general_information.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        region_dp = self.create_region_dp()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in region_dp.findChildren(QSpinBox) + region_dp.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
    
        region_subcontract = self.create_region_subcontract()

        region_printer = self.create_region_printer()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in region_printer.findChildren(QSpinBox) + region_printer.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
        
        region_clt = self.create_region_clt()
        region_hut = self.create_region_hut()
        
        # Add regions to layout
        scroll_layout.addWidget(region_general_information)
        scroll_layout.addWidget(region_dp)
        scroll_layout.addWidget(region_subcontract)
        scroll_layout.addWidget(region_printer)
        scroll_layout.addWidget(region_clt)
        scroll_layout.addWidget(region_hut)

        scroll_layout.addStretch()
        
        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # After setting up all UI elements, explicitly trigger updates for comboboxes
        # This ensures initial values are saved to the model
        if self.project_type.currentText():
            self.project_model.update_general("project_type", self.project_type.currentText())
        
        if self.sampling_method.currentText():
            self.project_model.update_general("sampling_method", self.sampling_method.currentText())
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)

        # Initial update from model
        self.update_from_model()

        self.update_region_visibility()

    def update_region_visibility(self):
        """Show/hide regions based on project type selection."""
        project_type = self.project_model.general.get("project_type", "")
        
        # Show/hide HUT region
        if hasattr(self, 'region_hut'):
            self.region_hut.setVisible("HUT" in project_type)
        
        # Show/hide CLT region  
        if hasattr(self, 'region_clt'):
            self.region_clt.setVisible("CLT" in project_type)

    def handle_text_changed(self, field_name:str, value: str):
        is_valid, error = self.validator.validate(field_name, value)
        self.show_warning_message(field_name, error)

        if is_valid:
            self.project_model.update_general(field_name, value)
        else:
            field = getattr(self, field_name, None)

            if field:
                field.setFocus()

    def handle_combobox_changed(self, field_name:str, value:str):
        is_valid, error = self.validator.validate(field_name, value)
        self.show_warning_message(field_name, error)

        if is_valid:
            self.project_model.update_general(field_name, value)
            
            # Add this line to handle region visibility when project type changes
            if field_name == "project_type":
                self.update_region_visibility()

    def show_warning_message(self, field_name:str, message: str):
        label_name = f"{field_name}_warning"
        label = getattr(self, label_name, None)
        
        if label:
            label.setText(message)
            label.setVisible(bool(message))
            
    def create_input_field(self, layout, field_name, label, widget, row= 0, col= 0, rowspan= 0, colspan= 0, margins = None):
        if margins is None:
            margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}

        label_widget = QLabel(label)
        label_widget.setStyleSheet("margin-left: 10px;")
        layout.addWidget(label_widget, row, col)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(
            margins["left"], margins["top"], margins["right"], margins["bottom"]
        )
        container_layout.addWidget(widget)

        warning_label = QLabel("")
        warning_label.setStyleSheet("color: red; font-size: 12px;")
        warning_label.setVisible(False)
        container_layout.addWidget(warning_label)

        # Gán warning label thành thuộc tính self
        setattr(self, f"{field_name}_warning", warning_label)

        layout.addWidget(container, row, col + 1)

    def create_combobox(self, layout, field_name, label, widget, row= 0, col= 0, margins = None):
        if margins is None:
            margins = { "left": 0, "top": 0, "right": 0, "bottom": 0}

        label_widget = QLabel(label)
        label_widget.setStyleSheet("margin-left: 10px;")
        layout.addWidget(label_widget, row, col)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(widget)

        warning_label = QLabel("")
        warning_label.setStyleSheet("color: red; font-size: 12px")
        warning_label.setVisible(False)
        container_layout.addWidget(warning_label)

        # Gán warning label thành thuộc tính self
        setattr(self, f"{field_name}_warning", warning_label)

        layout.addWidget(container, row, col + 1)

    def create_spinbox(self, layout, field_name, label, widget, row=0, col=0, margins=None):
        if margins is None:
            margins = {"left": 0, "top": 0, "right": 0, "bottom": 0}
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet("margin-left: 10px")
        layout.addWidget(label_widget, row, col)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(
            margins["left"], margins["top"], margins["right"], margins["bottom"]
        )
        container_layout.addWidget(widget)

        layout.addWidget(container, row, col + 1)

    def create_group_header(self, title:str):
        container = QWidget()
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)

        label = QLabel(title)
        label.setStyleSheet("font-weight: bold;")

        layout.addWidget(label)
        return container

    def handle_platform_changed(self, button):
        platform = button.text()
        self.project_model.update_general("platform", platform)        

    def create_region_general_information(self):
        """Create the General Information region."""
        group_box = QGroupBox("General Information")

        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch
        
        row = 0

        layout.addWidget(self.create_group_header("Project Information"), row, 0, 1, 4) 
        row += 1

        ### Row 0 - Cell 0
        self.internal_job = QLineEdit()
        self.internal_job.textChanged.connect(
            lambda text: self.handle_text_changed("internal_job", text)
        )
        self.create_input_field(layout, "internal_job", "Internal Job:", self.internal_job, row=row, col=0)
        
        ### Row 0 - Cell 1
        self.symphony = QLineEdit()
        self.symphony.textChanged.connect(
            lambda text: self.handle_text_changed("symphony", text)
        )
        self.create_input_field(layout, "symphony", "Symphony:", self.symphony, row=row, col=2)
        
        row += 1

        ### Row 1 - Cell 0
        self.project_name = QLineEdit()
        self.project_name.textChanged.connect(
            lambda text: self.handle_text_changed("project_name", text)
        )
        self.create_input_field(layout, "project_name", "Project Name:", self.project_name, row=row, col=0)
        
        ### Project Type
        self.project_type = QComboBox()
        self.project_type.addItem("-- Select --")
        self.project_type.addItems(PROJECT_TYPES)
        
        # Set item đầu tiên là mặc định
        self.project_type.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.project_type.model().item(0).setEnabled(False)
        
        self.project_type.currentTextChanged.connect(
            lambda text: (
                self.handle_combobox_changed("project_type", text)
            )
        )

        self.create_combobox(layout, "project_type", "Project Type:", self.project_type, row=row, col=2)
        row += 1
        
        ### Clients
        clients_label = QLabel("Clients:")
        clients_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(clients_label, row, 0)

        self.clients = MultiSelectWidget(CLIENTS, allow_adding=True)
        
        self.clients.selectionChanged.connect(
            lambda items: self.project_model.update_general("clients", items)
        )
        
        layout.addWidget(self.clients, row, 1, 1, 3)
        row += 1
        
        ### Project Objectives
        project_objectives_label = QLabel("Project Objectives:")
        project_objectives_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(project_objectives_label, row, 0, 1, 4)

        row += 1

        self.project_objectives_container = QWidget()

        project_objectives_layout = QHBoxLayout(self.project_objectives_container)
        project_objectives_layout.setContentsMargins(0, 0, 0, 0)

        self.project_objectives_line_input = QTextEdit()
        self.project_objectives_line_input.setStyleSheet("margin-left: 10px;")
        self.project_objectives_line_input.setPlaceholderText("Enter your text here...")
        self.project_objectives_line_input.setAcceptRichText(True)

        self.project_objectives_line_input.textChanged.connect(
            lambda: self.project_model.update_general("project_objectives", self.project_objectives_line_input.toPlainText())
        )

        project_objectives_layout.addWidget(self.project_objectives_line_input)

        layout.addWidget(self.project_objectives_container, row, 0, 1, 4)

        row += 1

        layout.addWidget(self.create_group_header("Platform Details"), row, 0, 1, 4)
        row += 1

        ### Row 2 - Cell 0
        platform_label = QLabel("Platform:")
        platform_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(platform_label, row, 0)
        
        platform_layout = QHBoxLayout()
        platform_layout.setContentsMargins(0, 5, 0, 5)

        self.platform_button_group = QButtonGroup(self)
        self.ifield_radio = QRadioButton("iField")
        self.dimension_radio = QRadioButton("Dimension")
        
        self.platform_button_group.addButton(self.ifield_radio, 0)
        self.platform_button_group.addButton(self.dimension_radio, 1)
        
        self.platform_button_group.buttonClicked.connect(self.handle_platform_changed)
        
        # Set default to iField
        self.ifield_radio.setChecked(True)
        
        platform_layout.addWidget(self.ifield_radio)
        platform_layout.addWidget(self.dimension_radio)
        platform_layout.addStretch()
        
        layout.addLayout(platform_layout, row, 1, 1, 3)
        row += 1

        layout.addWidget(self.create_group_header("Quota & Sampling"), row, 0, 1, 4)
        row += 1

        ### Interview Methods
        interview_methods_label = QLabel("Interview Methods:")
        interview_methods_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(interview_methods_label, row, 0)

        self.interview_methods = MultiSelectWidget(INTERVIEW_METHODS)
        
        self.interview_methods.selectionChanged.connect(
            lambda items: self.project_model.update_general("interview_methods", items)
        )
        
        layout.addWidget(self.interview_methods, row, 1, 1, 3)
        row += 1

        ### Sampling Method
        self.sampling_method = QComboBox()
        self.sampling_method.addItem("-- Select --")
        self.sampling_method.addItems(SAMPLING_METHODS)

        # Set item đầu tiên là mặc định
        self.sampling_method.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.sampling_method.model().item(0).setEnabled(False)

        self.sampling_method.currentTextChanged.connect(
            lambda text: self.handle_combobox_changed("sampling_method", text)
        )

        self.create_combobox(layout, "sampling_method", "Sampling Method", self.sampling_method, row=row, col=0)
        
        ### Recruit Method
        recruit_method_label = QLabel("Recruit Method:")
        recruit_method_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(recruit_method_label, row, 2)

        self.recruit_method = MultiSelectWidget(RECRUIT_METHOD)

        self.recruit_method.selectionChanged.connect(
            lambda items: self.project_model.update_general("recruit_method", items)
        )

        layout.addWidget(self.recruit_method, row, 3)
        row += 1
        
        ### Type of Quota Controls
        self.type_of_quota_control = QComboBox()
        self.type_of_quota_control.addItem("--Select--")
        self.type_of_quota_control.addItems(TYPE_OF_QUOTA_CONTROLS)

        # Set item đầu tiên là mặc định
        self.type_of_quota_control.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.type_of_quota_control.model().item(0).setEnabled(False)

        self.type_of_quota_control.currentTextChanged.connect(
            lambda text: self.handle_combobox_changed("type_of_quota_control", text)
        )

        self.create_combobox(layout, "type_of_quota_control", "Type of Quota Control:", self.type_of_quota_control, row=row, col=0)
        
        ### Quota Description
        quota_description_label = QLabel("Quota Description:")
        quota_description_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(quota_description_label, row, 2)

        self.quota_description = MultiSelectWidget(QUOTA_DESCRIPTION)

        self.quota_description.selectionChanged.connect(
            lambda items: self.project_model.update_general("quota_description", items)
        )
        
        quota_description_container = QWidget()
        quota_description_layout = QVBoxLayout(quota_description_container)
        quota_description_layout.setContentsMargins(0, 0, 0, 0)
        quota_description_layout.addWidget(self.quota_description)

        self.quota_description_warning = QLabel("")
        self.quota_description_warning.setStyleSheet("color: red; font-size: 12px")
        self.quota_description_warning.setVisible(False)
        quota_description_layout.addWidget(self.quota_description_warning)

        layout.addWidget(quota_description_container, row, 3)
        row += 1

        layout.addWidget(self.create_group_header("Target Audience"), row, 0, 1, 4)
        row += 1

        ### Service Lines
        self.service_line = QComboBox()
        self.service_line.addItem("-- Select --")
        self.service_line.addItems(SERVICE_LINES)

        # Set item đầu tiên là mặc định
        self.service_line.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.service_line.model().item(0).setEnabled(False)

        self.service_line.currentTextChanged.connect(
            lambda text: self.project_model.update_general("service_line", text)
            if text != "-- Select --" else None # bỏ qua nếu đang là placeholder
        )

        self.create_combobox(layout, "service_line", "Service Line:", self.service_line, row=row, col=0)

        row += 1

        ### Provinces
        provinces_label = QLabel("Provinces:")
        provinces_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(provinces_label, row, 0)
        
        self.provinces = MultiSelectWidget(VIETNAM_PROVINCES)
        
        self.provinces.selectionChanged.connect(
            lambda items: self.project_model.update_general("provinces", items)
        )

        layout.addWidget(self.provinces, row, 1, 1, 3)
        row += 1

        ### Sample Types
        sample_types_label = QLabel("Sample Types:")
        sample_types_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(sample_types_label, row, 0)
        
        self.sample_types = MultiSelectWidget(SAMPLE_TYPES)
        
        self.sample_types.selectionChanged.connect(
            lambda items: self.project_model.update_general("sample_types", items)
        )
        
        layout.addWidget(self.sample_types, row, 1, 1, 3)
        row += 1
        
        ### Industries
        industries_label = QLabel("Industries:")
        industries_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(industries_label, row, 0)
        
        self.industries = MultiSelectWidget(list(self.project_model.industries_data))
        
        self.industries.selectionChanged.connect(
            lambda items: (
                # Cập nhật model
                self.project_model.update_general("industries", items),
            
                # Bật hoặc tắt Target Audience Widget
                self.target_audiences.set_enabled(len(items) > 0)
            )
        )

        layout.addWidget(self.industries, row, 1, 1, 3)
        row += 1

        ### Target Audience
        target_audience_label = QLabel("Target Audience:")
        target_audience_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(target_audience_label, row, 0)

        self.target_audiences = TargetAudienceWidget(self.project_model.industries_data)

        self.target_audiences.selectionChanged.connect(
            lambda items: (
                # Cập nhật model
                self.project_model.update_general("target_audiences", items)
            )
        )

        layout.addWidget(self.target_audiences, row, 1, 1, 3)
        row += 1
        
        layout.addWidget(self.create_group_header("Timing & Description"))
        row += 1
        
        ### Length of Interview (min)
        length_of_interview_label = QLabel("Length of Interview (min):")
        length_of_interview_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(length_of_interview_label, row, 0)

        self.interview_length = QSpinBox()
        self.interview_length.setRange(0, 999)
        
        self.interview_length.valueChanged.connect(
            lambda value: self.project_model.update_general("interview_length", value)
        )

        layout.addWidget(self.interview_length, row, 1)
        
        ### Length of Questionnaire
        length_of_questionaire_label = QLabel("Length of Questionnaire:")
        length_of_questionaire_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(length_of_questionaire_label, row, 2)

        self.questionnaire_length = QSpinBox()
        self.questionnaire_length.setRange(0, 999)
        
        self.questionnaire_length.valueChanged.connect(
            lambda value: self.project_model.update_general("questionnaire_length", value)
        )
        
        layout.addWidget(self.questionnaire_length, row, 3)
        row += 1
        
        # Connect platform radio buttons to model
        self.platform_button_group.buttonClicked.connect(self.platform_changed)

        return group_box
    
    def handle_data_processing_checkbox(self, is_checked: bool):
        self.project_model.update_general("data_processing", is_checked)

        self.data_processing_method.set_enabled(is_checked)

        if not is_checked:
            self.project_model.update_general("data_processing_method", [])

    def handle_coding_checkbox(self, is_check: bool):
        self.project_model.update_general("coding", is_check)

        self.open_ended_main_count.setEnabled(bool("Main" in self.project_model.general["sample_types"]))
        self.open_ended_booster_count.setEnabled(bool("Boosters" in self.project_model.general["sample_types"]))

        if not is_check:
            self.project_model.update_general("open_ended_main_count", 0)
            self.project_model.update_general("open_ended_booster_count", 0)
    
    def handle_device_type_changed(self, text: str):
        self.project_model.update_general("device_type", text)

        is_enabled = text == "Tablet < 9 inch"
        self.tablet_usage_duration.setEnabled(is_enabled)

        if not is_enabled:
            self.project_model.update_general("tablet_usage_duration", "")

    def handle_clt_respondent_visits_changed(self, value):
        self.project_model.update_general("clt_respondent_visits", value)

        is_enabled = value == 0

        if not is_enabled:
            self.project_model.update_general("clt_failure_rate", 0)

    def create_region_dp(self):
        group_box = QGroupBox("Scripting - Data Processing")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch
        
        ### Row 1 - Cell 0
        layout.addWidget(QLabel("Choose the relevant tasks for this project"), 0, 0, 1, 3)

        ### Row 2 - Cell 0
        self.relevant_task_container = QWidget()

        relevant_task_layout = QHBoxLayout(self.relevant_task_container)
        relevant_task_layout.setContentsMargins(20, 5, 0, 5)
        
        self.scripting_checkbox = QCheckBox("Scripting")

        self.scripting_checkbox.stateChanged.connect(
            lambda state: self.project_model.update_general("scripting", bool(state)) 
        )

        self.data_processing_checkbox = QCheckBox("Data Processing")

        self.data_processing_checkbox.stateChanged.connect(
            lambda state: self.handle_data_processing_checkbox(bool(state))
        )
        
        self.coding_checkbox = QCheckBox("Coding")

        self.coding_checkbox.stateChanged.connect(
            lambda state: self.handle_coding_checkbox(bool(state))
        )   

        relevant_task_layout.addWidget(self.scripting_checkbox)
        relevant_task_layout.addWidget(self.data_processing_checkbox)
        relevant_task_layout.addWidget(self.coding_checkbox)

        layout.addWidget(self.relevant_task_container, 2, 0)
        
        ### Row 3 - Cell 0
        self.open_ended_main_count = QSpinBox()
        self.open_ended_main_count.setRange(0, 999)
        
        self.open_ended_main_count.valueChanged.connect(
            lambda value: self.project_model.update_general("open_ended_main_count", value)
        )

        self.create_spinbox(layout, "open_ended_main_count", "Open-ended Questions (Main):", self.open_ended_main_count, row=3, col=0)

        ### Row 3 - Cell 1
        self.open_ended_booster_count = QSpinBox()
        self.open_ended_booster_count.setRange(0, 999)
        
        self.open_ended_booster_count.valueChanged.connect(
            lambda value: self.project_model.update_general("open_ended_booster_count", value)
        )

        self.create_spinbox(layout, "open_ended_main_count", "Open-ended Questions (Booster):", self.open_ended_booster_count, row=3, col=2)

        ### Data Processing
        data_processing_method_label = QLabel("Data Processing Method:")
        data_processing_method_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(data_processing_method_label, 4, 0)

        self.data_processing_method = MultiSelectWidget(DATA_PROCESSING_METHOD, allow_adding=True)
        
        self.data_processing_method.selectionChanged.connect(
            lambda items: self.project_model.update_general("data_processing_method", items)
            
        )
        
        layout.addWidget(self.data_processing_method, 4, 1, 1, 3)

        return group_box

    def create_region_subcontract(self):
        group_box = QGroupBox("Sub-Contracting")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch
        
        subcontracts_label = QLabel("Subcontracts:")
        subcontracts_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(subcontracts_label, 4, 0)

        self.subcontracts = GenericEditorWidget(
            title="Subcontracts",
            field_config = [
                { "name": "subcontractor", "label": "Subcontractor", "widget": QComboBox, "options" : SUBCONTRACTORS, "retuired": True },
                { "name": "cost_type", "label": "Cost Type", "widget": QComboBox, "options": COST_TYPES, "required": True},
                { "name": "optional_detail", "label": "Optional Detail", "widget": QLineEdit },
                { "name": "unit", "label" : "Unit", "widget" : QSpinBox, "min": 0, "max": 99999999, "required": True },
                { "name" : "currency", "label": "Currency", "widget": QComboBox, "options": CURRENCIES, "required": True },
                { "name": "unit_cost", "label": "Unit Cost", "widget": QSpinBox, "min": 0, "max": 99999999, "required": True } 
            ]
        )
        
        layout.addWidget(self.subcontracts, 4, 1, 1, 3)

        return group_box
    
    def create_region_hut(self):
        """Create the HUT (Home Use Test) region."""
        group_box = QGroupBox("HUT (Home Use Test)")
        layout = QFormLayout(group_box)
        
        # Number of test products
        self.hut_test_products = QSpinBox()
        self.hut_test_products.setRange(0, 999)
        layout.addRow("Number of Test Products:", self.hut_test_products)
        self.hut_test_products.valueChanged.connect(
            lambda value: self.project_model.update_general("hut_test_products", value)
        )
        
        # Product usage duration
        self.hut_usage_duration = QSpinBox()
        self.hut_usage_duration.setRange(0, 365)
        layout.addRow("Product Usage Duration (days):", self.hut_usage_duration)
        self.hut_usage_duration.valueChanged.connect(
            lambda value: self.project_model.update_general("hut_usage_duration", value)
        )
        
        return group_box
        
    def create_region_clt(self):
        """Create the CLT (Central Location Test) region."""
        group_box = QGroupBox("CLT (Central Location Test)")
        layout = QFormLayout(group_box)
        
        # Number of test products
        self.clt_test_products = QSpinBox()
        self.clt_test_products.setRange(0, 999)
        
        self.clt_test_products.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_test_products", value)
        )

        layout.addRow("Number of Test Products:", self.clt_test_products)
        
        # Create a horizontal layout for respondent visits and failure rate
        visits_layout = QHBoxLayout()
        
        # Number of respondent visits
        self.clt_respondent_visits = QSpinBox()
        self.clt_respondent_visits.setRange(1, 3)

        self.clt_respondent_visits.valueChanged.connect(
            lambda value: self.handle_clt_respondent_visits_changed(value)
        )

        visits_layout.addWidget(self.clt_respondent_visits)

        # Add spacing
        visits_layout.addSpacing(20)
        
        # Failure Rate - only enabled when respondent visits > 1
        visits_layout.addWidget(QLabel("Failure Rate:"))
        self.clt_failure_rate = QSpinBox()
        self.clt_failure_rate.setRange(0, 100)
        self.clt_failure_rate.setSuffix("%")
        self.clt_failure_rate.setEnabled(False)  # Initially disabled

        visits_layout.addWidget(self.clt_failure_rate)
        
        visits_layout.addStretch()

        layout.addRow("Number of Respondent Visits:", visits_layout)
        
        # Connect signals for respondent visits and failure rate
        self.clt_respondent_visits.valueChanged.connect(self.update_respondent_visits)

        self.clt_failure_rate.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_failure_rate", value)
        )
        
        # Tablet/Laptop selection
        self.device_type = QComboBox()
        self.device_type.addItem("-- Select --")
        self.device_type.addItems(DEVIVE_TYPES)

        # Set item đầu tiên là mặc định
        self.device_type.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.device_type.model().item(0).setEnabled(False)

        self.device_type.currentTextChanged.connect(
            lambda text: (
                self.handle_device_type_changed(text)
            )
        )
        
        layout.addRow("Thuê tablet / laptop:", self.device_type)
        # self.clt_device_type.currentTextChanged.connect(self.update_device_type)

        # Tablet usage duration - only shown when "Tablet < 9 inch" is selected
        self.tablet_usage_duration = QComboBox()
        self.tablet_usage_duration.addItem("-- Select --")
        self.tablet_usage_duration.addItems(TABLET_USAGE_DURATIONS)

        # Set item đầu tiên là mặc định
        self.tablet_usage_duration.setCurrentIndex(0)

        # Set item đầu tiên là không thể chọn
        self.tablet_usage_duration.model().item(0).setEnabled(False)

        self.tablet_usage_duration.currentTextChanged.connect(
            lambda text: (
                self.handle_combobox_changed("tablet_usage_duration", text)
            )
        )

        layout.addRow("Thời gian sử dụng tablet:", self.tablet_usage_duration)
        
        # Sample Recruit IDI
        self.clt_sample_recruit_idi = QSpinBox()
        self.clt_sample_recruit_idi.setRange(0, 10000)
        layout.addRow("Sample Recruit IDI:", self.clt_sample_recruit_idi)
        self.clt_sample_recruit_idi.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_sample_recruit_idi", value)
        )
        
        # Assistant Set Up Days - NEW FIELD
        self.clt_assistant_setup_days = QSpinBox()
        self.clt_assistant_setup_days.setRange(1, 30)
        self.clt_assistant_setup_days.setValue(1)  # Default value
        self.clt_assistant_setup_days.setSuffix(" day(s)")
        layout.addRow("Assistant set up needs:", self.clt_assistant_setup_days)
        self.clt_assistant_setup_days.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_assistant_setup_days", value)
        )
        
        # Dán mẫu checkbox and Số ngày dán mẫu spinbox
        dan_mau_layout = QHBoxLayout()
        self.clt_dan_mau = QCheckBox("Dán mẫu")
        dan_mau_layout.addWidget(self.clt_dan_mau)
        
        dan_mau_layout.addSpacing(10)
        dan_mau_layout.addWidget(QLabel("Số ngày dán mẫu:"))
        self.clt_dan_mau_days = QSpinBox()
        self.clt_dan_mau_days.setRange(0, 100)
        self.clt_dan_mau_days.setEnabled(False)  # Initially disabled
        dan_mau_layout.addWidget(self.clt_dan_mau_days)
        dan_mau_layout.addStretch()
        
        layout.addRow("", dan_mau_layout)
        
        # Connect signals for Dán mẫu related widgets
        self.clt_dan_mau.stateChanged.connect(self.update_dan_mau)
        self.clt_dan_mau_days.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_dan_mau_days", value)
        )
        
        # Sample size target per day
        self.clt_sample_size_per_day = QSpinBox()
        self.clt_sample_size_per_day.setRange(0, 999)
        layout.addRow("Sample Size Target per Day:", self.clt_sample_size_per_day)
        self.clt_sample_size_per_day.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_sample_size_per_day", value)
        )

        # Number of desk-based interviewers (NGỒI BÀN)
        self.clt_desk_interviewers_count = QSpinBox()
        self.clt_desk_interviewers_count.setRange(0, 999)
        layout.addRow("Số lượng PVV tham gia dự án (NGỒI BÀN):", self.clt_desk_interviewers_count)
        self.clt_desk_interviewers_count.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_desk_interviewers_count", value)
        )

        # Number of provincial desk-based interviewers
        self.clt_provincial_desk_interviewers_count = QSpinBox()
        self.clt_provincial_desk_interviewers_count.setRange(0, 999)
        layout.addRow("Số lượng PVV đi tỉnh (NGỒI BÀN):", self.clt_provincial_desk_interviewers_count)
        self.clt_provincial_desk_interviewers_count.valueChanged.connect(
            lambda value: self.project_model.update_general("clt_provincial_desk_interviewers_count", value)
        )

        return group_box
        
    def create_region_printer(self):
        """Create the Printer region."""
        group_box = QGroupBox("Printer")
        layout = QFormLayout(group_box)
        
        # BACKWHITE page count
        self.bw_page_count = QSpinBox()
        self.bw_page_count.setRange(0, 9999)
        layout.addRow("Số trang photo trắng đen:", self.bw_page_count)
        self.bw_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("bw_page_count", value)
        )
        
        # SHOWPHOTO page count
        self.showphoto_page_count = QSpinBox()
        self.showphoto_page_count.setRange(0, 9999)
        layout.addRow("Số trang shop photo:", self.showphoto_page_count)
        self.showphoto_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("showphoto_page_count", value)
        )
        
        # SHOWCARD page count
        self.showcard_page_count = QSpinBox()
        self.showcard_page_count.setRange(0, 9999)
        layout.addRow("Số trang showcard:", self.showcard_page_count)
        self.showcard_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("showcard_page_count", value)
        )
        
        # DROPCARD page count
        self.dropcard_page_count = QSpinBox()
        self.dropcard_page_count.setRange(0, 9999)
        layout.addRow("Số trang dropcard:", self.dropcard_page_count)
        self.dropcard_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("dropcard_page_count", value)
        )
        
        # COLOR page count
        self.color_page_count = QSpinBox()
        self.color_page_count.setRange(0, 9999)
        layout.addRow("Số trang in màu:", self.color_page_count)
        self.color_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("color_page_count", value)
        )
        
        # DECAL page count
        self.decal_page_count = QSpinBox()
        self.decal_page_count.setRange(0, 9999)
        layout.addRow("Số decal dán mẫu:", self.decal_page_count)
        self.decal_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("decal_page_count", value)
        )
        
        # Laminated page count
        self.laminated_page_count = QSpinBox()
        self.laminated_page_count.setRange(0, 9999)
        layout.addRow("Số trang ép plastic:", self.laminated_page_count)
        self.laminated_page_count.valueChanged.connect(
            lambda value: self.project_model.update_general("laminated_page_count", value)
        )
        
        return group_box

    def update_respondent_visits(self, value):
        """Update failure rate field based on respondent visits value."""
        self.project_model.update_general("clt_respondent_visits", value)
        self.clt_failure_rate.setEnabled(value > 1)
        
    def update_dan_mau(self, state):
        """Update Số ngày dán mẫu field based on Dán mẫu checkbox state."""
        is_checked = bool(state)  # Any non-zero state means it's checked
        self.project_model.update_general("clt_dan_mau", is_checked)
        self.clt_dan_mau_days.setEnabled(is_checked)
        
    def service_line_changed(self, service_line):
        """Handle service line change and update available industries."""
        self.project_model.update_general("service_line", service_line)
        
        # Update available industries based on service line
        if service_line in INDUSTRIES_BY_SERVICE_LINE:
            industries_list = INDUSTRIES_BY_SERVICE_LINE[service_line]
            self.industries.set_items(industries_list)
        else:
            self.industries.set_items([])

    def platform_changed(self, button):
        """
        Handle platform radio button change.
        
        Args:
            button (QRadioButton): The selected radio button
        """
        if button == self.ifield_radio:
            self.project_model.update_general("platform", "iField")
        else:  # dimension_radio
            self.project_model.update_general("platform", "Dimension")

    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Project Information
        self.internal_job.blockSignals(True)
        self.internal_job.setText(self.project_model.general["internal_job"])
        self.internal_job.blockSignals(False)

        self.symphony.blockSignals(True)
        self.symphony.setText(self.project_model.general["symphony"])
        self.symphony.blockSignals(False)

        self.project_name.blockSignals(True)
        self.project_name.setText(self.project_model.general["project_name"])
        self.project_name.blockSignals(False)

        # Project Type
        value = self.project_model.general["project_type"]

        self.project_type.blockSignals(True)

        if value and value in PROJECT_TYPES:
            self.project_type.setCurrentText(value)
        else:
            self.project_type.setCurrentIndex(0) #--Select--
        self.project_type.blockSignals(False)  
        
        # Clients
        self.clients.set_selected_items(self.project_model.general["clients"])
        
        # Project Objectives
        self.project_objectives_line_input.blockSignals(True)
        
        cursor = self.project_objectives_line_input.textCursor()
        pos = cursor.position()

        self.project_objectives_line_input.setPlainText(self.project_model.general["project_objectives"])

        cursor.setPosition(min(pos, len(self.project_model.general["project_objectives"])))
        self.project_objectives_line_input.setTextCursor(cursor)

        self.project_objectives_line_input.blockSignals(False)

        # Platform Details
        platform = self.project_model.general.get("platform", "iField")

        if platform == "iField":
            self.ifield_radio.setChecked(True)
        else:  # Dimension
            self.dimension_radio.setChecked(True)

        # Quota & Sampling
        self.interview_methods.set_selected_items(self.project_model.general["interview_methods"])

        # Sampling Method
        value = self.project_model.general["sampling_method"]
        
        self.sampling_method.blockSignals(True)

        if value and value in SAMPLING_METHODS:
            self.sampling_method.setCurrentText(value)
        else:
            self.sampling_method.setCurrentIndex(0)
        self.sampling_method.blockSignals(False)
        
        self.recruit_method.set_selected_items(self.project_model.general["recruit_method"])

        # Type of Quota Control
        value = self.project_model.general["type_of_quota_control"]
        
        self.type_of_quota_control.blockSignals(True)

        if value and value in TYPE_OF_QUOTA_CONTROLS:
            self.type_of_quota_control.setCurrentText(value)
        else:
            self.type_of_quota_control.setCurrentIndex(0)

        self.type_of_quota_control.blockSignals(False)

        self.quota_description.set_enabled(self.project_model.general["type_of_quota_control"] == "Interlocked Quota")
        self.quota_description.set_selected_items(self.project_model.general["quota_description"])
        self.quota_description_warning.setVisible(False)

        # Service Line
        value = self.project_model.general["service_line"]
        
        self.service_line.blockSignals(True)

        if value and value in SERVICE_LINES:
            self.service_line.setCurrentText(value)
        else:
            self.service_line.setCurrentIndex(0)
        self.service_line.blockSignals(False)

        self.provinces.set_enabled(bool(self.project_model.general["service_line"]))
        self.provinces.set_selected_items(self.project_model.general["provinces"])

        self.sample_types.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"])
        )            
        self.sample_types.set_selected_items(self.project_model.general["sample_types"])

        self.industries.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"]) and 
            bool(self.project_model.general["sample_types"])
        )
        self.industries.set_selected_items(self.project_model.general["industries"])

        self.target_audiences.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"]) and 
            bool(self.project_model.general["sample_types"]) and
            bool(self.project_model.general["industries"])
        )

        self.target_audiences.set_selected_sample_types(self.project_model.general["sample_types"])
        self.target_audiences.set_selected_industries(self.project_model.general["industries"])
        self.target_audiences.set_selected_audiences(self.project_model.general["target_audiences"])

        self.interview_length.setValue(self.project_model.general["interview_length"])
        self.questionnaire_length.setValue(self.project_model.general["questionnaire_length"])
        
        # Scripting & Data Processing
        
        self.scripting_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["scripting"] else Qt.CheckState.Unchecked)
        self.data_processing_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["data_processing"] else Qt.CheckState.Unchecked)
        self.coding_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["coding"] else Qt.CheckState.Unchecked)

        is_check = self.project_model.general["coding"] and "Main" in self.project_model.general["sample_types"]
        self.open_ended_main_count.setEnabled(is_check)
        self.open_ended_main_count.setValue(self.project_model.general["open_ended_main_count"])

        is_check = self.project_model.general["coding"] and "Boosters" in self.project_model.general["sample_types"]
        self.open_ended_booster_count.setEnabled(is_check)
        self.open_ended_booster_count.setValue(self.project_model.general["open_ended_booster_count"])
        
        self.data_processing_method.set_enabled(bool(self.project_model.general["data_processing"]))
        self.data_processing_method.set_selected_items(self.project_model.general["data_processing_method"])
        
        # Update HUT
        if "HUT" in self.project_model.general["project_type"]:
            self.hut_test_products.setValue(self.project_model.general["hut_test_products"])
            self.hut_usage_duration.setValue(self.project_model.general["hut_usage_duration"])
        
        # Update CLT
        self.clt_test_products.setValue(self.project_model.general["clt_test_products"])
        self.clt_respondent_visits.setValue(self.project_model.general["clt_respondent_visits"])
        self.clt_failure_rate.setValue(self.project_model.general.get("clt_failure_rate", 0))

        self.project_model.set_selected_failure_rate_costs(self.project_model.general.get("clt_failure_rate", 0) != 0)

        self.clt_sample_size_per_day.setValue(self.project_model.general["clt_sample_size_per_day"])
        self.clt_desk_interviewers_count.setValue(self.project_model.general["clt_desk_interviewers_count"])
        self.clt_provincial_desk_interviewers_count.setValue(self.project_model.general["clt_provincial_desk_interviewers_count"])
        self.clt_assistant_setup_days.setValue(self.project_model.general.get("clt_assistant_setup_days", 1))
        

        value = self.project_model.general["device_type"]
        
        self.device_type.blockSignals(True)

        if value and value in DEVIVE_TYPES:
            self.device_type.setCurrentText(value)
        else:
            self.device_type.setCurrentIndex(0)

        self.project_model.set_selected_device_cost(value)

        self.device_type.blockSignals(False)
        
        value = self.project_model.general["tablet_usage_duration"]

        self.tablet_usage_duration.blockSignals(True)

        if value and value in TABLET_USAGE_DURATIONS:
            self.tablet_usage_duration.setCurrentText(value)
        else:
            self.tablet_usage_duration.setCurrentIndex(0)

        self.tablet_usage_duration.blockSignals(False)

        self.clt_sample_recruit_idi.setValue(self.project_model.general.get("clt_sample_recruit_idi", 0))
        self.clt_dan_mau.setChecked(self.project_model.general.get("clt_dan_mau", False))
        self.clt_dan_mau_days.setValue(self.project_model.general.get("clt_dan_mau_days", 0))
        self.clt_dan_mau_days.setEnabled(self.project_model.general.get("clt_dan_mau", False))

        self.clt_sample_size_per_day.setValue(self.project_model.general["clt_sample_size_per_day"])

        # Update Printer
        self.bw_page_count.setValue(self.project_model.general["bw_page_count"])
        self.showphoto_page_count.setValue(self.project_model.general["showphoto_page_count"])
        self.showcard_page_count.setValue(self.project_model.general["showcard_page_count"])
        self.dropcard_page_count.setValue(self.project_model.general["dropcard_page_count"])
        self.color_page_count.setValue(self.project_model.general["color_page_count"])
        self.decal_page_count.setValue(self.project_model.general["decal_page_count"])
        self.laminated_page_count.setValue(self.project_model.general["laminated_page_count"])

        self.update_region_visibility()

        