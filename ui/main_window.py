# ui/main_window.py
# -*- coding: utf-8 -*-
"""
Main window for the Project Cost Calculator application.
Contains the tab widget and menu structure.
"""
import sys
import os

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QToolBar,
    QStatusBar, QVBoxLayout, QWidget, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon

from ui.tabs.general_tab import GeneralTab
from ui.tabs.samples_tab import SamplesTab
from ui.tabs.operations_tab import OperationsTab
from ui.tabs.assignment_tab import AssignmentTab
from ui.dialogs.settings_dialog import SettingsDialog
from ui.tabs.travel_tab import TravelTab
from ui.tabs.additional_costs_tab import AdditionalCostsTab
from models.project_model import ProjectModel
import json
import os
import re
import logging
from components.validation_field import FieldValidator
from ui.dialogs.hierarchical_cost_results_dialog import HierarchicalCostResultsDialog

class MainWindow(QMainWindow):
    """
    Main application window with tabs, menus and toolbars.
    """
    def resource_path(self, path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, path)
        return os.path.join(os.getcwd(), path)
    
    def __init__(self):
        super().__init__()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Set window properties
        self.setWindowTitle("Project Cost Calculator")
        self.resize(1100, 800)
        
        # Create project model
        self.project_model = ProjectModel()
        
        # Create the central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.general_tab = GeneralTab(self.project_model)
        self.samples_tab = SamplesTab(self.project_model)
        self.operations_tab = OperationsTab(self.project_model)
        self.travel_tab = TravelTab(self.project_model)
        self.assignment_tab = AssignmentTab(self.project_model)
        self.additional_costs_tab = AdditionalCostsTab(self.project_model)
        
        # Add tabs to the widget
        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.samples_tab, "Samples")
        self.tab_widget.addTab(self.operations_tab, "Operations")  
        self.tab_widget.addTab(self.assignment_tab, "Assignments")
        self.tab_widget.addTab(self.travel_tab, "Travel")
        self.tab_widget.addTab(self.additional_costs_tab, "Additional Costs")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Connect signals
        self.project_model.dataChanged.connect(self.update_status)
        # self.project_model.element_costs.costsChanged.connect(self.update_status)
        
        self.general_tab.projectTypeChanged.connect(self.operations_tab.handle_project_type_changed)
        self.general_tab.interviewLengthChanged.connect(self.operations_tab.handle_interview_length_changed)

    def create_menu_bar(self):
        """Create the application menu bar."""
        # Create menu bar
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # import_costs_action = QAction("Import Element Costs...", self)
        # import_costs_action.triggered.connect(self.import_element_costs)
        # file_menu.addAction(import_costs_action)
        
        # export_costs_action = QAction("Export Element Costs...", self)
        # export_costs_action.triggered.connect(self.export_element_costs)
        # file_menu.addAction(export_costs_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Settings menu
        settings_menu = menu_bar.addMenu("Settings")
        
        app_settings_action = QAction("Application Settings", self)
        app_settings_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(app_settings_action)

        # Calculate menu
        calculate_menu = menu_bar.addMenu("Calculate")
        
        # Add hierarchical calculation option
        hierarchical_calc_action = QAction("Calculate Hierarchical Cost", self)
        hierarchical_calc_action.setShortcut("F7")
        hierarchical_calc_action.triggered.connect(self.display_hierarchical_cost_results)
        calculate_menu.addAction(hierarchical_calc_action)
        
        report_action = QAction("Generate Report", self)
        report_action.setShortcut("F6")
        report_action.triggered.connect(self.generate_report)
        calculate_menu.addAction(report_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # Database menu
        database_menu = menu_bar.addMenu("Database")

        # Database Info action
        db_info_action = QAction("Database Info", self)
        db_info_action.triggered.connect(self.show_database_info)
        database_menu.addAction(db_info_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add toolbar actions
        new_action = QAction(QIcon("icons/new.png"), "New", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction(QIcon("icons/open.png"), "Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction(QIcon("icons/save.png"), "Save", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
    
        settings_action = QAction(QIcon("icons/settings.png"), "Settings", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        toolbar.addAction(settings_action)
        
        import_costs_action = QAction(QIcon("icons/import.png"), "Import Costs", self)
        import_costs_action.triggered.connect(self.import_element_costs)
        toolbar.addAction(import_costs_action)
        
        toolbar.addSeparator()
        
        # Add hierarchical calculation button
        hierarchical_calc_action = QAction(QIcon("icons/hierarchical_calculate.png"), "Hierarchical Calculate", self)
        hierarchical_calc_action.triggered.connect(self.display_hierarchical_cost_results)
        toolbar.addAction(hierarchical_calc_action)
        
        report_action = QAction(QIcon("icons/report.png"), "Report", self)
        report_action.triggered.connect(self.generate_report)
        toolbar.addAction(report_action)
        
    def new_project(self):
        """Reset the project model for a new project."""
        # Ask for confirmation if data has been entered
        if self.has_data():
            reply = QMessageBox.question(
                self, 
                "New Project", 
                "Are you sure you want to create a new project? All unsaved data will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Reset the project model
        self.project_model.reset()
        self.statusBar().showMessage("New project created")
        
    def has_data(self):
        """Check if any meaningful data has been entered."""
        # Check for basic project info
        if self.project_model.general["project_name"] or self.project_model.general["internal_job"]:
            return True
            
        # Check if any provinces are selected
        if self.project_model.general["provinces"]:
            return True
            
        # Check if any QC methods are defined
        if self.project_model.qc_methods:
            return True
            
        return False
        
    def open_project(self):
        """Open a saved project file."""
        # Ask for confirmation if data has been entered
        if self.has_data():
            reply = QMessageBox.question(
                self, 
                "Open Project", 
                "Are you sure you want to open a project? All unsaved data will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
                
        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Project", 
            "", 
            "Project Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Load data into model
            self.project_model.from_dict(data)
            
            self.statusBar().showMessage(f"Project loaded from {os.path.basename(file_path)}")
                
        except Exception as e:
            self.logger.error(f"Failed to open project: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to open project: {str(e)}"
            )
            
    def save_project(self):
        """Save the current project to a file."""
        # Open file dialog
        field_name, is_valid, error_message = self.project_model.validate()

        if not is_valid:
            self.logger.error(f"Failed to save project: {error_message}")
            self.show_warning_message(field_name, error_message)
            QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to save project: {field_name} - {error_message}"
                )
        else:
            internal_job = re.sub(pattern=r"[-]", repl='', string=self.project_model.general["internal_job"])
            project_name = re.sub(pattern='\s', repl=' ', string=self.project_model.general["project_name"].strip())
            
            filename = f"{internal_job}_{project_name}.json"

            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Project", 
                filename, 
                "Project Files (*.json);;All Files (*)"
            )
            
            if not file_path:
                return
                
            # Ensure .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'
                
            try:
                # Prepare data
                data = self.project_model.to_dict()
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                    
                self.statusBar().showMessage(f"Project saved to {os.path.basename(file_path)}")
                
            except Exception as e:
                self.logger.error(f"Failed to save project: {str(e)}")
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"Failed to save project: {str(e)}"
                )

    

    def show_warning_message(self, field_name:str, message: str):
        label_name = f"{field_name}_warning"
        label = getattr(self.general_tab, label_name, None)
        
        if label:
            label.setText(message)
            label.setVisible(bool(message))

    # Add a new method for showing the settings dialog
    def show_settings_dialog(self):
        """Show the application settings dialog."""
        dialog = SettingsDialog(self.project_model, self)
        dialog.exec()

    def import_element_costs(self):
        """Import element costs from CSV."""
        # Delegate to element costs tab
        self.element_costs_tab.import_csv()
        
    def export_element_costs(self):
        """Export element costs to CSV."""
        # Delegate to element costs tab
        self.element_costs_tab.export_csv()
        
    def generate_report(self):
        """Generate a project report."""
        # This would be implemented in the future
        self.statusBar().showMessage("Report generation not implemented yet")
        
        QMessageBox.information(
            self, 
            "Generate Report", 
            "Report generation would be implemented here.\n"
            "The report would include all project details, calculated costs, and element costs."
        )
        
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Project Cost Calculator",
            "Project Cost Calculator v1.1\n\n"
            "An internal tool for managing project details and calculating costs.\n\n"
            "© IPSOS 2025"
        )
        
    def update_status(self):
        """Update status bar with latest information."""
        # Update status with project info
        project_name = self.project_model.general["project_name"]
        
        # Count element costs
        element_costs_count = len(self.project_model.element_costs.get_project_types())
        
        if project_name:
            status = f"Project: {project_name}"
            if element_costs_count > 0:
                status += f" | Element costs: {element_costs_count} project types"
            self.statusBar().showMessage(status)
        else:
            if element_costs_count > 0:
                self.statusBar().showMessage(f"Element costs: {element_costs_count} project types")
            else:
                self.statusBar().showMessage("Ready")

    def show_database_info(self):
        """Show database information dialog."""
        from ui.dialogs.database_info_dialog import DatabaseInfoDialog
        dialog = DatabaseInfoDialog(self.project_model.element_costs.db_manager, self)
        dialog.exec()

    def display_hierarchical_cost_results(self):
        """Calculate and display hierarchical project cost results."""
        try:
            # Calculate hierarchical costs
            path_file = self.resource_path("config/clt_cost_hierarchy.json")

            with open(path_file, "r", encoding="utf-8") as file:
                hierarchy_data = json.load(file)
            
            cost_data = self.project_model.flatten_cost_hierarchy(hierarchy_data)
            
            dialog = HierarchicalCostResultsDialog(cost_data, self)
            dialog.exec()
            
            self.statusBar().showMessage("Hierarchical cost calculation completed")
        except Exception as e:
            self.logger.error(f"Failed to calculate hierarchical project cost: {str(e)}")
            QMessageBox.critical(
                self, 
                "Calculation Error", 
                f"Failed to calculate hierarchical project cost: {str(e)}"
            )