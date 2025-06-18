# ui/tabs/samples_tab.py
# -*- coding: utf-8 -*-
"""
Samples tab for the Project Cost Calculator application.
Manages sample sizes for each province, target audience, and sample type.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QSpinBox, QDoubleSpinBox, QPushButton,
    QHeaderView, QSizePolicy, QScrollArea, QFrame, QToolButton, QToolTip
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QStyledItemDelegate

from models.project_model import ProjectModel
from config.predefined_values import TARGET_AUDIENCE_INTERVIEWER_TARGETS
from ui.dialogs.sample_edit_dialog import SampleEditDialog
from utils import utils
from config.predefined_values import SAMPLE_TYPES
from formulars .pricing_formulas import calculate_daily_sup_target
from utils.utils import (
    proper,
    shortten_string
)

class EditButton(QPushButton):
    """Custom button class to avoid lambda closure issues in loops."""
    
    def __init__(self, row, callback_fn, parent=None):
        super().__init__("Edit", parent)
        self.row = row
        self.callback_fn = callback_fn
        self.setMaximumWidth(80)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply style
        self.setStyleSheet("""
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
        
        # Connect clicked signal
        self.clicked.connect(self.on_clicked)
        
    def on_clicked(self):
        """Handle button click event."""
        self.callback_fn(self.row)


class SamplesTab(QWidget):
    """
    Tab for managing sample sizes for each province, target audience, and sample type.
    """
    def __init__(self, project_model):
        super().__init__()
        self.project_model = project_model
        
        self.collapsed = False
        self.max_lines = 2
        self.full_text = (
            "Define sample sizes, price growth rates, Target for Interviewers, and daily supervisor targets "
            "for each target audience and sample type in each province.\n"
            "Click the Edit button to modify row details. Hover over comments to see full text. "
            "This information will be used for cost calculation."
        )

        # Main layout
        main_layout = QVBoxLayout(self)

        # Instruction label
        self.instruction_label = QLabel()
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setTextFormat(Qt.PlainText)

        self.instruction_toggle_button = QPushButton("Show more")
        self.instruction_toggle_button.clicked.connect(self.toggle_text)

        instruction_widget = QWidget()
        instruction_layout = QVBoxLayout(instruction_widget)
        instruction_layout.addWidget(self.instruction_label)
        instruction_layout.addWidget(self.instruction_toggle_button)
        instruction_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(instruction_widget)
        
        # Create province tabs
        self.province_tabs = QTabWidget()
        self.province_tabs.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.province_tabs)
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
        # Hiển thị ban đầu phần instruction
        self.update_label()  

        # Initial update from model
        self.update_from_model()
    
    def update_label(self):
        if self.collapsed:
            lines = self.full_text.strip().split("<br>")
            short_text = "<br>".join(lines[:self.max_lines])
            if len(lines) > self.max_lines:
                short_text += "..."
            self.instruction_label.setText(short_text)
            self.instruction_toggle_button.setText("Show More")
        else:
            self.instruction_label.setText(self.full_text)
            self.instruction_toggle_button.setText("Show Less")

    def toggle_text(self):
        self.collapsed = not self.collapsed
        self.update_label()

    @Slot()
    def update_from_model(self):
        # Cập nhật lại nội dung instruction
        objectives = self.project_model.general.get("project_objectives", "").strip()
        objectives = objectives.replace("\n", "<br>").replace("----", "<br><br>")

        self.instruction_label.setTextFormat(Qt.RichText)

        if objectives:
            self.instruction_label.setTextFormat(Qt.RichText)
            self.full_text = (
                f"<b>Project Objectives:</b> <br><br>{objectives}<br><br>"
                "Define sample sizes, price growth rates, Target for Interviewers, and daily supervisor targets "
                "for each target audience and sample type in each province.<br><br>"
                "Click the Edit button to modify row details. Hover over comments to see full text. "
                "This information will be used for cost calculation."
            )
        else:
            self.instruction_label.setTextFormat(Qt.PlainText)
            self.full_text = (
                "Define sample sizes, price growth rates, Target for Interviewers, and daily supervisor targets "
                "for each target audience and sample type in each province.\n"
                "Click the Edit button to modify row details. Hover over comments to see full text. "
                "This information will be used for cost calculation."
            )
        
        self.update_label()

        """Update the UI elements from the model data."""
        # Get selected provinces, target audiences, and sample types
        provinces = self.project_model.general["provinces"]
        target_audiences = self.project_model.general["target_audiences"]
        sample_types = self.project_model.general["sample_types"]
        
        # Save current tab index
        current_index = self.province_tabs.currentIndex()
        
        # Clear existing tabs
        while self.province_tabs.count() > 0:
            self.province_tabs.removeTab(0)
            
        # If any of the dimensions is empty, show a message
        if not provinces or not target_audiences or not sample_types:
            msg_label = QLabel(
                "Please select at least one province, target audience, and sample type in the General tab."
            )
            msg_label.setAlignment(Qt.AlignCenter)
            
            empty_widget = QWidget()
            empty_layout = QVBoxLayout(empty_widget)
            empty_layout.addStretch()
            empty_layout.addWidget(msg_label)
            empty_layout.addStretch()
            
            self.province_tabs.addTab(empty_widget, "No Data")
            return
            
        # Create a tab for each province
        for province in provinces:
            province_widget = QWidget()
            province_layout = QVBoxLayout(province_widget)
            
            # Create a table for this province
            table = SamplesTable(
                self.project_model,
                province
            )
            province_layout.addWidget(table)
            
            # Add tab for this province
            self.province_tabs.addTab(province_widget, province)
            
        # Restore tab index if possible
        if current_index >= 0 and current_index < self.province_tabs.count():
            self.province_tabs.setCurrentIndex(current_index)

