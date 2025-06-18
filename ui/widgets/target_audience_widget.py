from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QListWidgetItem, QLineEdit, QLabel, QDialog, QDialogButtonBox,
    QCheckBox, QScrollArea, QFrame, QMessageBox, QComboBox, QSpinBox, QGroupBox,
    QGridLayout, QButtonGroup, QRadioButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QCompleter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont

from ui.events.wheelBlocker import WheelBlocker
from config.predefined_values import COMPLEXITY, SAMPLE_TYPES

class TargetAudienceWidget(QWidget):
    
    selectionChanged = Signal(list)
    
    def __init__(self, industries_data, parent=None):
        super().__init__(parent)

        self.industries_data = industries_data
        self.selected_sample_types = []
        self.selected_industries = []
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
            self.selected_audiences,
            self.selected_industries,
            self.selected_sample_types,
            self.industries_data,
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

    def set_selected_sample_types(self, sample_types):
        """Set the selected sample types and update the display."""
        self.selected_sample_types = sample_types

    def set_selected_industries(self, industries):
        """Set the selected industries and update the display."""
        self.selected_industries = industries

    def set_selected_audiences(self, audiences):
        """Set the selected audiences and update the display."""
        self.selected_audiences = audiences
        self.update_display()

    def update_display(self):
        names = list(set([aud["name"] for aud in self.selected_audiences]))
        display = ", ".join(names[:2]) + (f" +{len(names)-2} more" if len(names) > 2 else "")
        self.selection_display.setText(display)

    def set_enabled(self, enable:bool):
        self.selection_display.setEnabled(enable)
        self.select_btn.setEnabled(enable)
    
