import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QListWidgetItem, QLineEdit, QLabel, QDialog, QDialogButtonBox,
    QCheckBox, QScrollArea, QFrame, QMessageBox, QComboBox, QSpinBox, QGroupBox,
    QGridLayout, QButtonGroup, QRadioButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QCompleter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont

from ui.events.wheelBlocker import WheelBlocker
from config.predefined_values import COMPLEXITY, SAMPLE_TYPES
from components.validation_field import FieldValidator
from ui.helpers.form_helpers import (create_header_label, create_input_field, create_combobox, create_multiselected_field, create_textedit_field, 
                                     create_radiobuttons_group, create_spinbox_field
                                     )
from ui.helpers.form_events import (bind_input_handler, bind_combobox_handler, bind_multiselection_handler, bind_textedit_handler, bind_radiogroup_handler, bind_spinbox_handler,
                                    bind_generic_editor_handler
                                    )

class TargetAudienceWidget(QWidget):
    
    selectionChanged = Signal(list)
    
    def __init__(self, project_model, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.project_model = project_model
        self.selected_audiences = []

        font = QFont("Arial", 10)
        self.setFont(font)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Selected items display
        self.selection_display = QLineEdit()
        self.selection_display.setReadOnly(True)
        self.selection_display.setFont(QFont("Arial", 10))
        layout.addWidget(self.selection_display, 1)
        
        # Select button
        self.select_btn = QPushButton("Select...")
        self.select_btn.clicked.connect(self.show_selection_dialog)
        layout.addWidget(self.select_btn)
    
    def show_selection_dialog(self):
        """Show the dialog for selecting items."""
        # Create dialog with current selections
        dialog = TargetAudienceDialog(
            self.project_model,
            self.selected_audiences,
            self
        )

        # Execute the dialog
        result = dialog.exec()
        print(f"Dialog result: {result}, Accepted: {result == QDialog.Accepted}")
        
        # If the dialog was accepted, update the selected audiences
        self.selected_audiences = dialog.get_selected_audiences()
        
        self.update_display()

        # Emit the selection changed signal
        self.selectionChanged.emit(self.selected_audiences)

    def set_selected_audiences(self, audiences):
        """Set the selected audiences and update the display."""
        self.selected_audiences = audiences
        self.update_display()

    def update_display(self):
        names = list(set([aud["target_audience_name"] for aud in self.selected_audiences]))
        display = ", ".join(names[:4]) + (f" +{len(names)-4} more" if len(names) > 4 else "")
        self.selection_display.setText(display)

    def set_enabled(self, enable:bool):
        self.selection_display.setEnabled(enable)
        self.select_btn.setEnabled(enable)
    
class TargetAudienceDialog(QDialog):
    
    def __init__(self, project_model, selected_audiences, parent=None):
        super().__init__(parent)
        
        self.validator = FieldValidator()
        self.validate_widgets = dict()

        self.project_model = project_model
        self.selected_audiences = selected_audiences.copy()


        self.setWindowTitle("Manage Target Audiences")
        self.setMinimumWidth(1200)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self) 
        
        # --- Left side: Form input ---
        form_container = QWidget()
        form_container.setFixedWidth(500)
        form_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        form_layout_wrapper = QVBoxLayout(form_container)

        self.group_box = QGroupBox("Define a new target audience")
        
        form_layout = QGridLayout(self.group_box)
        form_layout.setColumnStretch(1, 1)  # Stretch the second column to fill available space

        # Sample Type
        create_combobox(form_layout, self, "sample_type", "Sample Type:", self.project_model.get_sample_types(), row=0, col=0)

        bind_combobox_handler(self, "sample_type", validator_func=self.validator.target_audience_validate)

        self.validate_widgets["sample_type"] = self.sample_type_combobox

        # Industry Name
        create_combobox(form_layout, self, "industry_name", "Industry:", self.project_model.general.get('industries'), row=1, col=0)

        bind_combobox_handler(self, "industry_name", validator_func=self.validator.target_audience_validate)

        self.industry_name_combobox.currentTextChanged.connect(self.on_industry_changed)

        self.validate_widgets["industry_name"] = self.industry_name_combobox

        # Target Audience Name
        create_input_field(form_layout, self, "target_audience_name", "Target Audience", row=2, col=0)

        bind_input_handler(self, "target_audience_name", validator_func=self.validator.target_audience_validate)

        self.validate_widgets["target_audience_name"] = self.target_audience_name_input

        # Row 2 - Gender
        gender_items = [
            { 'name': 'male', 'label': 'Male', 'checked': False},
            { 'name': 'female', 'label': 'Female', 'checked': False},
            { 'name': 'both', 'label': 'Both', 'checked': True}
        ]

        create_radiobuttons_group(form_layout, self, "gender", "Gender:", gender_items, row=3, col=0)
        
        # Row 3 - Age Group
        age_group_label = QLabel("Age Group:")
        age_group_label.setStyleSheet("margin-left: 10px;")

        form_layout.addWidget(age_group_label, 4, 0)

        age_group_layout = QGridLayout()
        age_group_layout.setColumnStretch(1, 1)
        age_group_layout.setColumnStretch(1, 3)

        create_spinbox_field(age_group_layout, self, "age_from", "From:", range=(0, 100), row=0, col=0)
        create_spinbox_field(age_group_layout, self, "age_to", "To:", range=(0, 100), row=0, col=2)

        form_layout.addLayout(age_group_layout, 4, 1)

        # Income
        househole_income = QLabel("Household Income:")
        househole_income.setStyleSheet("margin-left: 10px;")

        form_layout.addWidget(househole_income, 5, 0)
        
        household_income_layout = QGridLayout()
        household_income_layout.setColumnStretch(1, 1)
        household_income_layout.setColumnStretch(1, 3)

        create_spinbox_field(household_income_layout, self, "household_income_from", "From:", range=(0, 100), row=0, col=0)
        create_spinbox_field(household_income_layout, self, "household_income_to", "To:", range=(0, 100), row=0, col=2)

        form_layout.addLayout(household_income_layout, 5, 1)

        # Incident Rate
        create_spinbox_field(form_layout, self, "incident_rate", "Incident Rate (IR):", range=(0, 100), value=100, suffix="%", row=6, col=0)

        # Complexity
        create_combobox(form_layout, self, "complexity", "Complexity:", COMPLEXITY, current_index=1, row=7, col=0)

        # Description
        create_textedit_field(form_layout, self, "description", "Description:", row=8, col=0, rowspan=1, colspan=2)

        # Sample size
        create_spinbox_field(form_layout, self, "sample_size", "Sample size (for each province):", range=(0, 10000), value=0, row=10, col=0)

        # Extra rate (for each province)
        create_spinbox_field(form_layout, self, "extra_rate", "Extra rate (for each province):", range=(0, 100), value=0, suffix="%", row=11, col=0)

        # Button
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_target_audience)
        form_layout.addWidget(self.add_btn, 12, 1, alignment=Qt.AlignRight)

        self.group_box.setLayout(form_layout)
        form_layout_wrapper.addWidget(self.group_box)

        # --- Right side: Table ---
        self.table = QTableWidget(0, 11)  # Cần 9 cột vì có thêm "Actions"
        self.table.setWordWrap(True) # Cho phép wrap toàn bảng

        self.table.setHorizontalHeaderLabels([
            "Sample Type", "Name", "Gender", "Age", "Income", "IR",
            "Complexity", "Sample Size", "Extra Rate", "Description", "Actions"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)

        # --- Add both sides to main layout ---
        main_layout.addWidget(form_container, stretch=0)
        main_layout.addWidget(self.table, stretch=1)

        self.wheel_blocker = WheelBlocker()

        # Apply filter cho tất cả các QComboBox và QSpinBox trong form
        for widget in main_layout.findChildren(QSpinBox) + main_layout.findChildren(QComboBox):
            widget.installEventFilter(self.wheel_blocker)

        self.refresh_table()
    
    def on_industry_changed(self, industry_name):
        audiences = self.project_model.get_audiences(industry_name)

        model = QStringListModel(audiences)
        
        completer = QCompleter()
        completer.setModel(model)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.target_audience_name_input.setCompleter(completer)
        self.target_audience_name_input.resize(400, 30)
        self.target_audience_name_input.show()

    def validate(self):
        for key, widget in self.validate_widgets.items():
            if isinstance(widget, QComboBox):
                is_valid, error_message = self.validator.target_audience_validate(key, widget.currentText())
            elif isinstance(widget, QLineEdit):
                is_valid, error_message = self.validator.target_audience_validate(key, widget.text().strip())

            warning_label = getattr(self, f"{key}_warning")

            if not is_valid:
                warning_label.setText(error_message)
                warning_label.show()

                return is_valid, error_message
            else:
                warning_label.setText("")
                warning_label.hide()

        return True, ""

    def get_gender(self):
        if self.male_radioitem.isChecked():
            return "Male"
        elif self.female_radioitem.isChecked():
            return "Female"
        else:
            return "Both"
    
    def get_age_group(self):
        value_from = self.age_from_spinbox.value()
        value_to = self.age_to_spinbox.value()
        return (value_from, value_to)
    
    def get_household_income(self):
        value_from = self.household_income_from_spinbox.value()
        value_to = self.household_income_to_spinbox.value()
        return (value_from, value_to)

    def make_audience_entry(self):
        return {
            "sample_type": self.sample_type_combobox.currentText(),
            "industry_name": self.industry_name_combobox.currentText(),
            "target_audience_name": self.target_audience_name_input.text().strip(),
            "gender": self.get_gender(),
            "age_group": self.get_age_group(),
            "household_income": self.get_household_income(),
            "description": self.description_textedit.toPlainText().strip(),
            "incident_rate": self.incident_rate_spinbox.value(),
            "complexity": self.complexity_combobox.currentText(),
            "sample_size": self.sample_size_spinbox.value(),
            "extra_rate": self.extra_rate_spinbox.value()
        }

    def is_duplicate_audience(self, new_data):
        for audience in self.selected_audiences:
            if (
                audience["sample_type"] == new_data["sample_type"]
                and audience["industry_name"].lower() == new_data["industry_name"].lower()
                and audience["target_audience_name"].lower() == new_data["target_audience_name"].lower()
                and audience["gender"] == new_data["gender"]
                and audience["age_group"] == new_data["age_group"]
                and audience["household_income"] == new_data["household_income"]
            ):
                return True
        return False
    
    def add_target_audience(self):
        
        is_valid, error_message = self.validate()
        
        if is_valid:
            new_audiance_data = self.make_audience_entry()
            
            if self.is_duplicate_audience(new_audiance_data):
                QMessageBox.warning(self, "Duplicate Audience", "This target audience already exists.")
                return
            
            selected_audience = self.project_model.get_audience(new_audiance_data)

            self.selected_audiences.append(selected_audience)
            self.refresh_table()
            self.clear_form()

    def clear_form(self):
        self.sample_type_combobox.setCurrentIndex(0)
        self.industry_name_combobox.setCurrentIndex(0)
        self.target_audience_name_input.clear()
        self.gender_radiogroup.setExclusive(False)
        self.male_radioitem.setChecked(False)
        self.female_radioitem.setChecked(False)
        self.both_radioitem.setChecked(True)
        self.gender_radiogroup.setExclusive(True)
        self.age_from_spinbox.setValue(0)
        self.age_to_spinbox.setValue(0)
        self.household_income_from_spinbox.setValue(0)
        self.household_income_to_spinbox.setValue(0)
        self.incident_rate_spinbox.setValue(100)
        self.complexity_combobox.setCurrentIndex(1)
        self.description_textedit.clear()
        self.sample_size_spinbox.setValue(0)
        self.extra_rate_spinbox.setValue(0)

        for key, widget in self.validate_widgets.items():
            warning_label = getattr(self, f"{key}_warning")

            warning_label.setText("")
            warning_label.hide()

    def refresh_table(self):
        
        self.table.setRowCount(len(self.selected_audiences))

        for i, item in enumerate(self.selected_audiences):
            self.table.setItem(i, 0, QTableWidgetItem(item.get("sample_type", "")))
            self.table.setItem(i, 1, QTableWidgetItem(item.get("target_audience_name", "")))
            self.table.setItem(i, 2, QTableWidgetItem(item.get("gender", "")))
            self.table.setItem(i, 3, QTableWidgetItem(f"{item.get('age_group', (0, 0))[0]} - {item.get('age_group', (0, 0))[1]}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{item.get('household_income', (0, 0))[0]:,} - {item.get('household_income', (0, 0))[1]:,}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{item.get('incident_rate', 100)}%"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{item.get('complexity', '')}"))
            self.table.setItem(i, 7, QTableWidgetItem(f"{item.get('sample_size', 0):,}"))
            self.table.setItem(i, 8, QTableWidgetItem(f"{item.get('extra_rate', 0)}%"))
            self.table.setItem(i, 9, QTableWidgetItem(item.get("description", "")))
            
            btn = QPushButton("Delete")
            btn.setStyleSheet(""" 
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 4px;
                    padding: 4px 8px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #1a5276;
                }
            """)
            btn.clicked.connect(lambda _, row=i: self.delete_row(row))

            # Bọc button bằng container với layout
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 2, 5, 2)  # left, top, right, bottom (khoảng cách từ button đến mép cell)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(btn)

            self.table.setCellWidget(i, 10, container)

        self.table.resizeColumnsToContents()

    def delete_row(self, index):
        del self.selected_audiences[index]
        self.refresh_table()

    def get_selected_audiences(self):
        return self.selected_audiences

    def accept(self):
        # Cập nhật lại selected_audiences từ các checkbox, list, etc.
        self.selected_audiences = self.collect_selected_items()
        super().accept()

    def resize_rows_to_contents(self):
        """Resize rows to fit content better, especially for rows with comments."""
        for row in range(self.rowCount()):
            comment_item = self.item(row, 6)
            if comment_item and comment_item.text():
                # Increase row height for rows with comments to make them more visible
                self.setRowHeight(row, 60)  # Fixed increased height for comment rows
            else:
                # Default height for rows without comments
                self.setRowHeight(row, self.verticalHeader().defaultSectionSize())