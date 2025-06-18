# ui/widgets/editable_table.py
# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal

class NumericDelegate(QStyledItemDelegate):
    """Delegate for editing numeric values in a table."""
    
    def createEditor(self, parent, option, index):
        """Create a double spin box for editing numeric values."""
        editor = QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(-999999.99)
        editor.setMaximum(999999.99)
        editor.setDecimals(2)
        return editor
        
    def setEditorData(self, editor, index):
        """Set editor data from model."""
        value = index.model().data(index, Qt.EditRole)
        if value and isinstance(value, (int, float, str)):
            try:
                editor.setValue(float(value))
            except (ValueError, TypeError):
                editor.setValue(0.0)
        else:
            editor.setValue(0.0)
            
    def setModelData(self, editor, model, index):
        """Set model data from editor."""
        model.setData(index, editor.value(), Qt.EditRole)

class EditableTable(QTableWidget):
    """Table widget with editing capabilities."""
    
    dataChanged = Signal(int, int, object)  # row, column, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the table UI."""
        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Set up header
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        # Connect signals
        self.itemChanged.connect(self._on_item_changed)
        
    def set_column_delegates(self, numeric_columns):
        """Set delegates for numeric columns."""
        numeric_delegate = NumericDelegate(self)
        for col in numeric_columns:
            self.setItemDelegateForColumn(col, numeric_delegate)
            
    def set_data(self, headers, data, editable_columns=None, numeric_columns=None):
        """Set table data."""
        # Block signals to prevent itemChanged during setup
        self.blockSignals(True)
        
        # Set column count and headers
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Set row count and data
        self.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # Set item flags based on editability
                if editable_columns and col_idx in editable_columns:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                else:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    
                # For numeric columns, set data role for sorting
                if numeric_columns and col_idx in numeric_columns:
                    try:
                        item.setData(Qt.UserRole, float(value))
                    except (ValueError, TypeError):
                        item.setData(Qt.UserRole, 0.0)
                        
                self.setItem(row_idx, col_idx, item)
                
        # Auto-adjust column widths
        self.resizeColumnsToContents()
        
        # Set delegates for numeric columns
        if numeric_columns:
            self.set_column_delegates(numeric_columns)
            
        # Unblock signals
        self.blockSignals(False)
        
    def get_data(self):
        """Get all table data."""
        data = []
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data
        
    def get_selected_row_data(self):
        """Get data from the selected row."""
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None
            
        row_idx = selected_rows[0].row()
        row_data = []
        
        for col in range(self.columnCount()):
            item = self.item(row_idx, col)
            row_data.append(item.text() if item else "")
            
        return row_data
        
    def _on_item_changed(self, item):
        """Handle item changed events."""
        row = item.row()
        col = item.column()
        value = item.text()
        
        # Emit signal with row, column, and new value
        self.dataChanged.emit(row, col, value)