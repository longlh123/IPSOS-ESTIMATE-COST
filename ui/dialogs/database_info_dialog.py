# ui/dialogs/database_info_dialog.py
# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QProgressBar, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
import os

class DatabaseInfoDialog(QDialog):
    """Dialog to display information about the database."""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        # Dialog properties
        self.setWindowTitle("Database Information")
        self.setMinimumSize(600, 400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Element Costs Database Information")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Get database stats
        stats = self.db_manager.get_database_stats()
        
        # Database info section
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setFrameShadow(QFrame.Raised)
        info_layout = QVBoxLayout(info_frame)
        
        # Database path
        path_label = QLabel(f"<b>Database Location:</b> {stats['path']}")
        path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info_layout.addWidget(path_label)
        
        # File size
        size_mb = stats['size_bytes'] / (1024 * 1024)
        size_label = QLabel(f"<b>Database Size:</b> {size_mb:.2f} MB")
        info_layout.addWidget(size_label)
        
        # Total elements
        elements_label = QLabel(f"<b>Total Element Costs:</b> {stats['total_elements']}")
        info_layout.addWidget(elements_label)
        
        # Add info frame to main layout
        main_layout.addWidget(info_frame)
        
        # Project types table
        table_label = QLabel("Project Types in Database:")
        table_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Project Type", "Number of Cost Elements"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        
        # Add project types to table
        project_types = stats['project_types']
        self.table.setRowCount(len(project_types))
        
        for i, project_type in enumerate(project_types):
            # Add project type
            type_item = QTableWidgetItem(project_type['name'])
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, type_item)
            
            # Add element count
            count_item = QTableWidgetItem(str(project_type['elements']))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_item.setFlags(count_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 1, count_item)
        
        main_layout.addWidget(self.table)
        
        # Database actions
        actions_frame = QFrame()
        actions_frame.setFrameShape(QFrame.StyledPanel)
        actions_layout = QHBoxLayout(actions_frame)
        
        # Backup button
        self.backup_button = QPushButton("Backup Database")
        self.backup_button.setIcon(QIcon("icons/backup.png"))
        self.backup_button.clicked.connect(self.backup_database)
        actions_layout.addWidget(self.backup_button)
        
        # Restore button
        self.restore_button = QPushButton("Restore Database")
        self.restore_button.setIcon(QIcon("icons/restore.png"))
        self.restore_button.clicked.connect(self.restore_database)
        actions_layout.addWidget(self.restore_button)
        
        main_layout.addWidget(actions_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def backup_database(self):
        """Backup the database to a file."""
        import shutil
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Backup Database",
            f"element_costs_backup.db",
            "Database Files (*.db);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Copy the database file
            shutil.copy2(self.db_manager.db_path, file_path)
            
            QMessageBox.information(
                self,
                "Backup Successful",
                f"Database successfully backed up to:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Failed",
                f"Failed to backup database: {str(e)}"
            )
    
    def restore_database(self):
        """Restore the database from a backup file."""
        import shutil
        
        # Confirm with user
        reply = QMessageBox.warning(
            self,
            "Restore Database",
            "Restoring the database will replace all current element costs. This cannot be undone.\n\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Database",
            "",
            "Database Files (*.db);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            # Close all connections to the database
            self.db_manager._get_connection().close()
            
            # Copy the backup file to the database location
            shutil.copy2(file_path, self.db_manager.db_path)
            
            QMessageBox.information(
                self,
                "Restore Successful",
                "Database successfully restored. The application will now close.\n\n"
                "Please restart the application to load the restored data."
            )
            
            # Close the application
            self.accept()
            self.parent().close()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Restore Failed",
                f"Failed to restore database: {str(e)}"
            )