# ui/tabs/additional_costs_tab.py
# -*- coding: utf-8 -*-
"""
Additional Costs tab for the Project Cost Calculator application.
Manages custom costs that can be added to the project.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QComboBox, QPushButton, QHeaderView, QMessageBox,
    QTextEdit, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor
from ui.widgets.multi_select import MultiSelectWidget

from models.project_model import ProjectModel

class AdditionalCostsTab(QWidget):
    """
    Tab for managing additional custom costs for the project.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Instruction label
        instruction_label = QLabel(
            "Add custom costs for the project. These costs will be applied globally to all provinces.\n"
            "Note: If you add a DP Coding cost here, it will override the automatic DP Coding calculation."
        )
        instruction_label.setWordWrap(True)
        main_layout.addWidget(instruction_label)
        
        # Input form for adding new cost
        form_layout = QHBoxLayout()
        
        # First subtitle selection
        form_layout.addWidget(QLabel("Category:"))
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.addItems([
            "INTERVIEWER",
            "SUPERVISOR",
            "QC", 
            "DP",
            "INCENTIVE",
            "COMMUNICATION",
            "STATIONARY",
            "OTHER",
            "TRAVEL"
        ])
        self.subtitle_combo.setMinimumWidth(150)
        form_layout.addWidget(self.subtitle_combo)
        
        # Cost name
        form_layout.addWidget(QLabel("Cost Name:"))
        self.cost_name_input = QLineEdit()
        self.cost_name_input.setPlaceholderText("Enter cost name...")
        self.cost_name_input.setMinimumWidth(200)
        form_layout.addWidget(self.cost_name_input)
        
        # Unit price
        form_layout.addWidget(QLabel("Unit Price:"))
        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0, 1000000000)
        self.unit_price_spin.setSuffix(" VND")
        self.unit_price_spin.setSingleStep(1000)
        form_layout.addWidget(self.unit_price_spin)
        
        # Quantity
        form_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0, 100000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setSingleStep(1)
        form_layout.addWidget(self.quantity_spin)
        
        # Province selection
        form_layout.addWidget(QLabel("Provinces:"))
        self.provinces_widget = MultiSelectWidget([])  # Will be populated from model
        self.provinces_widget.setMinimumWidth(200)
        form_layout.addWidget(self.provinces_widget)

        form_layout.addStretch()
        
        main_layout.addLayout(form_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        self.description_input.setPlaceholderText("Enter description (optional)...")
        desc_layout.addWidget(self.description_input)
        
        # Add button
        self.add_button = QPushButton("Add Cost")
        self.add_button.clicked.connect(self.add_cost)
        desc_layout.addWidget(self.add_button)
        
        main_layout.addLayout(desc_layout)
        
        # Table for displaying additional costs
        self.costs_table = QTableWidget()
        self.costs_table.setColumnCount(7)  # Category, Cost Name, Unit Price, Quantity, Total Cost, Description, Delete
        self.costs_table.setHorizontalHeaderLabels([
            "Category",
            "Cost Name",
            "Unit Price (VND)",
            "Quantity",
            "Total Cost (VND)",
            "Description",
            ""  # Delete button column
        ])
        
        # Set header properties
        header = self.costs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Cost Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Unit Price
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total Cost
        header.setSectionResizeMode(5, QHeaderView.Stretch)           # Description
        header.setSectionResizeMode(6, QHeaderView.Fixed)             # Delete button
        
        self.costs_table.setColumnWidth(6, 80)   # Delete button
        
        # Apply styling
        self.costs_table.setAlternatingRowColors(True)
        self.costs_table.setSelectionMode(QTableWidget.SingleSelection)
        self.costs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.costs_table)
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
        # Initial update from model
        self.update_from_model()
        
    def add_cost(self):
        """Add a new additional custom cost."""
        category = self.subtitle_combo.currentText()
        cost_name = self.cost_name_input.text().strip()
        unit_price = self.unit_price_spin.value()
        quantity = self.quantity_spin.value()
        description = self.description_input.toPlainText().strip()
        selected_provinces = self.provinces_widget.get_selected_items()
        
        # Validate inputs
        if not cost_name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a cost name."
            )
            return
            
        if unit_price <= 0:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid unit price greater than 0."
            )
            return
            
        if quantity <= 0:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid quantity greater than 0."
            )
            return
        
        if not selected_provinces:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please select at least one province."
            )
            return
        
        # Check if this is a DP Coding cost
        is_dp_coding = category == "DP" and "coding" in cost_name.lower()
        
        # Add to the model
        success = self.project_model.add_additional_cost(
            category, cost_name, unit_price, quantity, description, is_dp_coding, selected_provinces
        )
        
        if success:
            # Clear inputs
            self.cost_name_input.clear()
            self.unit_price_spin.setValue(0)
            self.quantity_spin.setValue(0)
            self.description_input.clear()
            self.provinces_widget.set_selected_items([])
            
            if is_dp_coding:
                QMessageBox.information(
                    self,
                    "DP Coding Cost Added",
                    "A DP Coding cost has been added. This will override the automatic DP Coding calculation."
                )
        else:
            QMessageBox.warning(
                self,
                "Duplicate Entry",
                f"A cost with the name '{cost_name}' already exists."
            )
    
    def remove_cost(self, row):
        """
        Remove an additional cost.
        
        Args:
            row (int): Row index of the cost to remove
        """
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to remove this additional cost?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.project_model.remove_additional_cost(row)
    
    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Update available provinces
        available_provinces = self.project_model.general.get("provinces", [])
        self.provinces_widget.set_items(available_provinces)
        
        # Get additional costs from the model
        additional_costs = self.project_model.additional_costs
        
        # Set row count
        self.costs_table.setRowCount(len(additional_costs))
        
        # Populate table
        for row, cost in enumerate(additional_costs):
            # Category
            category_item = QTableWidgetItem(cost["category"])
            self.costs_table.setItem(row, 0, category_item)
            
            # Cost Name
            name_item = QTableWidgetItem(cost["name"])
            if cost.get("is_dp_coding", False):
                # Highlight DP Coding costs
                name_item.setBackground(QColor(255, 255, 200))  # Light yellow
                name_item.setToolTip("This cost overrides automatic DP Coding calculation")
            self.costs_table.setItem(row, 1, name_item)
            
            # Unit Price
            unit_price_item = QTableWidgetItem(f"{cost['unit_price']:,.0f}")
            unit_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.costs_table.setItem(row, 2, unit_price_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(f"{cost['quantity']:,.2f}")
            quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.costs_table.setItem(row, 3, quantity_item)
            
            # Total Cost
            total_cost = cost['unit_price'] * cost['quantity']
            total_cost_item = QTableWidgetItem(f"{total_cost:,.0f}")
            total_cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_cost_item.setFont(total_cost_item.font())
            font = total_cost_item.font()
            font.setBold(True)
            total_cost_item.setFont(font)
            self.costs_table.setItem(row, 4, total_cost_item)

            # Add provinces column (if you want to display it)
            provinces_list = cost.get("provinces", [])
            provinces_item = QTableWidgetItem(", ".join(provinces_list))
            self.costs_table.setItem(row, 6, provinces_item)  # Adjust column index as needed
            
            # Description
            description_item = QTableWidgetItem(cost.get("description", ""))
            self.costs_table.setItem(row, 5, description_item)
            
            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked=False, r=row: self.remove_cost(r)
            )
            self.costs_table.setCellWidget(row, 6, delete_button)