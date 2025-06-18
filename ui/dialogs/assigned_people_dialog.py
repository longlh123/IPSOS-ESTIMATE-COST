# ui/dialogs/assigned_people_dialog.py
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox,
    QLabel, QHeaderView, QCheckBox, QTableWidgetItem
)
from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QTableWidget
)

class AssignedPeopleDialog(QDialog):
    """Dialog for selecting people to assign to travel."""
    
    def __init__(self, available_people, selected_people, parent=None):
        super().__init__(parent)
        self.available_people = available_people
        self.selected_people = selected_people.copy()  # Make a copy to avoid modifying original
        
        self.setWindowTitle("Select People for Travel")
        self.setMinimumSize(400, 300)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select people to assign for travel:")
        layout.addWidget(instructions)
        
        # Table of people with checkboxes
        self.people_table = QTableWidget()
        self.people_table.setColumnCount(3)  # Checkbox, Level, Email
        self.people_table.setHorizontalHeaderLabels(["", "Level", "Email"])
        
        # Set column properties
        header = self.people_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Level
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Email
        
        # Populate table
        self.populate_table()
        
        layout.addWidget(self.people_table)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
    def populate_table(self):
        """Populate the table with available people."""
        self.people_table.setRowCount(len(self.available_people))
        
        for row, person in enumerate(self.available_people):
            # Create checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(person["email"] in self.selected_people)
            
            # Create a container for the checkbox to center it
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.addWidget(checkbox)
            
            # Store the person's email as a property of the checkbox
            checkbox.setProperty("email", person["email"])
            
            # Connect state changed signal
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            
            # Add to table
            self.people_table.setCellWidget(row, 0, checkbox_widget)
            
            # Level
            level_item = QTableWidgetItem(person["level"])
            self.people_table.setItem(row, 1, level_item)
            
            # Email
            email_item = QTableWidgetItem(person["email"])
            self.people_table.setItem(row, 2, email_item)
            
    def on_checkbox_changed(self, state):
        """Handle checkbox state change."""
        # Get the checkbox that sent the signal
        checkbox = self.sender()
        if not checkbox:
            return
            
        # Get the email associated with this checkbox
        email = checkbox.property("email")
        if not email:
            return
            
        # Update selected_people list
        if state == Qt.Checked:
            if email not in self.selected_people:
                self.selected_people.append(email)
        else:
            if email in self.selected_people:
                self.selected_people.remove(email)
                
    def get_selected_people(self):
        """Get the list of selected people emails."""
        # Double check to make sure list is accurate
        selected = []
        
        # Iterate through table to find checked boxes
        for row in range(self.people_table.rowCount()):
            checkbox_widget = self.people_table.cellWidget(row, 0)
            if checkbox_widget:
                # The checkbox is the first child of the widget
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox and checkbox.isChecked():
                    email = checkbox.property("email")
                    if email:
                        selected.append(email)
                        
        return selected