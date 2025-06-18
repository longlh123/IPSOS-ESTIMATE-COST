# ui/tabs/assignment_tab.py
# -*- coding: utf-8 -*-
"""
Assignment tab for the Project Cost Calculator application.
Manages people assigned to the project with their levels and emails.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QComboBox, QPushButton, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot

from models.project_model import ProjectModel

class AssignmentTab(QWidget):
    """
    Tab for managing people assigned to the project.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Instruction label
        instruction_label = QLabel(
            "Manage people assigned to the project. These people can be selected for travel in the Travel tab."
        )
        instruction_label.setWordWrap(True)
        main_layout.addWidget(instruction_label)
        
        # Controls for adding new assignment
        add_layout = QHBoxLayout()
        
        # Level combo box
        self.level_combo = QComboBox()
        self.level_combo.addItems(["Junior", "Senior", "Manager", "Director"])
        add_layout.addWidget(QLabel("Level:"))
        add_layout.addWidget(self.level_combo)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address...")
        add_layout.addWidget(QLabel("Email:"))
        add_layout.addWidget(self.email_input)
        
        # Add button
        add_button = QPushButton("Add Person")
        add_button.clicked.connect(self.add_person)
        add_layout.addWidget(add_button)
        
        main_layout.addLayout(add_layout)
        
        # Table for displaying assignments
        self.assignment_table = QTableWidget()
        self.assignment_table.setColumnCount(3)  # Level, Email, Delete
        self.assignment_table.setHorizontalHeaderLabels([
            "Level",
            "Email",
            ""  # Delete button column
        ])
        
        # Set header properties
        header = self.assignment_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Level
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Email
        header.setSectionResizeMode(2, QHeaderView.Fixed)             # Delete button
        
        self.assignment_table.setColumnWidth(2, 80)   # Delete button
        
        # Apply styling
        self.assignment_table.setAlternatingRowColors(True)
        self.assignment_table.setSelectionMode(QTableWidget.SingleSelection)
        self.assignment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        main_layout.addWidget(self.assignment_table)
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
        # Initial update from model
        self.update_from_model()
        
    def add_person(self):
        """Add a new person assignment."""
        level = self.level_combo.currentText()
        email = self.email_input.text().strip()
        
        # Validate inputs
        if not email:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter an email address."
            )
            return
            
        # Basic email validation
        if '@' not in email or '.' not in email:
            QMessageBox.warning(
                self,
                "Invalid Email",
                "Please enter a valid email address."
            )
            return
            
        # Add to the model
        success = self.project_model.add_assignment(level, email)
        
        if success:
            # Clear the email input
            self.email_input.clear()
        else:
            QMessageBox.warning(
                self,
                "Duplicate Entry",
                f"A person with email '{email}' is already assigned to the project."
            )
    
    def remove_person(self, row):
        """
        Remove a person assignment.
        
        Args:
            row (int): Row index of the assignment to remove
        """
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to remove this person?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.project_model.remove_assignment(row)
    
    @Slot()
    def update_from_model(self):
        """Update the UI elements from the model data."""
        # Get assignments from the model
        assignments = self.project_model.assignments
        
        # Set row count
        self.assignment_table.setRowCount(len(assignments))
        
        # Populate table
        for row, assignment in enumerate(assignments):
            # Level
            level_item = QTableWidgetItem(assignment["level"])
            self.assignment_table.setItem(row, 0, level_item)
            
            # Email
            email_item = QTableWidgetItem(assignment["email"])
            self.assignment_table.setItem(row, 1, email_item)
            
            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked=False, r=row: self.remove_person(r)
            )
            self.assignment_table.setCellWidget(row, 2, delete_button)