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

class GeneralEditorDialog(QDialog):

    def __init__(self, title, field_config, selected_items, parent=None):
        super().__init__(parent)
        
        self.title = title

        self.selected_items = selected_items.copy()
        self.field_config = field_config.copy()

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
            elif field["widget"] == QComboBox:
                widget = QComboBox()
                options = field.get("options", [])
                widget.addItem("-- Select --")
                widget.addItems(options)
                widget.setCurrentIndex(0)
                widget.model().item(0).setEnabled(False)

            self.widgets[field["name"]] = widget
            grid_layout.addWidget(widget, i, 1)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_entry)
        grid_layout.addWidget(self.add_button, len(self.field_config), 1)

        form_layout_wrapper.addWidget(group_box)
        layout.addWidget(form_container, stretch=0)

        # Right list widget
        self.table = QTableWidget(0, len(self.field_config), self)
        self.table.setHorizontalHeaderLabels([field["label"] for field in self.field_config])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, stretch=1)
    
    def clear_form(self):
        for widget in self.widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)

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

        if not all(entry.values()):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        # Add the entry to the selected items
        self.selected_items.append(entry)

        # Refresh the table to show the new entry
        self.refresh_table()
        # Clear the form for the next entry
        self.clear_form()

    def refresh_table(self):
        self.table.setRowCount(len(self.selected_items))

        for entry in self.selected_items:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for field_name in entry.keys():
                widget = self.widgets[field_name]

                if isinstance(widget, QLineEdit):
                    item = QTableWidgetItem(widget.text().strip())
                elif isinstance(widget, QSpinBox):
                    item = QTableWidgetItem(f'{widget.value():,}')
                self.table.setItem(row_position, i, item)
            
        self.table.resizeColumnsToContents()
        
