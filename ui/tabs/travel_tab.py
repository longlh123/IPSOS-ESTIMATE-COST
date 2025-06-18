# ui/tabs/travel_tab.py
# -*- coding: utf-8 -*-
"""
Travel tab for the Project Cost Calculator application.
Manages travel details for each province.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QLabel, QSpinBox, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QColor

from ui.widgets.assigned_people_widget import AssignedPeopleWidget


class TravelTab(QWidget):
    """
    Tab for managing travel details for each province.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Instruction label
        instruction_label = QLabel(
            "Define travel details for each province."
        )
        instruction_label.setWordWrap(True)
        main_layout.addWidget(instruction_label)
        
        # Create province tabs
        self.province_tabs = QTabWidget()
        self.province_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.province_tabs)
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
        # Initial update from model
        self.update_from_model()
        
    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Get selected provinces
        provinces = self.project_model.general["provinces"]
        
        # Save current tab index
        current_index = self.province_tabs.currentIndex()
        
        # Clear existing tabs
        while self.province_tabs.count() > 0:
            self.province_tabs.removeTab(0)
            
        # If no provinces, show a message
        if not provinces:
            msg_label = QLabel(
                "Please select at least one province in the General tab."
            )
            msg_label.setAlignment(Qt.AlignCenter)
            
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.addStretch()
            empty_layout.addWidget(msg_label)
            empty_layout.addStretch()
            
            self.province_tabs.addTab(empty_widget, "No Data")
            return
            
        # Create a tab for each province
        for province in provinces:
            province_widget = QWidget()
            province_layout = QVBoxLayout(province_widget)
            
            # Create a travel tree for this province
            tree = TravelTree(
                self.project_model,
                province
            )
            province_layout.addWidget(tree)
            
            # Add tab for this province
            self.province_tabs.addTab(province_widget, province)
            
        # Restore tab index if possible
        if current_index >= 0 and current_index < self.province_tabs.count():
            self.province_tabs.setCurrentIndex(current_index)


