# ui/models/element_costs_table_model.py
# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
import logging

class ElementCostsTableModel(QAbstractTableModel):
    """Table model for displaying and editing element costs."""
    
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
        self.logger = logging.getLogger(__name__)
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns) if not self._data.empty else 0
        
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self._data.empty:
            return None
            
        value = self._data.iloc[index.row(), index.column()]
        
        if role == Qt.DisplayRole:
            # Format numeric values with commas and 2 decimal places for cost columns
            col_name = self._data.columns[index.column()]
            if col_name.startswith("L") and pd.notna(value):
                return f"{value:,.2f}" if isinstance(value, (int, float)) else str(value)
            return "" if pd.isna(value) else str(value)
        
        elif role == Qt.TextAlignmentRole:
            # Align numbers to the right, text to the left
            col_name = self._data.columns[index.column()]
            if col_name.startswith("L"):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter
            
        return None
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(section + 1)
                
        return None
        
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            try:
                col_name = self._data.columns[index.column()]
                
                # Only allow editing cost columns
                if not col_name.startswith("L"):
                    return False
                
                # Convert value to float for cost columns
                try:
                    # Remove commas and convert to float
                    clean_value = value.replace(',', '')
                    float_value = float(clean_value)
                    
                    # Update the data
                    self._data.iloc[index.row(), index.column()] = float_value
                    
                    # Emit dataChanged signal
                    self.dataChanged.emit(index, index)
                    return True
                except ValueError:
                    self.logger.warning(f"Invalid value: {value} for column {col_name}")
                    return False
            except Exception as e:
                self.logger.error(f"Error setting data: {e}")
                return False
                
        return False
        
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
            
        # Make only cost columns editable
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
        col_name = self._data.columns[index.column()]
        if col_name.startswith("L"):
            flags |= Qt.ItemIsEditable
            
        return flags
    
    def setDataFrame(self, df):
        """Update the model with a new DataFrame."""
        self.beginResetModel()
        self._data = df.copy() if df is not None else pd.DataFrame()
        self.endResetModel()