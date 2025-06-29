# ui/tabs/qc_tab.py
# -*- coding: utf-8 -*-
"""
QC Method tab for the Project Cost Calculator application.
Manages QC methods, teams, and rates.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QDoubleSpinBox, QPushButton, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot

from models.project_model import ProjectModel
from config.predefined_values import TEAMS, QC_METHODS


class QCMethodTab(QWidget):
    """
    Tab for managing QC methods, teams, and rates.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Instruction label
        instruction_label = QLabel(
            "Define QC methods for each team and set QC rates."
        )
        instruction_label.setWordWrap(True)
        main_layout.addWidget(instruction_label)
        
        # Controls for adding new QC method
        add_layout = QHBoxLayout()
        
        self.team_combo = QComboBox()
        self.team_combo.addItems(TEAMS)
        add_layout.addWidget(QLabel("Team:"))
        add_layout.addWidget(self.team_combo)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(QC_METHODS)
        add_layout.addWidget(QLabel("QC Method:"))
        add_layout.addWidget(self.method_combo)
        
        self.rate_spinbox = QDoubleSpinBox()
        self.rate_spinbox.setRange(0.0, 100.0)
        self.rate_spinbox.setValue(10.0)
        self.rate_spinbox.setSuffix("%")
        self.rate_spinbox.setDecimals(1)
        self.rate_spinbox.setSingleStep(1.0)
        add_layout.addWidget(QLabel("QC Rate:"))
        add_layout.addWidget(self.rate_spinbox)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_qc_method)
        add_layout.addWidget(add_button)
        
        main_layout.addLayout(add_layout)
        
        # Table for displaying QC methods
        self.qc_table = QTableWidget()
        self.qc_table.setColumnCount(4)  # Team, QC Method, QC Rate, Delete
        self.qc_table.setHorizontalHeaderLabels([
            "Team",
            "QC Method",
            "QC Rate",
            ""  # Delete button column
        ])
        
        # Set header properties
        header = self.qc_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Team
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # QC Method
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # QC Rate
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Delete button
        
        self.qc_table.setColumnWidth(2, 100)  # QC Rate
        self.qc_table.setColumnWidth(3, 80)   # Delete button
        
        # Apply styling
        self.qc_table.setAlternatingRowColors(True)
        self.qc_table.setSelectionMode(QTableWidget.SingleSelection)
        self.qc_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.qc_table)
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
        # Initial update from model
        self.update_from_model()
        
    def add_qc_method(self):
        """Add a new QC method."""
        team = self.team_combo.currentText()
        method = self.method_combo.currentText()
        rate = self.rate_spinbox.value()
        
        # Validate inputs
        if not team or not method:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please select a team and QC method."
            )
            return
            
        # Try to add to the model
        success = self.project_model.add_qc_method(team, method, rate)
        
        if not success:
            QMessageBox.warning(
                self,
                "Duplicate Entry",
                f"A QC method for team '{team}' with method '{method}' already exists."
            )
    
    def remove_qc_method(self, row):
        """
        Remove a QC method.
        
        Args:
            row (int): Row index of the method to remove
        """
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to remove this QC method?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.project_model.remove_qc_method(row)
    
    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Get QC methods from the model
        qc_methods = self.project_model.qc_methods
        
        # Set row count
        self.qc_table.setRowCount(len(qc_methods))
        
        # Populate table
        for row, qc_method in enumerate(qc_methods):
            # Team
            team_item = QTableWidgetItem(qc_method["team"])
            self.qc_table.setItem(row, 0, team_item)
            
            # QC Method
            method_item = QTableWidgetItem(qc_method["method"])
            self.qc_table.setItem(row, 1, method_item)
            
            # QC Rate
            rate_spinbox = QDoubleSpinBox()
            rate_spinbox.setRange(0.0, 100.0)
            rate_spinbox.setValue(qc_method["rate"])
            rate_spinbox.setSuffix("%")
            rate_spinbox.setDecimals(1)
            rate_spinbox.setSingleStep(1.0)
            rate_spinbox.valueChanged.connect(
                lambda value, r=row: self.update_qc_rate(r, value)
            )
            self.qc_table.setCellWidget(row, 2, rate_spinbox)
            
            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked=False, r=row: self.remove_qc_method(r)
            )
            self.qc_table.setCellWidget(row, 3, delete_button)
    
    def update_qc_rate(self, row, value):
        """
        Update the QC rate for a method.
        
        Args:
            row (int): Row index of the method
            value (float): New QC rate value
        """
        # Update the rate in the model
        if 0 <= row < len(self.project_model.qc_methods):
            self.project_model.qc_methods[row]["rate"] = value
            self.project_model.dataChanged.emit()