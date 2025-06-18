# ui/dialogs/element_cost_edit_dialog.py
# -*- coding: utf-8 -*-
"""
Dialog for editing a single element cost.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal

class ElementCostEditDialog(QDialog):
    """Dialog for editing a single element cost."""
    
    costUpdated = Signal(str, str, str, float)  # subtitle_code, classification, interval, new_value
    
    def __init__(self, subtitle_code, subtitle_name, element_costs_model, project_type, parent=None):
        super().__init__(parent)
        self.subtitle_code = subtitle_code
        self.subtitle_name = subtitle_name
        self.element_costs_model = element_costs_model
        self.project_type = project_type
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Dialog properties
        self.setWindowTitle("Edit Element Cost")
        self.setMinimumWidth(500)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Element info
        info_group = QGroupBox("Element Information")
        info_layout = QFormLayout(info_group)
        
        self.subtitle_code_edit = QLineEdit(str(self.subtitle_code))
        self.subtitle_code_edit.setReadOnly(True)
        
        self.subtitle_name_edit = QLineEdit(self.subtitle_name)
        self.subtitle_name_edit.setReadOnly(True)
        
        info_layout.addRow("Subtitle Code:", self.subtitle_code_edit)
        info_layout.addRow("Subtitle Name:", self.subtitle_name_edit)
        
        main_layout.addWidget(info_group)
        
        # Cost editor
        cost_group = QGroupBox("Cost Values")
        cost_layout = QFormLayout(cost_group)
        
        # Classification selection
        self.classification_combo = QComboBox()
        self.classification_combo.addItems(["L1", "L2", "L3", "L4"])
        self.classification_combo.currentTextChanged.connect(self.update_cost_value)
        
        # Interview length selection
        self.length_combo = QComboBox()
        self.length_combo.addItems(["<15 min", "15-30 min", "30-45 min", "45-60 min"])
        self.length_combo.currentTextChanged.connect(self.update_cost_value)
        
        # Cost input
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 1000000000)  # 0 to 1 billion
        self.cost_spin.setDecimals(2)
        self.cost_spin.setSingleStep(1000)
        self.cost_spin.setPrefix("")
        self.cost_spin.setSuffix(" VND")
        
        cost_layout.addRow("Classification:", self.classification_combo)
        cost_layout.addRow("Interview Length:", self.length_combo)
        cost_layout.addRow("Cost Value:", self.cost_spin)
        
        main_layout.addWidget(cost_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_cost)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Initialize with current value
        self.update_cost_value()
        
    def update_cost_value(self):
        """Update the cost spin box with the current value."""
        classification = self.classification_combo.currentText()
        length = self.length_combo.currentText()
        
        # Get the current value from the model
        df = self.element_costs_model.costs.get(self.project_type)
        if df is not None:
            # Find the row with matching subtitle code
            matching_rows = df[df["Subtitle Code"] == self.subtitle_code]
            if not matching_rows.empty:
                # Get the column name
                column = f"{classification} ({length})"
                if column in df.columns:
                    # Get the value
                    value = matching_rows.iloc[0][column]
                    # Update the spin box
                    self.cost_spin.setValue(value)
                    return
        
        # If we get here, either the value wasn't found or there was an error
        self.cost_spin.setValue(0)
        
    def save_cost(self):
        """Save the updated cost value."""
        classification = self.classification_combo.currentText()
        length = self.length_combo.currentText()
        value = self.cost_spin.value()
        
        # Find the interview length in minutes
        if length == "<15 min":
            length_minutes = 10  # Use mid-point
        elif length == "15-30 min":
            length_minutes = 22  # Use mid-point
        elif length == "30-45 min":
            length_minutes = 37  # Use mid-point
        else:  # "45-60 min"
            length_minutes = 52  # Use mid-point
        
        # Update the model
        success = self.element_costs_model.update_cost(
            self.project_type,
            self.subtitle_code,
            classification,
            length_minutes,
            value
        )
        
        if success:
            # Emit signal
            self.costUpdated.emit(
                str(self.subtitle_code),
                classification,
                length,
                value
            )
            
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Update Error",
                f"Failed to update cost value for {classification} ({length})."
            )