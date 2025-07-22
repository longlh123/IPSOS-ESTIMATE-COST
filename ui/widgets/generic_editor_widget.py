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
from components.validation_field import FieldValidator

class GenericEditorWidget(QWidget):
    selectionChanged = Signal(list)

    def __init__(self, title, field_config, parent=None):
        super().__init__(parent)
        
        self.title = title
        self.field_config = field_config.copy()

        self.selected_items = []

        font = QFont("Arial", 10)
        self.setFont(font)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        #Selected items display
        self.selected_items_input = QLineEdit(self)
        self.selected_items_input.setReadOnly(True)
        self.selected_items_input.setPlaceholderText("Selected items will appear here")
        self.selected_items_input.setFont(QFont("Arial", 10))
        layout.addWidget(self.selected_items_input, 1)

        # Select button
        self.select_button = QPushButton("Select...", self)
        self.select_button.clicked.connect(self.open_selection_dialog)
        layout.addWidget(self.select_button)
    
    def set_enabled(self, enable):
        self.selected_items_input.setEnabled(enable)
        self.select_button.setEnabled(enable)

    def open_selection_dialog(self):
        dialog = GeneralEditorDialog(
            self.title, 
            self.field_config, 
            self.selected_items, 
            self)

        result = dialog.exec_()
        print("Dialog result:", result)

        self.selected_items = dialog.get_selected_items()

        # Emit the selectionChanged signal
        self.selectionChanged.emit(self.selected_items)
    
    def set_selected_items(self, items):
        self.selected_items = items
        self.update_display()

    def update_display(self):
        names = list()

        for item in self.selected_items:
            if 'qc_method' in item.keys():
                names.append(item.get('qc_method', ""))
            if 'cost_type' in item.keys():
                names.append(item.get('cost_type', ""))
            if all(k in item.keys() for k in ['sample_type', 'sampling_method']):
                names.append(f"{item.get('sample_type', '')} [{item.get('sampling_method', '')}]")

        names = list(set(names))
        display = ", ".join(names[:4]) + (f" +{len(names)-4} more" if len(names) > 4 else "")
        self.selected_items_input.setText(display)

