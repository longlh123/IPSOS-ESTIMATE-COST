# ui/dialogs/sample_edit_dialog.py
# -*- coding: utf-8 -*-
"""
Updated dialog for editing a sample row with improved comment handling.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QFormLayout, QGroupBox, QLineEdit,
    QTextEdit, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from formulars.pricing_formulas import calculate_daily_sup_target

class SampleEditDialog(QDialog):
    """
    Dialog for editing a row in the samples table.
    """
    def __init__(self, province, audience_data, price_item_data, interviewers_per_supervisor, parent=None):
        super().__init__(parent)
        self.province = province
        self.audience_data = audience_data.copy()
        self.price_item_data = price_item_data
        self.interviewers_per_supervisor = interviewers_per_supervisor
        
        self.setWindowTitle(f"Edit Sample: {self.audience_data.get('sample_type')} - {self.audience_data.get('name')}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add header with province, audience, and sample type
        header_layout = QVBoxLayout()
        header_label = QLabel(f"<b>Province:</b> {province}")
        header_layout.addWidget(header_label)
        header_label = QLabel(f"<b>Target Audience:</b> {self.audience_data.get('name')}")
        header_layout.addWidget(header_label)
        header_label = QLabel(f"<b>Sample Type:</b> {self.audience_data.get('sample_type')}")
        header_layout.addWidget(header_label)
        layout.addLayout(header_layout)
        
        # Create a group box for Price Growth Rate
        pricing_growth_group = self.create_pricing_growth_group()
        layout.addWidget(pricing_growth_group)
        
        # Create a group box for Sample information
        sample_group = self.create_sample_group()
        
        # Add sample group to main layout
        layout.addWidget(sample_group)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set common properties for all spin boxes for better readability and usability
        for spin_box in [self.price_growth, self.sample_size, 
                         self.target_for_interviewer, self.daily_sup_target]:
            # Adjust size properties
            spin_box.setMinimumHeight(28)
            spin_box.setMinimumWidth(100)  # Ensure width is sufficient
        
        self.handle_daily_sup_target_changed()
    
    def create_pricing_growth_group(self):
        """Create the Price Growth Rate group with its form and comments."""
         # Create a group box for Price Growth Rate

        growth_group = QGroupBox("Price Growth Rate")
        growth_group.setStyleSheet("QGroupBox { background-color: #f8f8f8; }")
        growth_layout = QVBoxLayout(growth_group)
        
        # Price Growth Rate form
        growth_form = QFormLayout()
        
        # Price Growth Rate
        self.price_growth = QDoubleSpinBox()
        self.price_growth.setRange(-1000.0, 1000.0)
        self.price_growth.setValue(self.audience_data.get("price_growth", 0.0))
        self.price_growth.setSuffix("%")
        self.price_growth.setDecimals(1)
        self.price_growth.setSingleStep(0.5)
        
        self.price_growth.valueChanged.connect(self.highlight_comment(self.price_growth_comment))

        self.price_growth.valueChanged.connect(lambda: self.comment_required.update({"price_growth": True}))
        
        
        growth_form.addRow("Price Growth Rate:", self.price_growth)

        # Add warning note for price growth rate changes
        self.price_growth_note = QLabel("<i>Note: Changes will apply to all provinces with this target audience</i>")
        self.price_growth_note.setStyleSheet("color: #0066CC;")
        growth_form.addRow("", self.price_growth_note)
        
        # Add price growth comment in the same group
        growth_comment_label = QLabel("Comment for price growth rate changes:")
        growth_layout.addLayout(growth_form)
        growth_layout.addWidget(growth_comment_label)
        
        # Price Growth Comment
        self.price_growth_comment = QTextEdit()
        self.price_growth_comment.setPlaceholderText("Enter comment for price growth rate changes...")
        self.price_growth_comment.setMaximumHeight(60)  # Limit height
        
        if "price_growth" in self.audience_data.get('comment', {}):
            self.price_growth_comment.setText(self.audience_data.get('comment', '').get('price_growth', ''))
        
        growth_layout.addWidget(self.price_growth_comment)

        return growth_group

    def create_sample_group(self):
        sample_group = QGroupBox("Sample Information")
        sample_layout = QVBoxLayout(sample_group)
        
        # Sample info form
        form_layout = QFormLayout()
        
        # Sample Size
        self.sample_size = QSpinBox()
        self.sample_size.setRange(0, 9999)
        self.sample_size.setValue(self.audience_data.get("sample_size", 0))
        
        self.sample_size.valueChanged.connect(self.handle_daily_sup_target_changed)
        
        form_layout.addRow("Sample Size:", self.sample_size)
        
        # Target for Interviewer
        self.target_for_interviewer = QSpinBox()
        self.target_for_interviewer.setRange(1, 99)
        self.target_for_interviewer.setValue(self.audience_data.get("target_for_interviewer", 2))
        self.target_for_interviewer.valueChanged.connect(self.handle_daily_sup_target_changed)
        
        self.target_for_interviewer.valueChanged.connect(self.highlight_interviewer_comment)
        # self.target_for_interviewer.valueChanged.connect(lambda: self.comment_required.update({"interviewer_target": True}))
        
        form_layout.addRow("Target for Interviewer:", self.target_for_interviewer)

        # Daily Supervisor Target
        self.daily_sup_target = QDoubleSpinBox()
        self.daily_sup_target.setValue(self.audience_data.get("daily_sup_target", 0.0))
        self.daily_sup_target.setDecimals(2)
        self.daily_sup_target.setSingleStep(0.1)
        
        self.daily_sup_target.valueChanged.connect(self.check_daily_sup_target_change)

        form_layout.addRow("Daily Target for SUP:", self.daily_sup_target)
        
        # Custom Value indicator
        self.custom_value_label = QLabel()
        self.custom_value_label.setStyleSheet("color: #FF5722; font-style: italic;")
        form_layout.addRow("", self.custom_value_label)
        
        # Daily Supervisor Target Formula
        
        self.formula_label = QLabel()
        form_layout.addRow("Daily Supervisor Target Formula:", self.formula_label)
        
        # Add form layout to sample group
        sample_layout.addLayout(form_layout)
        
        # Comment section for interviewer target and daily SUP target
        comments_layout = QVBoxLayout()
        comments_label = QLabel("Comments:")
        comments_layout.addWidget(comments_label)
        
        # Create a smaller tab widget for comments
        comment_tabs = QTabWidget()
        comment_tabs.setMaximumHeight(80)  # Limit height
        
        # Target for Interviewer Comment
        self.target_for_interviewer_comment = QTextEdit()
        self.target_for_interviewer_comment.setPlaceholderText("Enter comment for Target for Interviewer changes...")
        
        if "target_for_interviewer" in self.audience_data.get('comment', {}):
            self.target_for_interviewer_comment.setText(self.audience_data.get('comment', {}).get('target_for_interviewer', ''))
        
        comment_tabs.addTab(self.target_for_interviewer_comment, "Target for Interviewer")
        
        # Daily SUP Target Comment
        self.daily_sup_target_comment = QTextEdit()
        self.daily_sup_target_comment.setPlaceholderText("Enter comment for custom daily SUP target values...")

        if "daily_sup_target" in self.audience_data.get('comment', {}):
            self.daily_sup_target_comment.setText(self.audience_data.get('comment', {}).get('daily_sup_target', ''))
        
        comment_tabs.addTab(self.daily_sup_target_comment, "Daily SUP Target")
        
        comments_layout.addWidget(comment_tabs)
        sample_layout.addLayout(comments_layout)

        return sample_group

    def handle_daily_sup_target_changed(self):
        """Update the daily supervisor target formula display."""
        sample_size = self.sample_size.value()
        target_for_interviewer = self.target_for_interviewer.value()
        
        # Calculate the formula result
        daily_sup_target = calculate_daily_sup_target(
            sample_size, target_for_interviewer, self.interviewers_per_supervisor
        )
        
        # Create the formula display
        if target_for_interviewer > 0 and self.interviewers_per_supervisor > 0:
            formula = f"{sample_size} / {target_for_interviewer} / {self.interviewers_per_supervisor}"
            formula_text = f"{formula} = {daily_sup_target:.2f}"
        else:
            formula_text = "Cannot calculate (division by zero)"
        
        self.formula_label.setText(formula_text)
        
        # Update the daily supervisor target value if it's not customized
        self.daily_sup_target.setValue(daily_sup_target)
    
    def has_custom_daily_sup_target(self):
        """Check if the daily supervisor target has been customized."""
        # Allow small floating point differences (0.001) to handle precision issues
        return abs(self.daily_sup_target.value() - self.formula_daily_sup_target) > 0.001
    
    def check_daily_sup_target_change(self):
        """Check if the daily supervisor target differs from the formula and update UI."""
        if self.has_custom_daily_sup_target():
            self.custom_value_label.setText("* Custom value - comment required")
            self.audience_data.get('comment', {})["daily_sup_target"] = True
            
            # Highlight the comment tab if needed
            if self.daily_sup_target_comment.toPlainText().strip() == "":
                # No need to switch tabs since they are visible at the same time
                self.daily_sup_target_comment.setStyleSheet("background-color: #fff8e1;")  # Light yellow background
        else:
            self.custom_value_label.setText("")
            if "daily_sup_target" in self.audience_data.get('comment', {}):
                self.audience_data.get('comment', {}).pop("daily_sup_target")
            
            # Reset tab styling
            self.daily_sup_target_comment.setStyleSheet("")
    
    def validate_and_accept(self):
        """Validate inputs and accept dialog if valid."""
        is_valid = True
        missing_comments = []
        
        # Check for required comments
        if "price_growth" in self.audience_data.get('comment', {}) and not self.price_growth_comment.toPlainText().strip():
            missing_comments.append("Price Growth Rate")
            is_valid = False
        
        if "interviewer_target" in self.audience_data.get('comment', {}) and not self.interviewer_target_comment.toPlainText().strip():
            missing_comments.append("Target for Interviewer")
            is_valid = False
        
        if "daily_sup_target" in self.audience_data.get('comment', {}) and not self.daily_sup_target_comment.toPlainText().strip():
            missing_comments.append("Daily Target for SUP")
            is_valid = False
        
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Comments",
                f"Please provide comments for changes to: {', '.join(missing_comments)}",
                QMessageBox.Ok
            )
            return
        
        # Update data dictionary with new values
        self.audience_data['sample_size'] = self.sample_size_spin.value()
        self.audience_data["price_growth"] = self.price_growth_spin.value()
        self.audience_data["target_for_interviewer"] = self.interviewer_target_spin.value()
        self.audience_data["daily_sup_target"] = self.daily_sup_target.value()
        
        # Only save comments if they exist
        price_growth_comment = self.price_growth_comment.toPlainText().strip()
        if price_growth_comment:
            self.audience_data["comment"]["price_growth"] = price_growth_comment
        
        interviewer_target_comment = self.interviewer_target_comment.toPlainText().strip()
        if interviewer_target_comment:
            self.audience_data["comment"]["target_for_interviewer"] = interviewer_target_comment
        
        daily_sup_target_comment = self.daily_sup_target_comment.toPlainText().strip()

        if daily_sup_target_comment:
            self.audience_data["comment"]["daily_sup_target"] = daily_sup_target_comment
        elif "daily_sup_target" in self.audience_data["comment"] and not self.has_custom_daily_sup_target():
            # Remove daily_sup_target comment if it's no longer custom
            del self.audience_data["comment"]["daily_sup_target"]
        
        super().accept()
    
    def highlight_comment(self, comment_field):
        """Highlight the comment field when a value changes."""
        self.price_item_data["comment"]["price_growth"] = True
        comment_field.setStyleSheet("background-color: #fff8e1;")

    def get_updated_data(self):
        """Return the updated data dictionary."""
        return self.audience_data