class TravelTree(QTreeWidget):
    """
    Tree widget for displaying and editing travel details.
    """
    def __init__(self, project_model, province):
        """
        Initialize the tree.
        
        Args:
            project_model (ProjectModel): Project model
            province (str): Province name
        """
        super().__init__()
        self.project_model = project_model
        self.province = province
        
        # Set column count and headers
        self.setColumnCount(2)  # Category, Value
        self.setHeaderLabels(["Category", "Value"])
        
        # Set header properties
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Category
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Value
        
        # Apply some styling
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.NoSelection)
        
        # Populate tree
        self.populate_tree()
    
    def populate_tree(self):
        """Populate the tree with data."""
        # Get data from model
        # Get project type
        project_type = self.project_model.general.get("project_type", "")
        
        # Get data from model
        travel_data = {}
        if self.province in self.project_model.travel:
            travel_data = self.project_model.travel[self.province]
        
        # Create FULLTIME item
        fulltime_item = QTreeWidgetItem(["FULLTIME", ""])
        self.addTopLevelItem(fulltime_item)
        
        # Create transportation selection item
        transport_item = QTreeWidgetItem(["Transportation Type", ""])
        fulltime_item.addChild(transport_item)
        
        # Create ComboBox for transportation selection
        transport_combo = QComboBox()
        transport_combo.addItems(["tàu/xe", "máy bay"])
        
        # Set the value from the model if available
        current_transport = "tàu/xe"  # Default value
        if "fulltime" in travel_data:
            current_transport = travel_data["fulltime"].get("transportation_type", "tàu/xe")
        
        # Set current selection
        transport_combo.setCurrentText(current_transport)
        
        # Connect to update method
        transport_combo.currentTextChanged.connect(
            lambda value: self.update_transportation_type(value)
        )
        self.setItemWidget(transport_item, 1, transport_combo)
        
        # Create travel days item
        fulltime_days_item = QTreeWidgetItem(["Travel Days", ""])
        fulltime_item.addChild(fulltime_days_item)
        
        # Create SpinBox for travel days
        fulltime_days_spin = QSpinBox()
        fulltime_days_spin.setRange(0, 999)
        
        # Set the value from the model if available
        if "fulltime" in travel_data:
            fulltime_days_spin.setValue(travel_data["fulltime"].get("travel_days", 0))
        else:
            fulltime_days_spin.setValue(0)
            
        fulltime_days_spin.valueChanged.connect(
            lambda value: self.update_fulltime_travel_days(value)
        )
        self.setItemWidget(fulltime_days_item, 1, fulltime_days_spin)
        
        # Create travel nights item
        fulltime_nights_item = QTreeWidgetItem(["Travel Nights", ""])
        fulltime_item.addChild(fulltime_nights_item)
        
        # Create SpinBox for travel nights
        fulltime_nights_spin = QSpinBox()
        fulltime_nights_spin.setRange(0, 999)
        
        # Set the value from the model if available
        if "fulltime" in travel_data:
            fulltime_nights_spin.setValue(travel_data["fulltime"].get("travel_nights", 0))
        else:
            fulltime_nights_spin.setValue(0)
            
        fulltime_nights_spin.valueChanged.connect(
            lambda value: self.update_fulltime_travel_nights(value)
        )
        self.setItemWidget(fulltime_nights_item, 1, fulltime_nights_spin)
        
        # Create assigned people item
        fulltime_people_item = QTreeWidgetItem(["Assigned People", ""])
        fulltime_item.addChild(fulltime_people_item)
        
        # Create people selection widget
        people_selection = AssignedPeopleWidget(
            self.project_model,
            self.province,
            self
        )
        self.setItemWidget(fulltime_people_item, 1, people_selection)
        
        # Create PARTTIME item
        parttime_item = QTreeWidgetItem(["PARTTIME", ""])
        self.addTopLevelItem(parttime_item)
        
        # Add PARTTIME sub-categories with dynamic UI based on project type
        parttime_data = travel_data.get("parttime", {
            "supervisor": {
                "distant": 0, "nearby": 0,
                "recruit_distant": 0, "recruit_nearby": 0,
                "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
            },
            "interviewer": {
                "distant": 0, "nearby": 0,
                "recruit_distant": 0, "recruit_nearby": 0,
                "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
            },
            "qc": {"distant": 0, "nearby": 0}
        })
        
        # SUPERVISOR
        supervisor_item = QTreeWidgetItem(["SUPERVISOR", ""])
        parttime_item.addChild(supervisor_item)
        
        if project_type == "CLT":
            # For CLT, create a more complex structure with recruit/ngoi_ban types
            
            # SUPERVISOR > RECRUIT
            recruit_item = QTreeWidgetItem(["RECRUIT", ""])
            supervisor_item.addChild(recruit_item)
            
            # Distant districts for RECRUIT
            recruit_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            recruit_item.addChild(recruit_distant_item)
            
            recruit_distant_spin = QSpinBox()
            recruit_distant_spin.setRange(0, 999)
            recruit_distant_spin.setValue(parttime_data.get("supervisor", {}).get("recruit_distant", 0))
            recruit_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "recruit_distant", value
                )
            )
            self.setItemWidget(recruit_distant_item, 1, recruit_distant_spin)
            
            # Nearby districts for RECRUIT
            recruit_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            recruit_item.addChild(recruit_nearby_item)
            
            recruit_nearby_spin = QSpinBox()
            recruit_nearby_spin.setRange(0, 999)
            recruit_nearby_spin.setValue(parttime_data.get("supervisor", {}).get("recruit_nearby", 0))
            recruit_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "recruit_nearby", value
                )
            )
            self.setItemWidget(recruit_nearby_item, 1, recruit_nearby_spin)
            
            # SUPERVISOR > NGOI BAN
            ngoi_ban_item = QTreeWidgetItem(["NGỒI BÀN", ""])
            supervisor_item.addChild(ngoi_ban_item)
            
            # Distant districts for NGOI BAN
            ngoi_ban_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            ngoi_ban_item.addChild(ngoi_ban_distant_item)
            
            ngoi_ban_distant_spin = QSpinBox()
            ngoi_ban_distant_spin.setRange(0, 999)
            ngoi_ban_distant_spin.setValue(parttime_data.get("supervisor", {}).get("ngoi_ban_distant", 0))
            ngoi_ban_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "ngoi_ban_distant", value
                )
            )
            self.setItemWidget(ngoi_ban_distant_item, 1, ngoi_ban_distant_spin)
            
            # Nearby districts for NGOI BAN
            ngoi_ban_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            ngoi_ban_item.addChild(ngoi_ban_nearby_item)
            
            ngoi_ban_nearby_spin = QSpinBox()
            ngoi_ban_nearby_spin.setRange(0, 999)
            ngoi_ban_nearby_spin.setValue(parttime_data.get("supervisor", {}).get("ngoi_ban_nearby", 0))
            ngoi_ban_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "ngoi_ban_nearby", value
                )
            )
            self.setItemWidget(ngoi_ban_nearby_item, 1, ngoi_ban_nearby_spin)
        else:
            # For F2F/D2D and other project types, use the simple distant/nearby structure
            
            # Distant districts
            supervisor_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            supervisor_item.addChild(supervisor_distant_item)
            
            supervisor_distant_spin = QSpinBox()
            supervisor_distant_spin.setRange(0, 999)
            supervisor_distant_spin.setValue(parttime_data.get("supervisor", {}).get("distant", 0))
            supervisor_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "distant", value
                )
            )
            self.setItemWidget(supervisor_distant_item, 1, supervisor_distant_spin)
            
            # Nearby districts
            supervisor_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            supervisor_item.addChild(supervisor_nearby_item)
            
            supervisor_nearby_spin = QSpinBox()
            supervisor_nearby_spin.setRange(0, 999)
            supervisor_nearby_spin.setValue(parttime_data.get("supervisor", {}).get("nearby", 0))
            supervisor_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "supervisor", "nearby", value
                )
            )
            self.setItemWidget(supervisor_nearby_item, 1, supervisor_nearby_spin)
        
        # INTERVIEWER
        interviewer_item = QTreeWidgetItem(["INTERVIEWER", ""])
        parttime_item.addChild(interviewer_item)
        
        if project_type == "CLT":
            # For CLT, create a more complex structure with recruit/ngoi_ban types
            
            # INTERVIEWER > RECRUIT
            recruit_item = QTreeWidgetItem(["RECRUIT", ""])
            interviewer_item.addChild(recruit_item)
            
            # Distant districts for RECRUIT
            recruit_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            recruit_item.addChild(recruit_distant_item)
            
            recruit_distant_spin = QSpinBox()
            recruit_distant_spin.setRange(0, 999)
            recruit_distant_spin.setValue(parttime_data.get("interviewer", {}).get("recruit_distant", 0))
            recruit_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "recruit_distant", value
                )
            )
            self.setItemWidget(recruit_distant_item, 1, recruit_distant_spin)
            
            # Nearby districts for RECRUIT
            recruit_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            recruit_item.addChild(recruit_nearby_item)
            
            recruit_nearby_spin = QSpinBox()
            recruit_nearby_spin.setRange(0, 999)
            recruit_nearby_spin.setValue(parttime_data.get("interviewer", {}).get("recruit_nearby", 0))
            recruit_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "recruit_nearby", value
                )
            )
            self.setItemWidget(recruit_nearby_item, 1, recruit_nearby_spin)
            
            # INTERVIEWER > NGOI BAN
            ngoi_ban_item = QTreeWidgetItem(["NGỒI BÀN", ""])
            interviewer_item.addChild(ngoi_ban_item)
            
            # Distant districts for NGOI BAN
            ngoi_ban_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            ngoi_ban_item.addChild(ngoi_ban_distant_item)
            
            ngoi_ban_distant_spin = QSpinBox()
            ngoi_ban_distant_spin.setRange(0, 999)
            ngoi_ban_distant_spin.setValue(parttime_data.get("interviewer", {}).get("ngoi_ban_distant", 0))
            ngoi_ban_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "ngoi_ban_distant", value
                )
            )
            self.setItemWidget(ngoi_ban_distant_item, 1, ngoi_ban_distant_spin)
            
            # Nearby districts for NGOI BAN
            ngoi_ban_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            ngoi_ban_item.addChild(ngoi_ban_nearby_item)
            
            ngoi_ban_nearby_spin = QSpinBox()
            ngoi_ban_nearby_spin.setRange(0, 999)
            ngoi_ban_nearby_spin.setValue(parttime_data.get("interviewer", {}).get("ngoi_ban_nearby", 0))
            ngoi_ban_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "ngoi_ban_nearby", value
                )
            )
            self.setItemWidget(ngoi_ban_nearby_item, 1, ngoi_ban_nearby_spin)
        else:
            # For F2F/D2D and other project types, use the simple distant/nearby structure
            
            # Distant districts
            interviewer_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
            interviewer_item.addChild(interviewer_distant_item)
            
            interviewer_distant_spin = QSpinBox()
            interviewer_distant_spin.setRange(0, 999)
            interviewer_distant_spin.setValue(parttime_data.get("interviewer", {}).get("distant", 0))
            interviewer_distant_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "distant", value
                )
            )
            self.setItemWidget(interviewer_distant_item, 1, interviewer_distant_spin)
            
            # Nearby districts
            interviewer_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
            interviewer_item.addChild(interviewer_nearby_item)
            
            interviewer_nearby_spin = QSpinBox()
            interviewer_nearby_spin.setRange(0, 999)
            interviewer_nearby_spin.setValue(parttime_data.get("interviewer", {}).get("nearby", 0))
            interviewer_nearby_spin.valueChanged.connect(
                lambda value: self.project_model.update_travel(
                    self.province, "parttime", "interviewer", "nearby", value
                )
            )
            self.setItemWidget(interviewer_nearby_item, 1, interviewer_nearby_spin)
        
        # QC - same for all project types
        qc_item = QTreeWidgetItem(["QC", ""])
        parttime_item.addChild(qc_item)
        
        # Distant districts
        qc_distant_item = QTreeWidgetItem(["How many people in distant districts?", ""])
        qc_item.addChild(qc_distant_item)
        
        qc_distant_spin = QSpinBox()
        qc_distant_spin.setRange(0, 999)
        qc_distant_spin.setValue(parttime_data.get("qc", {}).get("distant", 0))
        qc_distant_spin.valueChanged.connect(
            lambda value: self.project_model.update_travel(
                self.province, "parttime", "qc", "distant", value
            )
        )
        self.setItemWidget(qc_distant_item, 1, qc_distant_spin)
        
        # Nearby districts
        qc_nearby_item = QTreeWidgetItem(["How many people in nearby districts?", ""])
        qc_item.addChild(qc_nearby_item)
        
        qc_nearby_spin = QSpinBox()
        qc_nearby_spin.setRange(0, 999)
        qc_nearby_spin.setValue(parttime_data.get("qc", {}).get("nearby", 0))
        qc_nearby_spin.valueChanged.connect(
            lambda value: self.project_model.update_travel(
                self.province, "parttime", "qc", "nearby", value
            )
        )
        self.setItemWidget(qc_nearby_item, 1, qc_nearby_spin)
        
        # Expand all items
        self.expandAll()

    def update_transportation_type(self, value):
        """Update transportation type in the model."""
        if self.province not in self.project_model.travel:
            self.project_model.travel[self.province] = {
                "fulltime": {
                    "travel_days": 0,
                    "travel_nights": 0,
                    "assigned_people": [],
                    "transportation_type": "tàu/xe"
                },
                "parttime": {
                    "supervisor": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "interviewer": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "qc": {"distant": 0, "nearby": 0}
                }
            }
        
        if "fulltime" not in self.project_model.travel[self.province]:
            self.project_model.travel[self.province]["fulltime"] = {
                "travel_days": 0,
                "travel_nights": 0,
                "assigned_people": [],
                "transportation_type": "tàu/xe"
            }
            
        # Update transportation type
        self.project_model.travel[self.province]["fulltime"]["transportation_type"] = value
        
        # Emit dataChanged signal
        self.project_model.dataChanged.emit()

    def update_fulltime_travel_days(self, value):
        """Update fulltime travel days in the model."""
        if self.province not in self.project_model.travel:
            self.project_model.travel[self.province] = {
                "fulltime": {
                    "travel_days": 0,
                    "travel_nights": 0,
                    "assigned_people": [],
                    "transportation_type": "tàu/xe"  # Add default transportation type
                },
                "parttime": {
                    "supervisor": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "interviewer": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "qc": {"distant": 0, "nearby": 0}
                }
            }
        
        if "fulltime" not in self.project_model.travel[self.province]:
            self.project_model.travel[self.province]["fulltime"] = {
                "travel_days": 0,
                "travel_nights": 0,
                "assigned_people": [],
                "transportation_type": "tàu/xe"  # Add default transportation type
            }
            
        # Update travel days
        self.project_model.travel[self.province]["fulltime"]["travel_days"] = value
        
        # Emit dataChanged signal
        self.project_model.dataChanged.emit()

    def update_fulltime_travel_nights(self, value):
        """Update fulltime travel nights in the model."""
        if self.province not in self.project_model.travel:
            self.project_model.travel[self.province] = {
                "fulltime": {
                    "travel_days": 0,
                    "travel_nights": 0,
                    "assigned_people": [],
                    "transportation_type": "tàu/xe"  # Add default transportation type
                },
                "parttime": {
                    "supervisor": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "interviewer": {
                        "distant": 0, "nearby": 0,
                        "recruit_distant": 0, "recruit_nearby": 0,
                        "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
                    },
                    "qc": {"distant": 0, "nearby": 0}
                }
            }
        
        if "fulltime" not in self.project_model.travel[self.province]:
            self.project_model.travel[self.province]["fulltime"] = {
                "travel_days": 0,
                "travel_nights": 0,
                "assigned_people": [],
                "transportation_type": "tàu/xe"  # Add default transportation type
            }
            
        # Update travel nights
        self.project_model.travel[self.province]["fulltime"]["travel_nights"] = value
        
        # Emit dataChanged signal
        self.project_model.dataChanged.emit()