from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QDialogButtonBox, QFormLayout, QGroupBox,
    QTabWidget, QWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from models.project_model import ProjectModel
from config.predefined_values import ASSIGNED_PEOPLE_LEVELS, DEFAULT_TRAVEL_COSTS, VIETNAM_PROVINCES

class SettingsDialog(QDialog):
    """
    Dialog for managing application settings.
    """
    def __init__(self, project_model, parent=None):
        super().__init__(parent)
        self.project_model = project_model
        
        self.setWindowTitle("Application Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Create tab for supervisor settings
        supervisor_tab = QWidget()
        supervisor_layout = QVBoxLayout(supervisor_tab)
        
        # Create supervisor settings group
        supervisor_group = QGroupBox("Supervisor Settings")
        supervisor_form_layout = QFormLayout(supervisor_group)
        
        # Interviewers per supervisor setting
        self.interviewers_per_supervisor_spin = QSpinBox()
        self.interviewers_per_supervisor_spin.setRange(1, 50)
        self.interviewers_per_supervisor_spin.setValue(
            self.project_model.settings.get("interviewers_per_supervisor", 8)
        )
        self.interviewers_per_supervisor_spin.setSuffix(" interviewers")
        supervisor_form_layout.addRow("Number of interviewers each supervisor manages:", 
                                self.interviewers_per_supervisor_spin)
        
        # Add help text
        help_label = QLabel("This value is used to calculate the daily supervisor target in the Samples tab.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-style: italic;")
        supervisor_form_layout.addRow("", help_label)
        
        supervisor_layout.addWidget(supervisor_group)
        supervisor_layout.addStretch()
        
        # Create tab for general cost settings
        cost_tab = QWidget()
        cost_layout = QVBoxLayout(cost_tab)
        
        # Create "Others" cost settings group
        others_group = QGroupBox("Others")
        others_form_layout = QFormLayout(others_group)
        
        # Parking fee
        self.parking_fee_spin = QSpinBox()
        self.parking_fee_spin.setRange(0, 100000)
        self.parking_fee_spin.setValue(
            self.project_model.settings.get("parking_fee", 5000)
        )
        self.parking_fee_spin.setSuffix(" VND")
        others_form_layout.addRow("Parking fee:", self.parking_fee_spin)
        
        # Distant district fee
        self.distant_district_fee_spin = QSpinBox()
        self.distant_district_fee_spin.setRange(0, 100000)
        self.distant_district_fee_spin.setValue(
            self.project_model.settings.get("distant_district_fee", 5000)
        )
        self.distant_district_fee_spin.setSuffix(" VND")
        others_form_layout.addRow("Distant district support fee:", self.distant_district_fee_spin)
        
        # Add others group to cost tab
        cost_layout.addWidget(others_group)
        cost_layout.addStretch()
        
        # Add tabs to tab widget
        self.tabs.addTab(supervisor_tab, "Supervisor")
        self.tabs.addTab(cost_tab, "Cost Settings")
        
        # Create stationary settings tab with province selection
        stationary_tab = QWidget()
        stationary_layout = QVBoxLayout(stationary_tab)

        # Province selection
        province_layout = QHBoxLayout()
        province_layout.addWidget(QLabel("Province:"))
        self.province_combo = QComboBox()
        self.province_combo.addItems(["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Cần Thơ", "Others"])
        self.province_combo.currentTextChanged.connect(self.load_province_stationary_settings)
        province_layout.addWidget(self.province_combo)
        province_layout.addStretch()
        stationary_layout.addLayout(province_layout)

        # Stationary settings form
        stationary_form_group = QGroupBox("Stationary Costs")
        self.stationary_form = QFormLayout(stationary_form_group)

        # Black and white photo fee
        self.bw_photo_fee_spin = QSpinBox()
        self.bw_photo_fee_spin.setRange(0, 100000)
        self.bw_photo_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Black and white photo fee:", self.bw_photo_fee_spin)

        # Color photo fee
        self.color_photo_fee_spin = QSpinBox()
        self.color_photo_fee_spin.setRange(0, 100000)
        self.color_photo_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Color photo fee:", self.color_photo_fee_spin)

        # Lamination fee
        self.lamination_fee_spin = QSpinBox()
        self.lamination_fee_spin.setRange(0, 100000)
        self.lamination_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Plastic lamination fee:", self.lamination_fee_spin)
        
        # Showcard fee
        self.showcard_fee_spin = QSpinBox()
        self.showcard_fee_spin.setRange(0, 100000)
        self.showcard_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Showcard fee:", self.showcard_fee_spin)

        # Dropcard fee
        self.dropcard_fee_spin = QSpinBox()
        self.dropcard_fee_spin.setRange(0, 100000)
        self.dropcard_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Dropcard fee:", self.dropcard_fee_spin)

        # Showphoto fee
        self.showphoto_fee_spin = QSpinBox()
        self.showphoto_fee_spin.setRange(0, 100000)
        self.showphoto_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Showphoto fee:", self.showphoto_fee_spin)

        # Decal fee
        self.decal_fee_spin = QSpinBox()
        self.decal_fee_spin.setRange(0, 100000)
        self.decal_fee_spin.setSuffix(" VND")
        self.stationary_form.addRow("Decal fee:", self.decal_fee_spin)

        stationary_layout.addWidget(stationary_form_group)
        stationary_layout.addStretch()

        # Add tab
        self.tabs.addTab(stationary_tab, "Stationary Costs")
        
        # Create tab for travel costs
        travel_tab = QWidget()
        travel_layout = QVBoxLayout(travel_tab)

        # Create travel settings group
        travel_group = QGroupBox("Travel Costs by Level")
        travel_form_layout = QFormLayout(travel_group)

        # Create settings for each level
        for level in ASSIGNED_PEOPLE_LEVELS:
            level_group = QGroupBox(level)
            level_layout = QFormLayout(level_group)
            
            # Hotel cost
            hotel_spin = QSpinBox()
            hotel_spin.setRange(0, 10000000)
            hotel_spin.setValue(
                self.project_model.settings.get(f"travel_{level.lower()}_hotel", DEFAULT_TRAVEL_COSTS[level]["hotel"])
            )
            hotel_spin.setSuffix(" VND")
            hotel_spin.setSingleStep(100000)
            level_layout.addRow("Chi phí Khách sạn:", hotel_spin)
            setattr(self, f"travel_{level.lower()}_hotel_spin", hotel_spin)
            
            # Food cost
            food_spin = QSpinBox()
            food_spin.setRange(0, 10000000)
            food_spin.setValue(
                self.project_model.settings.get(f"travel_{level.lower()}_food", DEFAULT_TRAVEL_COSTS[level]["food"])
            )
            food_spin.setSuffix(" VND")
            food_spin.setSingleStep(100000)
            level_layout.addRow("Chi phí ăn uống:", food_spin)
            setattr(self, f"travel_{level.lower()}_food_spin", food_spin)
            
            travel_form_layout.addRow(level_group)

        travel_group.setLayout(travel_form_layout)
        travel_layout.addWidget(travel_group)
        travel_layout.addStretch()

        # Add tab to tab widget
        self.tabs.addTab(travel_tab, "Travel Costs")
        
        # Create tab for province-specific transportation costs
        transport_tab = QWidget()
        transport_layout = QVBoxLayout(transport_tab)
        
        # Instructions
        transport_instructions = QLabel(
            "Set flight and train ticket costs for specific provinces. "
            "Provinces not listed here will use the 'Others' costs."
        )
        transport_instructions.setWordWrap(True)
        transport_layout.addWidget(transport_instructions)
        
        # Table for province costs
        self.transport_table = QTableWidget()
        self.transport_table.setColumnCount(4)  # Province, Flight, Train, Actions
        self.transport_table.setHorizontalHeaderLabels([
            "Province", "Vé máy bay (VND)", "Vé xe/tàu (VND)", "Actions"
        ])
        
        # Set header properties
        header = self.transport_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        
        self.transport_table.setColumnWidth(3, 100)
        
        transport_layout.addWidget(self.transport_table)
        
        # Add province controls
        add_transport_layout = QHBoxLayout()
        
        self.transport_province_combo = QComboBox()
        # Add available provinces excluding those already added
        add_transport_layout.addWidget(QLabel("Province:"))
        add_transport_layout.addWidget(self.transport_province_combo)
        
        add_transport_button = QPushButton("Add Province")
        add_transport_button.clicked.connect(self.add_transport_province)
        add_transport_layout.addWidget(add_transport_button)
        
        add_transport_layout.addStretch()
        transport_layout.addLayout(add_transport_layout)
        
        # Add tab
        self.tabs.addTab(transport_tab, "Transportation Costs")
        
        # Add tab widget to main layout
        layout.addWidget(self.tabs)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load initial province settings
        self.load_province_stationary_settings(self.province_combo.currentText())
        
        # Load transportation costs
        self.load_transportation_costs()

    def load_transportation_costs(self):
        """Load province-specific transportation costs into the table."""
        self.transport_table.setRowCount(0)
        
        # Get transportation settings
        transportation = self.project_model.settings.get("transportation", {})
        
        # Add each province to the table
        for province, costs in transportation.items():
            self.add_transport_row(province, costs)
        
        # Update available provinces in combo
        self.update_available_transport_provinces()
    
    def add_transport_row(self, province, costs):
        """Add a row to the transportation table."""
        row = self.transport_table.rowCount()
        self.transport_table.insertRow(row)
        
        # Province name
        province_item = QTableWidgetItem(province)
        province_item.setFlags(province_item.flags() & ~Qt.ItemIsEditable)
        self.transport_table.setItem(row, 0, province_item)
        
        # Flight cost
        flight_spin = QSpinBox()
        flight_spin.setRange(0, 100000000)
        flight_spin.setValue(costs.get("flight", 0))
        flight_spin.setSuffix(" VND")
        flight_spin.setSingleStep(100000)
        self.transport_table.setCellWidget(row, 1, flight_spin)
        
        # Train cost
        train_spin = QSpinBox()
        train_spin.setRange(0, 10000000)
        train_spin.setValue(costs.get("train", 400000))
        train_spin.setSuffix(" VND")
        train_spin.setSingleStep(50000)
        self.transport_table.setCellWidget(row, 2, train_spin)
        
        # Delete button
        if province != "Others":  # Can't delete "Others"
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, r=row: self.delete_transport_province(r))
            self.transport_table.setCellWidget(row, 3, delete_button)
    
    def add_transport_province(self):
        """Add a new province to the transportation costs table."""
        province = self.transport_province_combo.currentText()
        if not province:
            return
        
        # Add the row with default costs
        default_costs = {"flight": 0, "train": 400000}
        self.add_transport_row(province, default_costs)
        
        # Update available provinces
        self.update_available_transport_provinces()
    
    def delete_transport_province(self, row):
        """Delete a province from the transportation costs table."""
        self.transport_table.removeRow(row)
        self.update_available_transport_provinces()
    
    def update_available_transport_provinces(self):
        """Update the combo box with provinces not yet added."""
        # Get currently added provinces
        added_provinces = set()
        for row in range(self.transport_table.rowCount()):
            province_item = self.transport_table.item(row, 0)
            if province_item:
                added_provinces.add(province_item.text())
        
        # Update combo box
        self.transport_province_combo.clear()
        available_provinces = [p for p in VIETNAM_PROVINCES if p not in added_provinces]
        self.transport_province_combo.addItems(available_provinces)

    def accept(self):
        """Save settings when OK is clicked."""
        # Save interviewers per supervisor
        self.project_model.update_settings(
            "interviewers_per_supervisor", 
            self.interviewers_per_supervisor_spin.value()
        )
        
        # Save other settings
        self.project_model.update_settings(
            "parking_fee",
            self.parking_fee_spin.value()
        )
        
        self.project_model.update_settings(
            "distant_district_fee",
            self.distant_district_fee_spin.value()
        )
        
        # Save stationary settings for the current province
        self.save_province_stationary_settings()
        
        # Save travel costs settings
        for level in ASSIGNED_PEOPLE_LEVELS:
            # Save hotel cost
            hotel_spin = getattr(self, f"travel_{level.lower()}_hotel_spin")
            self.project_model.update_settings(
                f"travel_{level.lower()}_hotel",
                hotel_spin.value()
            )
            
            # Save food cost
            food_spin = getattr(self, f"travel_{level.lower()}_food_spin")
            self.project_model.update_settings(
                f"travel_{level.lower()}_food",
                food_spin.value()
            )
        
        # Save transportation costs
        transportation = {}
        for row in range(self.transport_table.rowCount()):
            province_item = self.transport_table.item(row, 0)
            if province_item:
                province = province_item.text()
                flight_spin = self.transport_table.cellWidget(row, 1)
                train_spin = self.transport_table.cellWidget(row, 2)
                
                transportation[province] = {
                    "flight": flight_spin.value() if flight_spin else 0,
                    "train": train_spin.value() if train_spin else 400000
                }
        
        # Always ensure "Others" exists
        if "Others" not in transportation:
            transportation["Others"] = {"flight": 0, "train": 400000}
        
        self.project_model.update_settings("transportation", transportation)

        super().accept()

    def load_province_stationary_settings(self, province):
        """Load stationary settings for the selected province."""
        stationary = self.project_model.settings.get("stationary", {})
        province_settings = stationary.get(province, {})
        
        # Load values into form fields with proper defaults
        default_settings = stationary.get("Others", {})
        
        self.bw_photo_fee_spin.setValue(
            province_settings.get("bw_photo_fee", 
                                default_settings.get("bw_photo_fee", 350))
        )
        self.color_photo_fee_spin.setValue(
            province_settings.get("color_photo_fee", 
                                default_settings.get("color_photo_fee", 2500))
        )
        self.lamination_fee_spin.setValue(
            province_settings.get("lamination_fee", 
                                default_settings.get("lamination_fee", 6000))
        )
        self.dropcard_fee_spin.setValue(
            province_settings.get("dropcard_fee", 
                                default_settings.get("dropcard_fee", 9000))
        )
        self.showphoto_fee_spin.setValue(
            province_settings.get("showphoto_fee", 
                                default_settings.get("showphoto_fee", 2500))
        )
        self.decal_fee_spin.setValue(
            province_settings.get("decal_fee", 
                                default_settings.get("decal_fee", 3500))
        )
        
        self.showcard_fee_spin.setValue(
            province_settings.get("showcard_fee", 
                                default_settings.get("showcard_fee", 4000))
        )

    def save_province_stationary_settings(self):
        """Save stationary settings for the current province."""
        province = self.province_combo.currentText()
        
        # Save each stationary setting for this province
        self.project_model.update_stationary_settings(
            province, "bw_photo_fee", self.bw_photo_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "color_photo_fee", self.color_photo_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "lamination_fee", self.lamination_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "dropcard_fee", self.dropcard_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "showphoto_fee", self.showphoto_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "decal_fee", self.decal_fee_spin.value()
        )
        self.project_model.update_stationary_settings(
            province, "showcard_fee", self.showcard_fee_spin.value()
        )