# Delegate hỗ trợ wrap text
class TextWrapDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.wrapText = True  # Quan trọng để wrap!

class SamplesTable(QTableWidget):
    """
    Table widget for displaying and editing sample sizes and price growth rates.
    """
    def __init__(self, project_model, province):
        """
        Initialize the table.
        
        Args:
            project_model (ProjectModel): Project model
            province (str): Province name
            target_audiences (dict): List of target audiences
            sample_types (list): List of sample types
        """
        super().__init__()
        self.project_model = project_model
        self.province = province
        
        # Set row and column counts
        self.setRowCount(len(self.project_model.general["target_audiences"]) * len(self.project_model.general["sample_types"]))
        self.setColumnCount(10)  # Target Audience, Sample Type, Sample Size, Price Growth Rate, Target for Interviewer, Daily SUP Target, Comment, Actions
        
        self.setWordWrap(True)  # Cho phép wrap toàn bảng
        self.setItemDelegate(TextWrapDelegate(self))  # Quan trọng

        # Set headers
        self.setHorizontalHeaderLabels([
            "Target Audience",
            "Sample Type",
            "Price",
            "Sample Size",
            "Extra",
            "Price Growth Rate (%)",
            "Target for Interviewer",
            "Daily Target for SUP",
            "Comment",
            "Actions"
        ])
        
        # Set header properties
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Target Audience
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Sample Type
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Price
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Extra
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Price Growth Rate
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # Target for Interviewer
        header.setSectionResizeMode(6, QHeaderView.Fixed)    # Daily SUP Target
        header.setSectionResizeMode(7, QHeaderView.Interactive)  # Comment
        header.setSectionResizeMode(8, QHeaderView.Fixed)    # Actions
        header.setMinimumSectionSize(100)                    # Minimum column width
        
        self.setColumnWidth(1, 100)  # Sample Type
        self.setColumnWidth(2, 80)  # Price
        self.setColumnWidth(3, 80)  # Extra
        self.setColumnWidth(4, 80)  # Price Growth Rate
        self.setColumnWidth(5, 80)  # Target for Interviewer
        self.setColumnWidth(6, 100)  # Daily SUP Target
        self.setColumnWidth(8, 200)  # Comment
        self.setColumnWidth(9, 100)  # Actions
        
        # Style header
        self.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #f0f0f0; padding: 4px; }")
        
        # Populate table
        self.populate_table()
        
        # Apply some styling
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # No direct editing
        
        # Resize rows to accommodate comments
        self.resizeRowsToContents()
        
    def populate_table(self):
        """Populate the table with data."""
        row_count = 0

        for row, audience_data in enumerate(self.project_model.samples.get(self.province, {}).values()):
            for row, price_item in enumerate(audience_data.get("pricing", {})):
                row_count += 1
        
        self.setRowCount(row_count)

        row_index = 0

        for row, audience_data in enumerate(self.project_model.samples.get(self.province, {}).values()):
            for price_row, price_item in enumerate(audience_data.get("pricing", {})):
                sample_type = audience_data.get("sample_type", "Main")
                name = audience_data.get("name", "")
                sample_size = audience_data.get("sample_size", 0)
                extra_rate = audience_data.get("extra_rate", 0)
                price = price_item.get("price", 0.0)
                price_growth = price_item.get("price_growth", 0.0)
                interviewer_target = audience_data.get("target_for_interviewer", 0)
                daily_sup_target = audience_data.get("daily_sup_target", 0.0)
                comment = audience_data.get("comment", {})
                price_comment = price_item.get("comment", {})
                
                # Target Audience (Column 0)
                audience_item = QTableWidgetItem(self.format_audience_name(audience_data))
                audience_item.setData(Qt.UserRole, audience_data)
                audience_item.setFlags(audience_item.flags() & ~Qt.ItemIsEditable)
                audience_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                audience_item.setData(Qt.TextWordWrap, True)
                self.setItem(row_index, 0, audience_item)
                
                # Sample Type (Column 1)
                sample_type_label = sample_type if price_item["type"] in SAMPLE_TYPES else f'{sample_type} ({utils.proper(price_item.get("type", ""))})'
                
                sample_type_item = QTableWidgetItem(sample_type_label)
                sample_type_item.setData(Qt.UserRole, utils.proper(price_item.get("type", "")))  # Store full price item data
                sample_type_item.setFlags(sample_type_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 1, sample_type_item)
                
                # Price (Column 1)
                price_value_item = QTableWidgetItem(str(f"{price:,}"))
                price_value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                price_value_item.setFlags(price_value_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 2, price_value_item)

                # Sample Size (Column 2)
                size_item = QTableWidgetItem(str(sample_size))
                size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 3, size_item)
                
                # Extra (Column 3)
                extra_rate_item = QTableWidgetItem(f"{extra_rate}%")
                extra_rate_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                extra_rate_item.setFlags(extra_rate_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 4, extra_rate_item)

                # Price Growth Rate (Column 4)
                growth_item = QTableWidgetItem(f"{price_growth:.1f}%")
                growth_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                growth_item.setFlags(growth_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 5, growth_item)
                
                # Target for Interviewer (Column 4)
                interviewer_item = QTableWidgetItem(str(interviewer_target))
                interviewer_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                interviewer_item.setFlags(interviewer_item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row_index, 6, interviewer_item)
                
                # Daily SUP Target (Column 5)
                # Calculate the formula string
                interviewers_per_supervisor = self.project_model.settings.get("interviewers_per_supervisor", 8)

                daily_sup_target_benchmark = calculate_daily_sup_target(
                    sample_size, interviewer_target, interviewers_per_supervisor
                )

                is_custom = abs(daily_sup_target - daily_sup_target_benchmark) > 0.001 if daily_sup_target_benchmark else daily_sup_target > 0

                daily_sup_text = f"{daily_sup_target:.2f}"

                if is_custom:
                    daily_sup_text += f" (custom)"
                else:
                    daily_sup_text += f" ({sample_size} / {interviewer_target} / {interviewers_per_supervisor})"
                
                daily_sup_item = QTableWidgetItem(daily_sup_text)
                daily_sup_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                daily_sup_item.setFlags(daily_sup_item.flags() & ~Qt.ItemIsEditable)
                
                # Highlight custom values
                if is_custom:
                    daily_sup_item.setBackground(QColor(255, 235, 230))  # Light orange for custom values
                
                self.setItem(row_index, 7, daily_sup_item)
                
                # Comment (Column 6)
                # Format comment dictionary into readable strings for display and tooltip
                comment_text = self.format_comment(comment)
                price_comment_text = self.format_comment(price_comment)

                if price_comment_text: 
                    comment_text += "; " + price_comment_text

                comment_item = QTableWidgetItem(comment_text)
                comment_item.setFlags(comment_item.flags() & ~Qt.ItemIsEditable)
                comment_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                comment_item.setData(Qt.TextWordWrap, True)

                tooltip_text = self.format_comment_tooltip(comment)
                price_tooltip_text = self.format_comment_tooltip(price_comment)

                if price_tooltip_text:
                    tooltip_text += "<hr>" + price_tooltip_text

                # Set tooltip with full comment text if available
                comment_item.setToolTip(f"<div style='white-space:pre-wrap; max-width:400px;'>{tooltip_text}</div>")
                comment_item.setBackground(QColor(255, 255, 220))  # Light yellow background for comments
                
                self.setItem(row_index, 8, comment_item)
                
                # Edit Button (Column 7)
                edit_button_container = QWidget()
                edit_button_layout = QHBoxLayout(edit_button_container)
                edit_button_layout.setContentsMargins(4, 4, 4, 4)
                edit_button_layout.setAlignment(Qt.AlignCenter)
                
                # Use the custom EditButton class to avoid lambda closure issues
                edit_button = EditButton(row_index, self.edit_row)
                
                edit_button_layout.addWidget(edit_button)
                self.setCellWidget(row_index, 9, edit_button_container)

                row_index += 1

        self.resizeRowsToContents()  # Cập nhật lại row height sau khi set item
    
    def format_comment(self, comment):
        """Format comment dictionary into a readable string."""
        titles = {
            "price_growth": "Price Growth",
            "interviewer_target": "Target for Interviewer",
            "daily_sup_target": "Daily SUP Target" 
        }

        comment_parts = []

        for key, value in comment.items():
            comment_parts.append(f"{titles.get(key, key).capitalize()}: {shortten_string(value, 30)}")

        return "; ".join(comment_parts) if comment_parts else ""
    
    def format_comment_tooltip(self, comment):
        """Format comment dictionary into a tooltip string."""
        titles = {
            "price_growth": "Price Growth",
            "interviewer_target": "Target for Interviewer",
            "daily_sup_target": "Daily SUP Target" 
        }

        tooltip_parts = []

        for key, value in comment.items():
            tooltip_parts.append(f"<b>{titles.get(key, key).capitalize()}:</b><br> {value}")

        tooltip_text = "<hr>".join(tooltip_parts) if tooltip_parts else ""

        return tooltip_text;
        
    def resizeRowsToContents(self):
        """Resize rows to fit content better, especially for rows with comments."""
        for row in range(self.rowCount()):
            comment_item = self.item(row, 6)
            if comment_item and comment_item.text():
                # Increase row height for rows with comments to make them more visible
                self.setRowHeight(row, 60)  # Fixed increased height for comment rows
            else:
                # Default height for rows without comments
                self.setRowHeight(row, self.verticalHeader().defaultSectionSize())
    
    def edit_row(self, row):
        """
        Open edit dialog for the specified row.
        
        Args:
            row (int): Row index to edit
        """
        # Get data for this row
        audience_data = self.item(row, 0).data(Qt.UserRole)
        sample_type_data = self.item(row, 1).data(Qt.UserRole)
        
        # Get interviewers per supervisor setting
        interviewers_per_supervisor = self.project_model.settings.get("interviewers_per_supervisor", 8)
        
        # Open edit dialog
        dialog = SampleEditDialog(
            self.province,
            audience_data,
            sample_type_data,
            interviewers_per_supervisor,
            self
        )
        
        if dialog.exec():
            # Update model with new data
            updated_audience_data = dialog.get_updated_data()
            
            self.project_model.update_sample(self.province, updated_audience_data)
            
            # Resize rows after update to accommodate any new comments
            self.resizeRowsToContents()
            
            # Display a brief status message in the status bar if available
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Updated sample for {updated_audience_data.get('sample_type')} - {updated_audience_data.get('name')}", 3000)

    def format_audience_name(self, audience):
        lines = [audience["name"]]

        # Gender (nếu khác Both)
        if audience.get("gender") and audience["gender"] != "Both":
            lines.append(f"- Giới tính: {audience['gender']}")

        # Age group (nếu không phải 0 - 100)
        if audience.get("age_range", 0)[0] > 0 and audience.get("age_range", 0)[1] == 0:
            lines.append("- Age group: %s" % audience.get("age_range", 0)[0])
        elif audience.get("age_range", 0)[0] == 0 and audience.get("age_range", 0)[1] > 0:
            lines.append("- Age group: %s" % audience.get("age_range", 0)[1])
        elif audience.get("age_range", 0)[0] > 0 and audience.get("age_range", 0)[1] > 0:
            lines.append("- Age group: %s - %s" % tuple(audience.get("age_range", [0, 0])))

        # Household income (nếu không phải 0 - 100)
        if audience.get("income_range", 0)[0] > 0 and audience.get("income_range", [0, 0])[1] == 0:
            lines.append("- Household income: Above %s" % audience.get("income_range", [0, 0])[0])
        elif audience.get("income_range", 0)[0] > 0 and audience.get("income_range", [0, 0])[1] == 0:
            income_from = f"{audience.get('income_range', [0, 0])[0]:,}"
            income_to = f"{audience.get('income_range', [0, 0])[1]:,}"
            lines.append(f"- Household income: {income_from} - {income_to}")
        elif audience.get("income_range", 0)[0] > 0 and audience.get("income_range", [0, 0])[1] > 0:
            income_from = f"{audience.get('income_range', [0, 0])[0]:,}"
            income_to = f"{audience.get('income_range', [0, 0])[1]:,}"
            lines.append(f"- Household income: {income_from} - {income_to}")

        lines.append(f"-IR: {audience['incident_rate']}%, Complexity: {audience['complexity']}")
        
        # Description (nếu có)
        if audience.get("description"):
            lines.append(f"_ Description: {audience['description']}")

        return "\n".join(lines)