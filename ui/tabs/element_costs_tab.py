# ui/tabs/element_costs_tab.py
# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, 
    QLabel, QComboBox, QFileDialog, QMessageBox, QHeaderView,
    QInputDialog, QLineEdit, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QFont
import logging
import os
import pandas as pd
from ui.models.element_costs_table_model import ElementCostsTableModel
from ui.dialogs.bulk_import_dialog import BulkImportDialog
from ui.dialogs.element_cost_edit_dialog import ElementCostEditDialog

class ElementCostsTab(QWidget):
    """Tab for managing element costs."""
    
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        self.current_project_type = None
        self.table_model = ElementCostsTableModel()
        self.logger = logging.getLogger(__name__)
        
        self.init_ui()
        
        # Connect signals
        self.project_model.element_costs.costsChanged.connect(self.update_from_model)

    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Element Costs Management")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setContentsMargins(0, 0, 0, 10)
        
        # Project type controls
        project_controls = QHBoxLayout()
        
        # Project type selector
        self.project_type_label = QLabel("Project Type:")
        self.project_type_combo = QComboBox()
        self.project_type_combo.setMinimumWidth(250)
        self.project_type_combo.currentTextChanged.connect(self.project_type_changed)
        
        # Add/Delete project type buttons
        self.add_type_button = QPushButton("Add Type")
        self.add_type_button.setIcon(QIcon("icons/add.png"))
        self.add_type_button.clicked.connect(self.add_project_type)
        
        self.delete_type_button = QPushButton("Delete Type")
        self.delete_type_button.setIcon(QIcon("icons/delete.png"))
        self.delete_type_button.clicked.connect(self.delete_project_type)
        
        # Add widgets to project controls
        project_controls.addWidget(self.project_type_label)
        project_controls.addWidget(self.project_type_combo)
        project_controls.addWidget(self.add_type_button)
        project_controls.addWidget(self.delete_type_button)
        project_controls.addStretch()
        
        # File operations
        file_controls = QHBoxLayout()
        
        # Import/Export buttons
        self.import_button = QPushButton("Import CSV")
        self.import_button.setIcon(QIcon("icons/import.png"))
        self.import_button.clicked.connect(self.import_csv)
        
        self.bulk_import_button = QPushButton("Bulk Import")
        self.bulk_import_button.setIcon(QIcon("icons/bulk_import.png"))
        self.bulk_import_button.clicked.connect(self.bulk_import)
        
        self.export_button = QPushButton("Export CSV")
        self.export_button.setIcon(QIcon("icons/export.png"))
        self.export_button.clicked.connect(self.export_csv)
        
        # Add buttons to file controls
        file_controls.addWidget(self.import_button)
        file_controls.addWidget(self.bulk_import_button)
        file_controls.addWidget(self.export_button)
        file_controls.addStretch()
        
        # Create a horizontal splitter
        controls_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for project controls
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        left_layout.addLayout(project_controls)
        left_layout.addStretch()
        
        # Right panel for file operations
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        right_layout.addLayout(file_controls)
        right_layout.addStretch()
        
        # Add panels to splitter
        controls_splitter.addWidget(left_panel)
        controls_splitter.addWidget(right_panel)
        controls_splitter.setSizes([500, 500])  # Equal initial sizes
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        # Filter by subtitle
        self.subtitle_label = QLabel("Filter by Subtitle:")
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.setMinimumWidth(250)
        self.subtitle_combo.currentTextChanged.connect(self.filter_by_subtitle)
        
        # Search box
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.textChanged.connect(self.search_costs)
        
        # Reset filters button
        self.reset_filters_button = QPushButton("Reset Filters")
        self.reset_filters_button.clicked.connect(self.reset_filters)
        
        # Add widgets to filter layout
        filter_layout.addWidget(self.subtitle_label)
        filter_layout.addWidget(self.subtitle_combo)
        filter_layout.addWidget(self.search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.reset_filters_button)
        
        # Table view for costs
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(False)
        self.table_view.verticalHeader().setVisible(False)
        
        # Set horizontal header properties
        h_header = self.table_view.horizontalHeader()
        h_header.setStretchLastSection(False)
        h_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Help text
        help_label = QLabel("Double-click on cost values to edit them. Filter by subtitle or use search to find specific items.")
        help_label.setStyleSheet("color: #666; font-style: italic;")
        
        # Add all components to main layout
        main_layout.addWidget(header_label)
        main_layout.addWidget(controls_splitter)
        main_layout.addLayout(filter_layout)
        main_layout.addWidget(self.table_view)
        main_layout.addWidget(help_label)
        
        # Initialize UI state
        self.update_from_model()
        
        self.setup_connections()
        
    @Slot()
    def update_from_model(self):
        """Update UI from model data."""
        # Update project type combo
        current_type = self.project_type_combo.currentText()
        self.project_type_combo.blockSignals(True)
        self.project_type_combo.clear()
        
        project_types = self.project_model.element_costs.get_project_types()
        if project_types:
            self.project_type_combo.addItems(project_types)
            
            # Restore previous selection if possible
            if current_type in project_types:
                self.project_type_combo.setCurrentText(current_type)
            else:
                self.current_project_type = project_types[0]
        
        self.project_type_combo.blockSignals(False)
        
        # Update table with current project type
        self.update_table()
        
        # Update subtitle filter
        self.update_subtitle_filter()
        
    def update_subtitle_filter(self):
        """Update the subtitle filter combo box."""
        current_subtitle = self.subtitle_combo.currentText()
        self.subtitle_combo.blockSignals(True)
        self.subtitle_combo.clear()
        
        # Always add "All Subtitles" option
        self.subtitle_combo.addItem("All Subtitles")
        
        if self.current_project_type:
            subtitles = self.project_model.element_costs.get_subtitles(self.current_project_type)
            if subtitles:
                self.subtitle_combo.addItems(subtitles)
                
                # Restore previous selection if possible
                if current_subtitle in subtitles:
                    self.subtitle_combo.setCurrentText(current_subtitle)
        
        self.subtitle_combo.blockSignals(False)
        
    def update_table(self):
        """Update the table view with current project type data."""
        if not self.current_project_type or self.current_project_type not in self.project_model.element_costs.costs:
            # Clear the table if no valid project type
            self.table_model.setDataFrame(None)
            return
            
        # Get the data for the current project type
        project_cost = self.project_model.element_costs.costs[self.current_project_type]
        
        # Check if this is the new format (dict with "data" key) or old format (directly DataFrame)
        if isinstance(project_cost, dict) and "data" in project_cost:
            df = project_cost["data"].copy()
        else:
            # Fallback for backward compatibility
            df = project_cost.copy()
        
        # Apply any active filters
        df = self.apply_filters(df)
        
        # Update the table model
        self.table_model.setDataFrame(df)
        
        # Optimize column widths
        for i in range(self.table_model.columnCount()):
            self.table_view.resizeColumnToContents(i)
        
    def apply_filters(self, df):
        """Apply active filters to the DataFrame."""
        filtered_df = df
        
        # Apply subtitle filter
        subtitle = self.subtitle_combo.currentText()
        if subtitle and subtitle != "All Subtitles":
            filtered_df = filtered_df[filtered_df["Subtitle 1"] == subtitle]
        
        # Apply search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            # Create a mask for rows that match the search text in any column
            mask = filtered_df.apply(
                lambda row: any(
                    search_text in str(val).lower() 
                    for val in row if pd.notna(val)
                ),
                axis=1
            )
            filtered_df = filtered_df[mask]
        
        return filtered_df
        
    def project_type_changed(self, project_type):
        """Handle project type change."""
        self.current_project_type = project_type
        self.update_table()
        self.update_subtitle_filter()
        
    def filter_by_subtitle(self, subtitle):
        """Handle subtitle filter change."""
        self.update_table()
        
    def search_costs(self, text):
        """Handle search text change."""
        self.update_table()
        
    def reset_filters(self):
        """Reset all filters."""
        self.subtitle_combo.setCurrentIndex(0)  # "All Subtitles"
        self.search_input.clear()
        self.update_table()
        
    def import_csv(self):
        """Import element costs from a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Element Costs",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Import the CSV
        success, message = self.project_model.element_costs.import_csv(file_path)
        
        # Show result message
        if success:
            QMessageBox.information(self, "Import Successful", message)
        else:
            QMessageBox.critical(self, "Import Error", message)
            
    def export_csv(self):
        """Export current project type costs to CSV."""
        if not self.current_project_type:
            QMessageBox.warning(self, "Export Error", "No project type selected.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Element Costs",
            f"{self.current_project_type}_costs.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        # Export the CSV
        success, message = self.project_model.element_costs.export_csv(
            self.current_project_type, file_path
        )
        
        # Show result message
        if success:
            QMessageBox.information(self, "Export Successful", message)
        else:
            QMessageBox.critical(self, "Export Error", message)
            
    def add_project_type(self):
        """Add a new project type."""
        project_type, ok = QInputDialog.getText(
            self,
            "Add Project Type",
            "Enter new project type name:"
        )
        
        if not ok or not project_type:
            return
            
        # Add project type
        success, message = self.project_model.element_costs.add_project_type(project_type)
        
        # Show result message
        if success:
            QMessageBox.information(self, "Add Project Type", message)
            # Select the new project type
            self.project_type_combo.setCurrentText(project_type)
        else:
            QMessageBox.critical(self, "Add Project Type Error", message)
            
    def delete_project_type(self):
        """Delete the current project type."""
        if not self.current_project_type:
            QMessageBox.warning(self, "Delete Error", "No project type selected.")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Project Type",
            f"Are you sure you want to delete the project type '{self.current_project_type}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        # Delete project type
        success, message = self.project_model.element_costs.delete_project_type(self.current_project_type)
        
        # Show result message
        if success:
            QMessageBox.information(self, "Delete Project Type", message)
        else:
            QMessageBox.critical(self, "Delete Project Type Error", message)
            
    def bulk_import(self):
        """Open the bulk import dialog."""
        dialog = BulkImportDialog(self.project_model.element_costs, self)
        dialog.importCompleted.connect(self.handle_bulk_import_completed)
        dialog.exec()
        
    def handle_bulk_import_completed(self, success_count, failure_count, messages):
        """Handle completion of bulk import."""
        self.logger.info(f"Bulk import completed: {success_count} succeeded, {failure_count} failed")
        
        # Update UI
        self.update_from_model()
        
        # Log messages
        for message in messages:
            self.logger.debug(message)

    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect double-click on table to edit cell
        self.table_view.doubleClicked.connect(self.edit_cell)
    
    def edit_cell(self, index):
        """Handle double-click on a cell."""
        # Check if we have a valid project type
        if not self.current_project_type:
            return
            
        # Get the column and data
        column = index.column()
        column_name = self.table_model._data.columns[column]
        
        # Only edit cost columns (L1-L4)
        if not column_name.startswith("L"):
            return
            
        # Get the row data
        row = index.row()
        subtitle_code = self.table_model._data.iloc[row]["Subtitle Code"]
        subtitle_name = self.table_model._data.iloc[row]["Subtitle 1"]
        
        # Open edit dialog
        dialog = ElementCostEditDialog(
            subtitle_code, 
            subtitle_name, 
            self.project_model.element_costs, 
            self.current_project_type,
            self
        )
        
        # Parse the column name to set initial values
        if " " in column_name:
            classification, length = column_name.split(" ", 1)
            dialog.classification_combo.setCurrentText(classification)
            dialog.length_combo.setCurrentText(length.strip("()"))
        
        # Connect the costUpdated signal
        dialog.costUpdated.connect(self.handle_cost_updated)
        
        # Show dialog
        dialog.exec()
        
    def handle_cost_updated(self, subtitle_code, classification, length, value):
        """Handle cost value update from dialog."""
        self.logger.debug(f"Cost updated: {subtitle_code}, {classification}, {length}, {value}")
        
        # Update the table view
        self.update_table()
    