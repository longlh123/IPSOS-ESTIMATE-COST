# ui/dialogs/sample_edit_dialog.py
# -*- coding: utf-8 -*-
"""
Updated dialog for editing a sample row with improved comment handling.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QFormLayout, QGroupBox, QLineEdit,
    QTextEdit, QTabWidget, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from formulars.pricing_formulas import (
    calculate_daily_sup_target
)
from ui.helpers.form_helpers import (create_header_label, create_input_field, create_combobox, create_multiselected_field, create_textedit_field, 
                                     create_radiobuttons_group, create_spinbox_field, create_generic_editor_field
                                     )
from ui.helpers.form_events import (bind_input_handler, bind_combobox_handler, bind_multiselection_handler, bind_textedit_handler, bind_radiogroup_handler, bind_spinbox_handler,
                                    bind_generic_editor_handler
                                    )

class SampleEditDialog(QDialog):

    """
    Dialog for editing a row in the samples table.
    """
    def __init__(self, province, audience_data, price_type, rate_card_target, parent=None):
        super().__init__(parent)
        self.province = province
        self.audience_data = audience_data.copy()
        self.price_type = price_type
        self.rate_card_target = rate_card_target
        
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
        header_label = QLabel(f"<b>Target Audience:</b> {self.audience_data.get('target_audience_name')}")
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
        for spin_box in [self.price_growth_spinbox, self.sample_size_spinbox, 
                         self.target_for_interviewer_spinbox, self.interviewers_per_supervisor_spinbox]:
            # Adjust size properties
            spin_box.setMinimumHeight(28)
            spin_box.setMinimumWidth(100)  # Ensure width is sufficient
    
    def create_pricing_growth_group(self):
        """Create the Price Growth Rate group with its form and comments."""
         # Create a group box for Price Growth Rate

        growth_group = QGroupBox("Price Growth Rate")
        growth_group.setStyleSheet("QGroupBox { background-color: #f8f8f8; }")
        growth_layout = QVBoxLayout(growth_group)
        
        # Price Growth Rate form
        growth_form = QFormLayout()
        
        # Price Growth Rate
        self.price_growth_spinbox = QDoubleSpinBox()
        self.price_growth_spinbox.setRange(-1000.0, 1000.0)
        self.price_growth_spinbox.setValue(self.get_price_growth_rate())
        self.price_growth_spinbox.setSuffix("%")
        self.price_growth_spinbox.setDecimals(1)
        self.price_growth_spinbox.setSingleStep(0.5)
        
        self.price_growth_spinbox.valueChanged.connect(
            lambda value: self.update_price_growth_comment_highlight(
                "price_growth", self.price_growth_comment, value != 0.0
            ))
        
        growth_form.addRow("Price Growth Rate:", self.price_growth_spinbox)

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
        self.price_growth_comment.setText(self.get_price_growth_comment())

        growth_layout.addWidget(self.price_growth_comment)

        return growth_group

    # === Price Growth utilities ===
    def get_price_growth_rate(self) -> float:
        price_item = self.get_current_price_item()

        return price_item.get('price_growth', 0.0) if price_item else 0.0

    def set_price_growth_rate(self, value: float):
        price_item = self.get_current_price_item()

        if price_item:
            price_item['price_growth'] = value

    # === Comment utilities===
    def get_current_price_item(self):
        for price_item in self.audience_data.get('pricing', []):
            if price_item.get('type').lower() == self.price_type.lower():
                return price_item
        return {}
    
    def set_price_growth_comment(self, value: str):
        if value:
            price_item = self.get_current_price_item()

            if price_item:
                price_item.setdefault('comment', {})['price_growth'] = value.strip()
    
    def get_price_growth_comment(self) -> str:
        price_item = self.get_current_price_item()

        return price_item.get('comment', {}).get('price_growth', "") if price_item else ""

    def is_price_growth_comment_required_and_missing(self) -> bool:
        price_item = self.get_current_price_item()

        return (price_item.get('comment', {}).get('price_growth', False) and not self.price_growth_comment.toPlainText().strip()) if price_item else False

    def update_price_growth_comment_highlight(self, key: str, field: QTextEdit, required: bool):
        price_item = self.get_current_price_item()

        if required:
            field.setStyleSheet("background-color: #fff8e1;")
            price_item.setdefault('comment', {})[key] = True
        else:
            field.setStyleSheet("background-color: white;")
            field.setText("")
            price_item.setdefault('comment', {}).pop(key, None)

    def check_comment_required(self):
        if self.is_price_growth_comment_required_and_missing():
            return False, "Price Growth Rate"

        if "target_for_interviewer" in self.audience_data.get('comment', {}) and not self.target_for_interviewer_comment.toPlainText().strip():
            return False, "Target for Interviewer"
        
        if "interviewers_per_supervisor" in self.audience_data.get('comment', {}) and not self.interviewers_per_supervisor_comment.toPlainText().strip():
            return False, "Interviewers per Supervisor"
        
        if "daily_interview_target" in self.audience_data.get('comment', {}) and not self.daily_interview_target_comment.toPlainText().strip():
            return False, "Daily Interview Target"

        return True, ""
    
    def create_sample_group(self):
        sample_group = QGroupBox("Sample Information")
        sample_layout = QVBoxLayout(sample_group)
        
        # Sample info form
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)
        
        sample_size = self.audience_data['sample_size']
        target_for_interviewer = self.audience_data['target']['target_for_interviewer']
        interviewers_per_supervisor = self.audience_data['target']['interviewers_per_supervisor']
        daily_interview_target = self.audience_data['target']['daily_interview_target']
        daily_sup_target = calculate_daily_sup_target(sample_size, target_for_interviewer, interviewers_per_supervisor)

        # Sample Size
        create_spinbox_field(form_layout, self, "sample_size", "Sample Size:", range=(0, 9999), value=sample_size, row=0, col=0)
        
        self.sample_size_spinbox.valueChanged.connect(
            lambda: self.handle_daily_sup_target_changed("sample_size")
        )
        
        #Extra Rate
        create_spinbox_field(form_layout, self, "extra_rate", "Extra Rate:", range=(0, 100), value=self.audience_data['extra_rate'], suffix="%", row=1, col=0)

        self.extra_rate_spinbox.valueChanged.connect(
            lambda: self.handle_daily_sup_target_changed("extra_rate")
        )

        # Target for Interviewer
        create_spinbox_field(form_layout, self, "target_for_interviewer", "Target For Interviewer:", range=(0, 100), value=target_for_interviewer, row=2, col=0)

        self.target_for_interviewer_spinbox.valueChanged.connect(
            lambda value: (
                self.handle_daily_sup_target_changed("target_for_interviewer"),
                self.update_comment_highlight("target_for_interviewer", self.target_for_interviewer_comment, required=value != self.rate_card_target['target_for_interview'])
            ) 
        )

        # Daily Supervisor Target
        create_spinbox_field(form_layout, self, "interviewers_per_supervisor", "Interviewers per Supervisor:", range=(0, 100), value=interviewers_per_supervisor, row=3, col=0)
        
        self.interviewers_per_supervisor_spinbox.valueChanged.connect(
            lambda value: (
                    self.handle_daily_sup_target_changed("interviewers_per_supervisor"),
                    self.update_comment_highlight("interviewers_per_supervisor", self.interviewers_per_supervisor_comment, required=value != self.rate_card_target['interviewers_per_supervisor'])
                )
        )

        # Daily Interview Target
        create_spinbox_field(form_layout, self, "daily_interview_target", "Daily Interview Target:", range=(0, 100), value=daily_interview_target, row=4, col=0)

        self.daily_interview_target_spinbox.valueChanged.connect(
            lambda value: (
                self.update_comment_highlight("daily_interview_target", self.daily_interview_target_comment, required=value != self.rate_card_target['daily_interview_target'])
            )
        )
        
        # Add form layout to sample group
        sample_layout.addLayout(form_layout)
        
        daily_sup_target_layout = QHBoxLayout()
        
        self.daily_sup_target_note = QLabel(f"Daily Sup Target ({sample_size} / {target_for_interviewer} / {interviewers_per_supervisor}): {daily_sup_target}" )
        
        daily_sup_target_layout.addWidget(self.daily_sup_target_note)

        sample_layout.addLayout(daily_sup_target_layout)

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
        self.target_for_interviewer_comment.setText(self.get_audience_comment("target_for_interviewer"))
        
        comment_tabs.addTab(self.target_for_interviewer_comment, "Target for Interviewer")
        
        # Daily SUP Target Comment
        self.interviewers_per_supervisor_comment = QTextEdit()
        self.interviewers_per_supervisor_comment.setPlaceholderText("Enter comment for Interviewers per Supervisor changes...")
        self.interviewers_per_supervisor_comment.setText(self.get_audience_comment("interviewers_per_supervisor"))
        
        comment_tabs.addTab(self.interviewers_per_supervisor_comment, "Interviewers per Supervisor")

        # Daily Interview Target Comment
        self.daily_interview_target_comment = QTextEdit()
        self.daily_interview_target_comment.setPlaceholderText("Enter comment for Daily Interview Target changes...")
        self.daily_interview_target_comment.setText(self.get_audience_comment("daily_interview_target"))

        comment_tabs.addTab(self.daily_interview_target_comment, "Daily Interview Target")
        
        comments_layout.addWidget(comment_tabs)
        sample_layout.addLayout(comments_layout)

        return sample_group

    # === Audience Comment utilities ===
    def set_audience_comment(self, key: str, value: str):
        if value:
            self.audience_data.setdefault('comment', {})[key] = value.strip()

    def get_audience_comment(self, key: str) -> str:
        return self.audience_data.get('comment', {}).get(key, "")
    
    def update_comment_highlight(self, key: str, field: QTextEdit, required: bool):
        if required:
            field.setStyleSheet("background-color: #fff8e1;")
            self.audience_data.setdefault('comment', {})[key] = True
        else:
            field.setStyleSheet("background-color: white;")
            field.setText("")
            self.audience_data.setdefault('comment', {}).pop(key, None)
    
    def handle_daily_sup_target_changed(self, key: str):
        """Update the daily supervisor target value and formula display."""
        sample_size = self.sample_size_spinbox.value()
        target_for_interviewer = self.target_for_interviewer_spinbox.value()
        interviewers_per_supervisor = self.interviewers_per_supervisor_spinbox.value()

        daily_sup_target = calculate_daily_sup_target(sample_size, target_for_interviewer, interviewers_per_supervisor)

        self.daily_sup_target_note.setText(f"Daily Sup Target ({sample_size} / {target_for_interviewer} / {interviewers_per_supervisor}): {daily_sup_target}" )
        
        old_daily_syp_target = self.audience_data.get('target', {}).get('daily_sup_target')

        self.update_comment_highlight("interviewers_per_supervisor", self.interviewers_per_supervisor_comment, daily_sup_target != old_daily_syp_target)

    def validate_and_accept(self):
        """Validate inputs and accept dialog if valid."""
        missing_comments = []
        
        is_value, missing_comment = self.check_comment_required()

        if not is_value:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Missing Comments",
                f"Please provide comments for changes to: {missing_comment}",
                QMessageBox.Ok
            )
            return
        
        # Update data dictionary with new values
        self.set_price_growth_rate(self.price_growth_spinbox.value()) 

        self.audience_data['sample_size'] = self.sample_size_spinbox.value()
        self.audience_data['extra_rate'] = self.extra_rate_spinbox.value()
        self.audience_data['target']['target_for_interviewer'] = self.target_for_interviewer_spinbox.value()
        self.audience_data['target']['interviewers_per_supervisor'] = self.interviewers_per_supervisor_spinbox.value()
        self.audience_data['target']['daily_interview_target'] = self.daily_interview_target_spinbox.value()

        daily_sup_target = calculate_daily_sup_target(self.sample_size_spinbox.value(), self.target_for_interviewer_spinbox.value(), self.interviewers_per_supervisor_spinbox.value())
        
        self.audience_data['target']['daily_sup_target'] = daily_sup_target

        # Only save comments if they exist
        self.set_price_growth_comment(self.price_growth_comment.toPlainText().strip())

        self.set_audience_comment('target_for_interviewer', self.target_for_interviewer_comment.toPlainText().strip())
        self.set_audience_comment('interviewers_per_supervisor', self.interviewers_per_supervisor_comment.toPlainText().strip())
        self.set_audience_comment('daily_interview_target', self.daily_interview_target_comment.toPlainText().strip())
        
        super().accept()
    
    def get_updated_data(self):
        """Return the updated data dictionary."""
        return self.audience_data