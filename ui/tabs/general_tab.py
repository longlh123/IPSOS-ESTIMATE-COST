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
from PySide6.QtCore import Signal

from models.project_model import ProjectModel
from config.predefined_values import *
from ui.widgets.multi_select import MultiSelectWidget
from ui.widgets.target_audience_widget import TargetAudienceWidget
from ui.widgets.generic_editor_widget import GenericEditorWidget
from components.validation_field import FieldValidator
from ui.events.wheelBlocker import WheelBlocker
from ui.helpers.form_helpers import (create_header_label, create_input_field, create_combobox, create_multiselected_field, create_textedit_field, 
                                     create_radiobuttons_group, create_spinbox_field
                                     )
from ui.helpers.form_events import bind_input_handler, bind_combobox_handler, bind_multiselection_handler, bind_textedit_handler, bind_radiogroup_handler, bind_spinbox_handler

class GeneralTab(QWidget):
    """
    Tab for general project information, divided into four regions.
    """
    
    projectTypeChanged = Signal(str)

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

        self.region_general_information = self.create_region_general_information()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_general_information.findChildren(QSpinBox) + self.region_general_information.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
        
        self.region_dp = self.create_region_dp()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_dp.findChildren(QSpinBox) + self.region_dp.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        self.region_subcontract = self.create_region_subcontract()

        self.region_printer = self.create_region_printer()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_printer.findChildren(QSpinBox) + self.region_printer.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)
        
        self.region_clt = self.create_region_clt()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_clt.findChildren(QSpinBox) + self.region_clt.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        self.region_hut = self.create_region_hut()
        
        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in self.region_hut.findChildren(QSpinBox) + self.region_hut.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        # Add regions to layout
        scroll_layout.addWidget(self.region_general_information)
        scroll_layout.addWidget(self.region_clt)
        scroll_layout.addWidget(self.region_hut)
        scroll_layout.addWidget(self.region_dp)
        scroll_layout.addWidget(self.region_printer)
        
        scroll_layout.addStretch()
        
        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # After setting up all UI elements, explicitly trigger updates for comboboxes
        # This ensures initial values are saved to the model
        if self.project_type_combobox.currentText():
            self.project_model.update_general("project_type", self.project_type_combobox.currentText())
        
        if self.sampling_method_combobox.currentText():
            self.project_model.update_general("sampling_method", self.sampling_method_combobox.currentText())
        
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

    def on_project_type_changed(self, value: str):
        self.projectTypeChanged.emit(value)

    def create_region_general_information(self):
        """Create the General Information region."""
        group_box = QGroupBox("General Information")

        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch
        
        create_header_label(layout, "Project Information", row=0, col=0, rowspan=1, colspan=4)
        
        ### Internal Job
        create_input_field(layout, self, "internal_job", "Internal Job:", row=1, col=0)

        bind_input_handler(self, "internal_job", validator=self.validator, update_func=self.project_model.update_general)
        
        ### Symphony 
        create_input_field(layout, self, "symphony", "Symphony:", row=1, col=2)

        bind_input_handler(self, "symphony", validator=self.validator, update_func=self.project_model.update_general)

        ### Project Name
        create_input_field(layout, self, "project_name", "Project Name:", row=2, col=0)

        bind_input_handler(self, "project_name", validator=self.validator, update_func=self.project_model.update_general)
        
        ### Project Type
        create_combobox(layout, self, "project_type", "Project Type:", PROJECT_TYPES, row=2, col=2)

        bind_combobox_handler(self, "project_type", validator=self.validator, update_func=self.project_model.update_general)

        self.project_type_combobox.currentTextChanged.connect(self.on_project_type_changed)
        
        ### Clients
        create_multiselected_field(layout, self, "clients", "Clients:", CLIENTS, allow_adding=True, row=3, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "clients", validator=self.validator, update_func=self.project_model.update_general)
        
        ### Project Objectives
        create_textedit_field(layout, self, "project_objectives", "Project Objectives:", placeholder="Enter your text here...", row=4, col=0, rowspan=1, colspan=4)
        
        bind_textedit_handler(self, "project_objectives", validator=self.validator, update_func=self.project_model.update_general)

        ### Platform Details Group
        create_header_label(layout, "Platform Details", row=6, col=0, rowspan=1, colspan=4)

        ### Platform
        radio_items = [
            { 'name': 'ifield', 'label': 'iField'},
            { 'name': 'dimension', 'label': 'Dimension'}
        ]
        create_radiobuttons_group(layout, self, "platform", "Platform:", radio_items=radio_items, row=7, col=0, rowspan=1, colspan=3, margins={"left": 0, "top": 5, "right": 0, "bottom": 5})

        bind_radiogroup_handler(self, "platform", update_func=self.project_model.update_general)

        ### Quota & Sampling Group
        create_header_label(layout, "Quota & Sampling", row=8, col=0, rowspan=1, colspan=4)

        ### Interview Methods
        create_multiselected_field(layout, self, "interview_methods", "Interview Methods:", INTERVIEW_METHODS, allow_adding=False, row=9, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "interview_methods", validator=self.validator, update_func=self.project_model.update_general)

        ### Sampling Method
        create_combobox(layout, self, "sampling_method", "Sampling Method:", SAMPLING_METHODS, row=10, col=0)

        bind_combobox_handler(self, "sampling_method", validator=self.validator, update_func=self.project_model.update_general)

        ### Recruit Method
        create_multiselected_field(layout, self, "recruit_method", "Recruit Method:", RECRUIT_METHOD, allow_adding=False, row=10, col=2)

        bind_multiselection_handler(self, "recruit_method", validator=self.validator, update_func=self.project_model.update_general)
        
        ### Type of Quota Controls
        create_combobox(layout, self, "type_of_quota_control", "Type of Quota Control:", TYPE_OF_QUOTA_CONTROLS, row=11, col=0)

        bind_combobox_handler(self, "type_of_quota_control", validator=self.validator, update_func=self.project_model.update_general)

        ### Quota Description
        create_multiselected_field(layout, self, "quota_description", "Quota Description:", QUOTA_DESCRIPTION, allow_adding=False, row=11, col=2)

        bind_multiselection_handler(self, "quota_description", validator=self.validator, update_func=self.project_model.update_general)
        
        ### "Target Audience Group" 
        create_header_label(layout, "Target Audience", row=12, col=0, rowspan=1, colspan=4)

        ### Service Lines
        create_combobox(layout, self, "service_line", "Service Line:", SERVICE_LINES, row=13, col=0)

        bind_combobox_handler(self, "service_line", validator=self.validator, update_func=self.project_model.update_general)

        ### Provinces
        create_multiselected_field(layout, self, "provinces", "Provinces:", VIETNAM_PROVINCES, allow_adding=False, row=14, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "provinces", validator=self.validator, update_func=self.project_model.update_general)

        ### Sample Types
        create_multiselected_field(layout, self, "sample_types", "Sample Types:", SAMPLE_TYPES, allow_adding=False, row=15, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "sample_types", validator=self.validator, update_func=self.project_model.update_general)
        
        ### Industries
        create_multiselected_field(layout, self, "industries", "Industries:", list(self.project_model.industries_data), allow_adding=False, row=16, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "industries", validator=self.validator, update_func=self.project_model.update_general)

        ### Target Audience
        target_audience_label = QLabel("Target Audiences:")
        target_audience_label.setStyleSheet("margin-left: 10px;")

        layout.addWidget(target_audience_label, 17, 0)

        self.target_audiences = TargetAudienceWidget(self.project_model.industries_data)

        self.target_audiences.selectionChanged.connect(
            lambda items: (
                # Cập nhật model
                self.project_model.update_general("target_audiences", items)
            )
        )

        layout.addWidget(self.target_audiences, 17, 1, 1, 3)

        ### Timing & Description Group
        create_header_label(layout, "Timing & Description", row=18, col=0, rowspan=1, colspan=4)

        ### Length of Interview
        create_spinbox_field(layout, self, "interview_length", "Length of Interview", range=(0, 999), suffix=" (minutes)", row=19, col=0)
        
        bind_spinbox_handler(self, "interview_length", validator=self.validator, update_func=self.project_model.update_general)

        ### Length of Questionnaire
        create_spinbox_field(layout, self, "questionnaire_length", "Length of Questionnaire", range=(0, 999), suffix=" (pages)", row=19, col=2)

        bind_spinbox_handler(self, "questionnaire_length", validator=self.validator, update_func=self.project_model.update_general)

        return group_box
    
    def handle_data_processing_checkbox(self, is_checked: bool):
        self.project_model.update_general("data_processing", is_checked)

        self.data_processing_method.set_enabled(is_checked)

        if not is_checked:
            self.project_model.update_general("data_processing_method", [])

    def handle_coding_checkbox(self, is_check: bool):
        self.project_model.update_general("coding", is_check)

        self.open_ended_main_count.setEnabled(bool("Main" in self.project_model.general["sample_types"]))
        self.open_ended_booster_count.setEnabled(bool("Booster" in self.project_model.general["sample_types"]))

        if not is_check:
            self.project_model.update_general("open_ended_main_count", 0)
            self.project_model.update_general("open_ended_booster_count", 0)
    
    def handle_device_type_changed(self, text: str):
        self.project_model.update_general("device_type", text)

        is_enabled = text == "Tablet < 9 inch"
        self.tablet_usage_duration.setEnabled(is_enabled)

        if not is_enabled:
            self.project_model.update_general("tablet_usage_duration", "")

    def create_region_dp(self):
        group_box = QGroupBox("Scripting - Data Processing")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)  # Make the second column stretch
        layout.setColumnStretch(3, 1)  # Make the fourth column stretch
        
        create_header_label(layout, "Choose the relevant tasks for this project", row=0, col=0, rowspan=1, colspan=4)

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
        
        ### Open-ended Questions (Main)
        create_spinbox_field(layout, self, "open_ended_main_count", "Open-ended Questions (Main):", range=(0, 999), suffix=" (questions)", row=3, col=0)
        
        bind_spinbox_handler(self, "open_ended_main_count", validator=self.validator, update_func=self.project_model.update_general)

        ### Open-ended Questions (Booster)
        create_spinbox_field(layout, self, "open_ended_booster_count", "Open-ended Questions (Booster):", range=(0, 999), suffix=" (questions)", row=3, col=2)
        
        bind_spinbox_handler(self, "open_ended_booster_count", validator=self.validator, update_func=self.project_model.update_general)

        ### Data Processing
        create_multiselected_field(layout, self, "data_processing_method", "Data Processing Method:", DATA_PROCESSING_METHOD, allow_adding=True, row=4, col=0, rowspan=1, colspan=3)

        bind_multiselection_handler(self, "data_processing_method", validator=self.validator, update_func=self.project_model.update_general)

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
            lambda value: self.project_model.update_hut_settings("hut_test_products", value)
        )
        
        # Product usage duration
        self.hut_usage_duration = QSpinBox()
        self.hut_usage_duration.setRange(0, 365)
        layout.addRow("Product Usage Duration (days):", self.hut_usage_duration)
        self.hut_usage_duration.valueChanged.connect(
            lambda value: self.project_model.update_hut_settings("hut_usage_duration", value)
        )
        
        return group_box

    def create_region_clt(self):
        """Create the CLT (Central Location Test) region."""
        group_box = QGroupBox("CLT (Central Location Test)")
        
        layout = QGridLayout(group_box)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        create_header_label(layout, "CLT Settings", row=0, col=0, rowspan=1, colspan=4)

        # Number of test products
        create_spinbox_field(layout, self, "clt_test_products", "Number of Test Products:", range=(0, 999), suffix="", row=1, col=0)

        bind_spinbox_handler(self, "clt_test_products", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Number of respondent visits
        create_spinbox_field(layout, self, "clt_respondent_visits", "Number of Respondent Visits:", range=(0, 999), suffix="", row=2, col=0)

        bind_spinbox_handler(self, "clt_respondent_visits", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Failure Rate
        create_spinbox_field(layout, self, "clt_failure_rate", "Failure Rate:", range=(0, 999), suffix="%", row=3, col=0)

        bind_spinbox_handler(self, "clt_failure_rate", validator=self.validator, update_func=self.project_model.update_clt_settings)

        # Sample Recruit IDI
        create_spinbox_field(layout, self, "clt_sample_recruit_idi", "Sample Recruit IDI:", range=(0, 999), suffix="", row=4, col=0)

        bind_spinbox_handler(self, "clt_sample_recruit_idi", validator=self.validator, update_func=self.project_model.update_clt_settings)
        
        create_header_label(layout, "Dán mẫu settings", row=5, col=0, rowspan=1, colspan=4)

        # Dán mẫu
        create_spinbox_field(layout, self, "clt_number_of_samples_to_label", "Number of samples to label:", range=(0, 999), suffix="", row=6, col=0)

        bind_spinbox_handler(self, "clt_number_of_samples_to_label", validator=self.validator, update_func=self.project_model.update_clt_settings)

        ### Description of label application method
        create_textedit_field(layout, self, "clt_description_howtolabelthesample", "Description of how to label the sample:", placeholder="Enter your text here...", row=7, col=0, rowspan=1, colspan=4)
        
        bind_textedit_handler(self, "clt_description_howtolabelthesample", validator=self.validator, update_func=self.project_model.update_general)

        # # Assistant Set Up Days - NEW FIELD
        # self.clt_assistant_setup_days = QSpinBox()
        # self.clt_assistant_setup_days.setRange(1, 30)
        # self.clt_assistant_setup_days.setValue(1)  # Default value
        # self.clt_assistant_setup_days.setSuffix(" day(s)")
        
        # self.clt_assistant_setup_days.valueChanged.connect(
        #     lambda value: self.handle_spinbox_changed("clt_assistant_setup_days", value)
        # )

        # self.create_spinbox(layout, "clt_assistant_setup_days", "Assistant set up needs:", self.clt_assistant_setup_days, 5, 0)

        # #--Số ngày dán mẫu
        # self.clt_dan_mau_days = QSpinBox()
        # self.clt_dan_mau_days.setRange(0, 100)

        # self.clt_dan_mau_days.valueChanged.connect(
        #     lambda value: self.handle_spinbox_changed("clt_dan_mau_days", value)
        # )

        # self.create_spinbox(layout, "clt_dan_mau_days", "Số ngày dán mẫu:", self.clt_dan_mau_days, 9, 0)
        
        # layout.addWidget(self.create_group_header("Daily Targets & Staffing"), 10, 0, 1, 4) 

        # # Sample size target per day
        # self.clt_sample_size_per_day = QSpinBox()
        # self.clt_sample_size_per_day.setRange(0, 999)

        # self.clt_sample_size_per_day.valueChanged.connect(
        #     lambda value: self.handle_spinbox_changed("clt_sample_size_per_day", value)
        # )

        # self.create_spinbox(layout, "clt_sample_size_per_day", "Sample Size Target per Day:", self.clt_sample_size_per_day, 11, 0)

        # # Number of desk-based interviewers (NGỒI BÀN)
        # self.clt_desk_interviewers_count = QSpinBox()
        # self.clt_desk_interviewers_count.setRange(0, 999)
        
        # self.clt_desk_interviewers_count.valueChanged.connect(
        #     lambda value: self.handle_spinbox_changed("clt_desk_interviewers_count", value)
        # )

        # self.create_spinbox(layout, "clt_desk_interviewers_count", "Số lượng PVV tham gia dự án (NGỒI BÀN):", self.clt_desk_interviewers_count, 12, 0)

        # # Number of provincial desk-based interviewers
        # self.clt_provincial_desk_interviewers_count = QSpinBox()
        # self.clt_provincial_desk_interviewers_count.setRange(0, 999)
        
        # self.clt_provincial_desk_interviewers_count.valueChanged.connect(
        #     lambda value: self.handle_spinbox_changed("clt_provincial_desk_interviewers_count", value)
        # )

        # self.create_spinbox(layout, "clt_provincial_desk_interviewers_count", "Số lượng PVV đi tỉnh (NGỒI BÀN):", self.clt_provincial_desk_interviewers_count, 13, 0)

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
        
    def service_line_changed(self, service_line):
        """Handle service line change and update available industries."""
        self.project_model.update_general("service_line", service_line)
        
        # Update available industries based on service line
        if service_line in INDUSTRIES_BY_SERVICE_LINE:
            industries_list = INDUSTRIES_BY_SERVICE_LINE[service_line]
            self.industries.set_items(industries_list)
        else:
            self.industries.set_items([])

    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Project Information
        self.internal_job_input.blockSignals(True)
        self.internal_job_input.setText(self.project_model.general["internal_job"])
        self.internal_job_input.blockSignals(False)

        self.symphony_input.blockSignals(True)
        self.symphony_input.setText(self.project_model.general["symphony"])
        self.symphony_input.blockSignals(False)

        self.project_name_input.blockSignals(True)
        self.project_name_input.setText(self.project_model.general["project_name"])
        self.project_name_input.blockSignals(False)

        # Project Type
        value = self.project_model.general["project_type"]

        self.project_type_combobox.blockSignals(True)

        if value and value in PROJECT_TYPES:
            self.project_type_combobox.setCurrentText(value)
        else:
            self.project_type_combobox.setCurrentIndex(0) #--Select--
        self.project_type_combobox.blockSignals(False)  

        self.project_model.qc_communication_costs("CLT" in value)
        
        # Clients
        self.clients_multiselecttion.set_selected_items(self.project_model.general["clients"])
        
        # Project Objectives
        self.project_objectives_textedit.blockSignals(True)
        
        cursor = self.project_objectives_textedit.textCursor()
        pos = cursor.position()

        self.project_objectives_textedit.setPlainText(self.project_model.general["project_objectives"])

        cursor.setPosition(min(pos, len(self.project_model.general["project_objectives"])))
        self.project_objectives_textedit.setTextCursor(cursor)

        self.project_objectives_textedit.blockSignals(False)

        # Platform Details
        platform = self.project_model.general.get("platform", "iField")

        if platform == "iField":
            self.ifield_radioitem.setChecked(True)
        else:  # Dimension
            self.dimension_radioitem.setChecked(True)

        # Quota & Sampling
        self.interview_methods_multiselecttion.set_selected_items(self.project_model.general["interview_methods"])

        # Sampling Method
        value = self.project_model.general["sampling_method"]
        
        self.sampling_method_combobox.blockSignals(True)

        if value and value in SAMPLING_METHODS:
            self.sampling_method_combobox.setCurrentText(value)
        else:
            self.sampling_method_combobox.setCurrentIndex(0)
        self.sampling_method_combobox.blockSignals(False)
        
        self.recruit_method_multiselecttion.set_selected_items(self.project_model.general["recruit_method"])

        # Type of Quota Control
        value = self.project_model.general["type_of_quota_control"]
        
        self.type_of_quota_control_combobox.blockSignals(True)

        if value and value in TYPE_OF_QUOTA_CONTROLS:
            self.type_of_quota_control_combobox.setCurrentText(value)
        else:
            self.type_of_quota_control_combobox.setCurrentIndex(0)

        self.type_of_quota_control_combobox.blockSignals(False)

        self.quota_description_multiselecttion.set_enabled(self.project_model.general["type_of_quota_control"] == "Interlocked Quota")
        self.quota_description_multiselecttion.set_selected_items(self.project_model.general["quota_description"])
        
        # Service Line
        value = self.project_model.general["service_line"]
        
        self.service_line_combobox.blockSignals(True)

        if value and value in SERVICE_LINES:
            self.service_line_combobox.setCurrentText(value)
        else:
            self.service_line_combobox.setCurrentIndex(0)
        self.service_line_combobox.blockSignals(False)

        self.provinces_multiselecttion.set_enabled(bool(self.project_model.general["service_line"]))
        self.provinces_multiselecttion.set_selected_items(self.project_model.general["provinces"])

        self.sample_types_multiselecttion.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"])
        )            
        self.sample_types_multiselecttion.set_selected_items(self.project_model.general["sample_types"])

        self.industries_multiselecttion.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"]) and 
            bool(self.project_model.general["sample_types"])
        )
        self.industries_multiselecttion.set_selected_items(self.project_model.general["industries"])

        self.target_audiences.set_enabled(
            bool(self.project_model.general["service_line"]) and 
            bool(self.project_model.general["provinces"]) and 
            bool(self.project_model.general["sample_types"]) and
            bool(self.project_model.general["industries"])
        )

        self.target_audiences.set_selected_sample_types(self.project_model.general["sample_types"])
        self.target_audiences.set_selected_industries(self.project_model.general["industries"])
        self.target_audiences.set_selected_audiences(self.project_model.general["target_audiences"])

        self.interview_length_spinbox.setValue(self.project_model.general["interview_length"])
        self.questionnaire_length_spinbox.setValue(self.project_model.general["questionnaire_length"])
        
        # Scripting & Data Processing
        
        self.scripting_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["scripting"] else Qt.CheckState.Unchecked)
        self.data_processing_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["data_processing"] else Qt.CheckState.Unchecked)
        self.coding_checkbox.setCheckState(Qt.CheckState.Checked if self.project_model.general["coding"] else Qt.CheckState.Unchecked)

        self.open_ended_main_count_spinbox.blockSignals(True)
        self.open_ended_booster_count_spinbox.blockSignals(True)

        is_check = self.project_model.general["coding"] and "Main" in self.project_model.general["sample_types"]
        self.open_ended_main_count_spinbox.setEnabled(is_check)
        self.open_ended_main_count_spinbox.setValue(self.project_model.general["open_ended_main_count"])

        is_check = self.project_model.general["coding"] and "Booster" in self.project_model.general["sample_types"]
        self.open_ended_booster_count_spinbox.setEnabled(is_check)
        self.open_ended_booster_count_spinbox.setValue(self.project_model.general["open_ended_booster_count"])

        self.project_model.set_selected_dp_costs()
        
        self.open_ended_main_count_spinbox.blockSignals(False)
        self.open_ended_booster_count_spinbox.blockSignals(False)

        self.data_processing_method_multiselecttion.set_enabled(bool(self.project_model.general["data_processing"]))
        self.data_processing_method_multiselecttion.set_selected_items(self.project_model.general["data_processing_method"])
        
        # Update HUT
        if "HUT" not in self.project_type_combobox.currentText():
            self.project_model.hut_settings_clear()

        self.hut_test_products.setValue(self.project_model.hut_settings.get("hut_test_products", 0))
        self.hut_usage_duration.setValue(self.project_model.hut_settings.get("hut_usage_duration", 0))
        
        # Update CLT
        if "CLT" not in self.project_type_combobox.currentText():
            self.project_model.clt_settings_clear()

        self.clt_test_products_spinbox.setValue(self.project_model.clt_settings.get("clt_test_products", 0))
        self.clt_respondent_visits_spinbox.setValue(self.project_model.clt_settings.get("clt_respondent_visits", 0))
        
        self.clt_failure_rate_spinbox.setValue(self.project_model.clt_settings.get("clt_failure_rate", 0))
        self.project_model.set_selected_failure_rate_costs(self.project_model.clt_settings.get("clt_failure_rate", 0) != 0)

        self.clt_sample_recruit_idi_spinbox.setValue(self.project_model.clt_settings.get("clt_sample_recruit_idi", 0))
        self.project_model.set_selected_idi_costs(self.project_model.clt_settings.get("clt_sample_recruit_idi", 0) != 0)
        
        self.clt_number_of_samples_to_label_spinbox.setValue(self.project_model.clt_settings.get("clt_number_of_samples_to_label", 0))
        
        self.clt_description_howtolabelthesample_textedit.blockSignals(True)
        
        cursor = self.clt_description_howtolabelthesample_textedit.textCursor()
        pos = cursor.position()

        self.clt_description_howtolabelthesample_textedit.setPlainText(self.project_model.clt_settings["clt_description_howtolabelthesample"])

        cursor.setPosition(min(pos, len(self.project_model.general["project_objectives"])))
        self.clt_description_howtolabelthesample_textedit.setTextCursor(cursor)

        self.clt_description_howtolabelthesample_textedit.setEnabled(self.project_model.clt_settings.get("clt_number_of_samples_to_label", 0) != 0)

        self.clt_description_howtolabelthesample_textedit.blockSignals(False)

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

        # Incentive
        self.project_model.set_selected_incentive_costs()

        self.update_region_visibility()

        