class GeneralEditorDialog(QDialog):

    def __init__(self, title, field_config, selected_items, parent=None):
        super().__init__(parent)
        
        self.title = title

        self.selected_items = selected_items.copy()
        self.field_config = field_config.copy()

        self.validator = FieldValidator()

        self.widgets = {}

        self.setWindowTitle(self.title)
        self.setMinimumWidth(1200)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Left list widget
        form_container = QWidget()
        form_container.setFixedWidth(500)
        form_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        form_layout_wrapper = QVBoxLayout(form_container)

        group_box = QGroupBox("Defined a New " + self.title)

        grid_layout = QGridLayout(group_box)
        grid_layout.setColumnStretch(1, 1)

        for i, field in enumerate(self.field_config):
            label = QLabel(field["label"])
            grid_layout.addWidget(label, i, 0)

            if field["widget"] == QLineEdit:
                widget = QLineEdit()
            elif field["widget"] == QSpinBox:
                widget = QSpinBox()
                widget.setRange(field.get("min", 0), field.get("max", 100))
                widget.setSuffix(field.get('suffix', ''))
            elif field["widget"] == QComboBox:
                widget = QComboBox()
                options = field.get("options", [])
                widget.addItem("-- Select --")
                widget.addItems(options)
                widget.setCurrentIndex(0)
                widget.model().item(0).setEnabled(False)
            elif field["widget"] == QTextEdit:
                widget = QTextEdit()

            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            container_layout.addWidget(widget)

            warning_label = QLabel("")
            warning_label.setStyleSheet("color: red; font-size: 12px")
            warning_label.setVisible(False)

            container_layout.addWidget(warning_label)

            setattr(self, f'{field["name"]}_warning', warning_label)

            self.widgets[field["name"]] = widget
            grid_layout.addWidget(container, i, 1)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)
        grid_layout.addWidget(self.add_button, len(self.field_config), 1)

        form_layout_wrapper.addWidget(group_box)
        layout.addWidget(form_container, stretch=0)

        # Right list widget
        self.table = QTableWidget(0, len(self.field_config) + 1, self)
        self.table.setHorizontalHeaderLabels([field["label"] for field in self.field_config])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=1)

        self.refresh_table()
    
    def clear_form(self):
        for widget in self.widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QTextEdit):
                widget.clear()

    def get_selected_items(self):
        return self.selected_items

    def add_entry(self):
        entry = {}

        for field in self.field_config:
            widget = self.widgets[field["name"]]

            if isinstance(widget, QLineEdit):
                entry[field["name"]] = widget.text().strip()
            elif isinstance(widget, QSpinBox):
                entry[field["name"]] = widget.value()
            elif isinstance(widget, QComboBox):
                entry[field["name"]] = widget.currentText()
            elif isinstance(widget, QTextEdit):
                entry[field["name"]] = widget.toPlainText().strip()

        if self.validate(entry):
            # Add the entry to the selected items
            self.selected_items.append(entry)

            # Refresh the table to show the new entry
            self.refresh_table()
            # Clear the form for the next entry
            self.clear_form()

    def validate(self, new_item):
        
        for field in self.field_config:
            field_name = field.get('name', '')
            label = field.get('label', '')
            required = field.get('required', False)
            min_range = field.get('min_range', None)

            if required:
                widget = self.widgets[field_name]

                value = new_item.get(field_name)
                warning_label = getattr(self, f'{field_name}_warning', None)

                if warning_label:
                    warning_label.hide()
                
                if isinstance(widget, QLineEdit) and not value.strip():
                    if warning_label:
                        warning_label.setText(f"{label} should not be blank.")
                        warning_label.show()
                    return False
                elif isinstance(widget, QComboBox) and value == '-- Select --':
                    if warning_label:
                        warning_label.setText(f"{label} is required.")
                        warning_label.show()
                    return False
                elif isinstance(widget, QSpinBox) and min_range is not None:
                    if value < min_range:
                        if warning_label:
                            warning_label.setText(f"{label} must be >= {field['min_range']}.")
                            warning_label.show()
                        return False

        # 2. Kiểm tra trùng lặp
        duplicated_fields = [f['name'] for f in self.field_config if f.get('duplicated')]

        if duplicated_fields and self.selected_items:
            
            for item in self.selected_items:
                if all(
                    [new_item.get(f_name) == item.get(f_name) for f_name in duplicated_fields]
                ):
                    field_name = duplicated_fields[0]
                    warning_label = getattr(self, f'{field_name}_warning', None)
                    
                    if warning_label:
                        warning_label.setText("Duplicated item detected.")
                        warning_label.show()
                    return False

        return True
    
    def refresh_table(self):
        self.table.setRowCount(len(self.selected_items))

        for row_index, entry in enumerate(self.selected_items):
            for col_index, field_name in enumerate([field["name"] for field in self.field_config]):
                widget = self.widgets[field_name]

                if isinstance(widget, QLineEdit):
                    item = QTableWidgetItem(entry.get(field_name, "").strip())
                elif isinstance(widget, QSpinBox):
                    item = QTableWidgetItem(f'{entry.get(field_name, 0):,}')
                elif isinstance(widget, QComboBox):
                    item = QTableWidgetItem(f'{entry.get(field_name, "")}')
                elif isinstance(widget, QTextEdit):
                    item = QTableWidgetItem(entry.get(field_name, "").strip())

                self.table.setItem(row_index, col_index, item)

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
            btn.clicked.connect(lambda _, row=row_index: self.delete_row(row))

            # Bọc button bằng container với layout
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(5, 2, 5, 2)  # left, top, right, bottom (khoảng cách từ button đến mép cell)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(btn)

            self.table.setCellWidget(row_index, col_index + 1, container)
            
        self.table.resizeColumnsToContents()
    
    def delete_row(self, index):
        del self.selected_items[index]
        self.refresh_table()
    
    def accept(self):
        if len(self.selected_items) > 0:
            QMessageBox.warning(self, "Validation Error", "You must add at least one valid item.")
            return
        super().accept()
    