class TargetAudienceDialog(QDialog):
    
    def __init__(self, selected_audiences, selected_industries, selected_sample_types, industries_data, parent=None):
        super().__init__(parent)
        
        self.selected_industries = selected_industries.copy()
        self.selected_sample_types = selected_sample_types.copy()
        self.industries_data = industries_data.copy()
        self.selected_audiences = selected_audiences.copy()
        self.available_audiences = self.get_available_audiences()

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

        group_box = QGroupBox("Define a new target audience")
        
        form_layout = QGridLayout(group_box)
        form_layout.setColumnStretch(1, 1)  # Stretch the second column to fill available space

        # Row 0 - Sample Type
        form_layout.addWidget(QLabel("Sample Type:"), 0, 0)

        self.sample_type = QComboBox()
        self.sample_type.addItems(self.selected_sample_types)
        self.sample_type.setCurrentIndex(0)

        form_layout.addWidget(self.sample_type, 0, 1)

        # Row 1 - Name
        form_layout.addWidget(QLabel("Target Audience:"), 1, 0)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name...")
        completer = QCompleter(self.available_audiences)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.name_input.setCompleter(completer)

        form_layout.addWidget(self.name_input, 1, 1)

        # Row 2 - Gender
        form_layout.addWidget(QLabel("Gender:"), 2, 0)

        gender_layout = QHBoxLayout()
        
        self.gender_group = QButtonGroup(self)
        
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.both_radio = QRadioButton("Both")
        
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        self.gender_group.addButton(self.both_radio)

        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        gender_layout.addWidget(self.both_radio)
        
        # Set default selection
        self.both_radio.setChecked(True)
        
        gender_widget = QWidget()
        gender_widget.setLayout(gender_layout)

        form_layout.addWidget(gender_widget, 2, 1)

        # Row 3 - Age Group
        form_layout.addWidget(QLabel("Age Group:"), 3, 0)

        age_layout = QHBoxLayout()
        self.age_from = QSpinBox()
        self.age_to = QSpinBox()
        self.age_from.setRange(0, 100)
        self.age_to.setRange(0, 100)
        
        age_layout.addWidget(QLabel("From"))
        age_layout.addWidget(self.age_from)
        age_layout.addWidget(QLabel("To"))
        age_layout.addWidget(self.age_to)
        
        age_widget = QWidget()
        age_widget.setLayout(age_layout)
        
        form_layout.addWidget(age_widget, 3, 1)

        # Row 4 - Income
        form_layout.addWidget(QLabel("Household Income:"), 4, 0)
        
        income_layout = QHBoxLayout()
        self.income_from = QSpinBox()
        self.income_to = QSpinBox()
        self.income_from.setRange(0, 1000000000)
        self.income_to.setRange(0, 1000000000)
        
        income_layout.addWidget(QLabel("From"))
        income_layout.addWidget(self.income_from)
        income_layout.addWidget(QLabel("To"))
        income_layout.addWidget(self.income_to)
        
        income_widget = QWidget()
        income_widget.setLayout(income_layout)
        
        form_layout.addWidget(income_widget, 4, 1)

        # Row 5 - Incident Rate
        form_layout.addWidget(QLabel("Incident Rate (IR):"), 5, 0)
        self.incident_rate = QSpinBox()
        self.incident_rate.setRange(0, 100)
        self.incident_rate.setValue(100)
        form_layout.addWidget(self.incident_rate, 5, 1)

        # Row 6 - Complexity
        form_layout.addWidget(QLabel("Complexity:"), 6, 0)

        self.complexity = QComboBox()
        self.complexity.addItems(COMPLEXITY)
        self.complexity.setCurrentIndex(1)

        form_layout.addWidget(self.complexity, 6, 1)

        # Row 7 - Description
        form_layout.addWidget(QLabel("Description:"), 7, 0)
        self.description_input = QTextEdit()
        form_layout.addWidget(self.description_input, 7, 1)

        # Row 8 - Sample size
        form_layout.addWidget(QLabel("Sample size (for each province):"), 8, 0)
        self.sample_size = QSpinBox()
        self.sample_size.setRange(0, 10000000)
        self.sample_size.setValue(0)
        form_layout.addWidget(self.sample_size, 8, 1)

        # Row 9 - Extra rate (for each province)
        form_layout.addWidget(QLabel("Extra rate (for each province):"), 9, 0)
        self.extra_rate = QSpinBox()
        self.extra_rate.setRange(0, 100)
        self.extra_rate.setValue(0)
        form_layout.addWidget(self.extra_rate, 9, 1)

        # Row 10 - Button
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_target_audience)
        form_layout.addWidget(self.add_btn, 10, 1, alignment=Qt.AlignRight)

        group_box.setLayout(form_layout)
        form_layout_wrapper.addWidget(group_box)

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
    
    def get_avaiable_price(self, audience_name, sample_type):
        for industry in self.selected_industries:
            industry_data = self.industries_data.get(industry, {})

            pricing = industry_data.get("default", {}).get("pricing", {})
            target_for_interviewers = industry_data.get("default", {}).get("target_for_interviewers", 2)

            for product in industry_data.values():
                if isinstance(product, dict) and product.get("target_audience") == audience_name:
                    pricing = product.get("pricing", {})
                    target_for_interviewers = product.get("target_for_interviewers", 2)
                    break
        
        price_info = []
        
        if sample_type == "Pilot":
            price_info = self.make_price_entry(pricing.get("pilot", 0), 100, target_for_interviewers, "pilot")
        elif sample_type == "Non":
            price_info = self.make_price_entry(pricing.get("non", 0), 100, target_for_interviewers, "non")
        elif sample_type == "Main":
            price_info = [
                self.make_price_entry(pricing.get("main", {}).get("recruit", 0), 100, "recruit"),
                self.make_price_entry(pricing.get("main", {}).get("location", 0), 100, "location")
            ]
        elif sample_type == "Booster":
            price_info = [
                self.make_price_entry(pricing.get("booster", {}).get("recruit", 0), 100, "recruit"),
                self.make_price_entry(pricing.get("booster", {}).get("location", 0), 100, "location")
            ]

        return price_info
    
    def make_price_entry(self, price, price_growth, type):
        """Create a price entry dictionary."""
        return {
            "price": price,
            "price_growth": price_growth,
            "type": type,
            "comment": {}
        }

    def get_available_audiences(self):
        audiences = set()

        for industry in self.selected_industries:
            industry_data = self.industries_data.get(industry, {})

            for ta_data in industry_data.values():
                audiences.add(ta_data["target_audience"])
        
        return list(audiences)
    
    def get_available_audience(self, audience_name):
        """Get the ID of an available target audience by name."""
        audience = {}

        for industry in self.selected_industries:
            industry_data = self.industries_data.get(industry, {})

            for key, ta_data in industry_data.items():
                if ta_data["target_audience"] == audience_name:
                    audience = ta_data
                    break
            
            if audience:
                break
        
        return audience
    
    def add_target_audience(self):
        sample_type = self.sample_type.currentText()
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a target audience name.")
            return

        audience_benchmark = self.get_available_audience(name)

        id = audience_benchmark.get("id", None)
        gender = "Male" if self.male_radio.isChecked() else "Female" if self.female_radio.isChecked() else "Both"
        age_range = [self.age_from.value(), self.age_to.value()]
        income_range = [self.income_from.value(), self.income_to.value()]
        incident_rate = self.incident_rate.value()
        complexity = self.complexity.currentText()
        description = self.description_input.toPlainText().strip()
        sample_size = self.sample_size.value()
        extra_rate = self.extra_rate.value()
        pricing = self.get_avaiable_price(name, sample_type)
        target_for_interviewer = audience_benchmark.get("target_for_interviewer", 2)
        daily_sup_target = audience_benchmark.get("daily_sup_target", 0)

        audience_data = {
            "id": id,
            "sample_type": sample_type,
            "name": name,
            "gender": gender,
            "age_range": age_range,
            "income_range": income_range,
            "incident_rate": incident_rate,
            "complexity": complexity,
            "description": description,
            "sample_size": sample_size,
            "extra_rate": extra_rate,
            "pricing": pricing,
            "target_for_interviewer": target_for_interviewer,
            "daily_sup_target": daily_sup_target,
            "comment": {},
        }

        if self.is_duplicate_audience(audience_data):
            QMessageBox.warning(self, "Duplicate Audience", "This target audience already exists.")
            return
        
        self.selected_audiences.append(audience_data)
        self.refresh_table()
        self.clear_form()

    def clear_form(self):
        self.sample_type.setCurrentIndex(0)
        self.name_input.clear()
        self.gender_group.setExclusive(False)
        self.male_radio.setChecked(False)
        self.female_radio.setChecked(False)
        self.both_radio.setChecked(True)
        self.gender_group.setExclusive(True)
        self.age_from.setValue(0)
        self.age_to.setValue(0)
        self.income_from.setValue(0)
        self.income_to.setValue(0)
        self.incident_rate.setValue(100)
        self.complexity.setCurrentIndex(1)
        self.description_input.clear()
        self.sample_size.setValue(0)
        self.extra_rate.setValue(0)

    def refresh_table(self):
        
        self.table.setRowCount(len(self.selected_audiences))

        for i, item in enumerate(self.selected_audiences):
            self.table.setItem(i, 0, QTableWidgetItem(item.get("sample_type", "")))
            self.table.setItem(i, 1, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(i, 2, QTableWidgetItem(item.get("gender", "")))
            self.table.setItem(i, 3, QTableWidgetItem(f"{item.get('age_range', (0, 0))[0]} - {item.get('age_range', (0, 0))[1]}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{item.get('income_range', (0, 0))[0]:,} - {item.get('income_range', (0, 0))[1]:,}"))
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

    def is_duplicate_audience(self, new_data):
        for audience in self.selected_audiences:
            if (
                audience["sample_type"] == new_data["sample_type"]
                and audience["name"].lower() == new_data["name"].lower()
                and audience["gender"] == new_data["gender"]
                and audience["age_range"] == new_data["age_range"]
                and audience["income_range"] == new_data["income_range"]
            ):
                return True
        return False

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