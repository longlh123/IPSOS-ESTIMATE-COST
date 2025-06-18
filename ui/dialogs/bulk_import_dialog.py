# ui/dialogs/bulk_import_dialog.py
# -*- coding: utf-8 -*-
"""
Dialog for bulk importing element costs from multiple CSV files.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QFileDialog, QProgressBar, QMessageBox,
    QFrame, QSplitter, QApplication
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

import os
from utils.element_costs_importer import ElementCostsImporter

class BulkImportDialog(QDialog):
    """Dialog for bulk importing element costs from multiple CSV files."""
    
    importCompleted = Signal(int, int, list)  # success_count, failure_count, messages
    
    def __init__(self, element_costs_model, parent=None):
        super().__init__(parent)
        self.element_costs_model = element_costs_model
        self.importer = ElementCostsImporter()
        self.selected_files = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Dialog properties
        self.setWindowTitle("Bulk Import Element Costs")
        self.setMinimumSize(600, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Import Element Costs from Multiple CSV Files")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Instructions
        instructions = QLabel(
            "Select individual CSV files or a directory containing CSV files to import. "
            "Each file should contain element costs for a single project type."
        )
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        
        # Buttons frame
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        
        self.add_files_button = QPushButton("Add Files...")
        self.add_files_button.clicked.connect(self.add_files)
        
        self.add_directory_button = QPushButton("Add Directory...")
        self.add_directory_button.clicked.connect(self.add_directory)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_files)
        
        buttons_layout.addWidget(self.add_files_button)
        buttons_layout.addWidget(self.add_directory_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        
        file_layout.addWidget(self.file_list, 3)
        file_layout.addWidget(buttons_frame, 1)
        
        main_layout.addLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready to import %v%")
        main_layout.addWidget(self.progress_bar)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_files)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.import_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
    def add_files(self):
        """Add individual CSV files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select CSV Files",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_paths:
            return
            
        # Add files to list
        for file_path in file_paths:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.file_list.addItem(os.path.basename(file_path))
                
        # Update progress bar
        self.update_progress_status()
        
    def add_directory(self):
        """Add all CSV files from a directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory Containing CSV Files"
        )
        
        if not directory:
            return
            
        # Add all CSV files from directory
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                file_path = os.path.join(directory, filename)
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.file_list.addItem(os.path.basename(file_path))
                    
        # Update progress bar
        self.update_progress_status()
        
    def remove_selected(self):
        """Remove selected files from the list."""
        selected_items = self.file_list.selectedItems()
        
        if not selected_items:
            return
            
        for item in selected_items:
            file_name = item.text()
            # Find the file path that ends with this filename
            for file_path in self.selected_files[:]:
                if os.path.basename(file_path) == file_name:
                    self.selected_files.remove(file_path)
                    break
                    
            # Remove item from list widget
            self.file_list.takeItem(self.file_list.row(item))
            
        # Update progress bar
        self.update_progress_status()
        
    def clear_files(self):
        """Clear all files from the list."""
        self.selected_files = []
        self.file_list.clear()
        
        # Update progress bar
        self.update_progress_status()
        
    def update_progress_status(self):
        """Update the progress bar status."""
        file_count = len(self.selected_files)
        
        if file_count == 0:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("No files selected")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"Ready to import {file_count} files")
            
    def import_files(self):
        """Import all selected files."""
        if not self.selected_files:
            QMessageBox.warning(
                self,
                "No Files Selected",
                "Please select at least one CSV file to import."
            )
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import {len(self.selected_files)} CSV files? This will overwrite any existing costs for the same project types.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        # Import files
        success_count = 0
        failure_count = 0
        messages = []
        
        # Update progress bar
        self.progress_bar.setRange(0, len(self.selected_files))
        self.progress_bar.setValue(0)
        
        # Process each file
        for i, file_path in enumerate(self.selected_files):
            # Update progress
            self.progress_bar.setValue(i)
            self.progress_bar.setFormat(f"Importing {os.path.basename(file_path)}... {i}/{len(self.selected_files)}")
            
            # Import file
            success, message = self.importer.import_csv(file_path, self.element_costs_model)
            
            if success:
                success_count += 1
            else:
                failure_count += 1
                
            messages.append(f"{os.path.basename(file_path)}: {message}")
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
        # Update progress
        self.progress_bar.setValue(len(self.selected_files))
        self.progress_bar.setFormat(f"Import completed: {success_count} succeeded, {failure_count} failed")
        
        # Emit signal
        self.importCompleted.emit(success_count, failure_count, messages)
        
        # Show result
        if failure_count == 0:
            QMessageBox.information(
                self,
                "Import Completed",
                f"Successfully imported {success_count} CSV files."
            )
            self.accept()
        else:
            error_msg = "\n".join([msg for msg in messages if "Failed" in msg])
            QMessageBox.warning(
                self,
                "Import Completed with Errors",
                f"Imported {success_count} files successfully, but {failure_count} files failed:\n\n{error_msg}"
            )
            # Keep the dialog open so user can see the errors