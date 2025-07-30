# ui/tabs/samples_tab.py
# -*- coding: utf-8 -*-
"""
Samples tab for the Project Cost Calculator application.
Manages sample sizes for each province, target audience, and sample type.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QSpinBox, QDoubleSpinBox, QPushButton,
    QHeaderView, QSizePolicy, QScrollArea, QFrame, QToolButton, QToolTip, QComboBox, QTableWidget
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QStyledItemDelegate

from models.project_model import ProjectModel
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
        self.max_lines = 0
        self.full_text = (
            "..."
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
        html_table = self.project_model.generate_settings_table()

        # objectives = self.project_model.general.get("project_objectives", "").strip()
        # objectives = objectives.replace("\n", "<br>").replace("----", "<br><br>")

        self.instruction_label.setTextFormat(Qt.RichText)

        if html_table:
            self.instruction_label.setTextFormat(Qt.RichText)
            self.full_text = (
                f"{html_table}"
                "Define sample sizes, price growth rates, Target for Interviewers, and daily supervisor targets "
                "for each target audience and sample type in each province.<br><br>"
                "Click the Edit button to modify row details. Hover over comments to see full text. "
                "This information will be used for cost calculation."
            )
        else:
            self.instruction_label.setTextFormat(Qt.PlainText)
            self.full_text = (
                "<b>Hướng dẫn:</b><br>"
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
        sample_types = self.project_model.get_sample_types()
        
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

        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        table = SamplesTable(
            self.project_model
        )

        table_layout.addWidget(table)

        self.province_tabs.addTab(table_widget, "Samples")

# Delegate hỗ trợ wrap text
class TextWrapDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.wrapText = True  # Quan trọng để wrap!

class SamplesTable(QWidget):
    """
    Table widget for displaying and editing sample sizes and price growth rates.
    """
    def __init__(self, project_model):
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
        self.table = QTableWidget()

        self.province_filter = QComboBox()
        self.sample_type_filter = QComboBox()

        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # --- Filter Section ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Province:"))
        filter_layout.addWidget(self.province_filter)
        filter_layout.addWidget(QLabel("Sample Type:"))
        filter_layout.addWidget(self.sample_type_filter)
        layout.addLayout(filter_layout)

        layout.addWidget(self.table)
        self.setLayout(layout)
        
        self.populate_filters()
        
        # Populate table
        self.populate_table()

    def populate_filters(self):
        provinces = list(self.project_model.samples.keys())
        
        self.province_filter.addItem("All")
        self.province_filter.addItems(provinces)

        # Sample types có thể trộn từ tất cả tỉnh
        sample_types = self.project_model.get_sample_types()

        self.sample_type_filter.addItem("All")
        self.sample_type_filter.addItems(sorted(sample_types))

        self.province_filter.currentTextChanged.connect(self.populate_table)
        self.sample_type_filter.currentTextChanged.connect(self.populate_table)

    def populate_table(self):
        # Set headers
        headers = {
            "Province" : { 'width' : 120, 'header_view' : QHeaderView.Fixed },
            "Target Audience" : { 'width' : 250, 'header_view' : QHeaderView.Interactive },
            "Sample Type" : { 'width' : 80, 'header_view' : QHeaderView.Fixed },
            "Price" : { 'width' : 80, 'header_view' : QHeaderView.Fixed },
            "Sample Size" : { 'width' : 80, 'header_view' : QHeaderView.Fixed },
            "Extra" : { 'width' : 80, 'header_view' : QHeaderView.Fixed },
            "Price Growth\nRate (%)" : { 'width' : 120, 'header_view' : QHeaderView.Fixed },
            "Target for\nInterviewer" : { 'width' : 120, 'header_view' : QHeaderView.Fixed },
            "Daily Target\nfor SUP" : { 'width' : 120, 'header_view' : QHeaderView.Fixed },
            "Comment" : { 'width' : 250, 'header_view' : QHeaderView.Fixed },
            "Actions" : { 'width' : 100, 'header_view' : QHeaderView.Fixed }
        }

        header = self.table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
            padding: 4px;
            height: 40px;  /* tăng chiều cao nếu cần */
            font-weight: bold;
            text-align: center;
        }
        """)

        for i, properties in enumerate(headers.values()):
            header.setSectionResizeMode(i, properties.get('header_view'))
            self.table.setColumnWidth(i, properties.get('width'))
        
        # Style header
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #f0f0f0; padding: 4px; }")

        row_count = 0

        selected_province = self.province_filter.currentText()
        selected_sample_type = self.sample_type_filter.currentText()

        for province, province_data in self.project_model.samples.items():
            if selected_province != 'All' and province != selected_province:
                continue
            
            for audience_data in province_data.values():
                if selected_sample_type != 'All' and audience_data.get('sample_type') != selected_sample_type:
                    continue

                row_count += len(audience_data.get("pricing", []))

        self.table.setRowCount(row_count)
        self.table.setColumnCount(len(headers.keys()))  # Target Audience, Sample Type, Sample Size, Price Growth Rate, Target for Interviewer, Daily SUP Target, Comment, Actions
        
        self.table.setHorizontalHeaderLabels(headers.keys())

        row_index = 0

        for province, province_data in self.project_model.samples.items():
            if selected_province != 'All' and province != selected_province:
                continue
            
            for audience_data in province_data.values():
                if selected_sample_type != 'All' and audience_data.get('sample_type') != selected_sample_type:
                    continue

                for price_item in audience_data.get('pricing', []):
                    self.populate_row(row_index, province, audience_data, price_item)
                    row_index += 1
        
        self.table.resizeRowsToContents()

        self.table.setWordWrap(True)  # Cho phép wrap toàn bảng
        self.table.setItemDelegate(TextWrapDelegate(self))  # Quan trọng

        # Apply some styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # No direct editing
        
        # Resize rows to accommodate comments
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        

    def populate_row(self, row_index, province, audience_data, price_item):
        
        def create_item(text, alignment=Qt.AlignLeft | Qt.AlignVCenter):
            item = QTableWidgetItem(text)
            item.setTextAlignment(alignment)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            return item
        
        sample_type = audience_data.get("sample_type", "Main")
        target_audience_name = audience_data.get("target_audience_name", "")
        sample_size = audience_data.get("sample_size", 0)
        extra_rate = audience_data.get("extra_rate", 0)
        price = price_item.get("price", 0.0)
        price_growth = price_item.get("price_growth", 0.0)
        interviewer_target = audience_data.get('target', {}).get("target_for_interviewer", 0)
        daily_sup_target = audience_data.get('target', {}).get("daily_sup_target", 0.0)
        daily_interview_target = audience_data.get('target', {}).get('daily_interview_target', 0)
        comment = audience_data.get("comment", {})
        price_comment = price_item.get("comment", {})

        price_type = price_item.get("type", "")
        sample_type_label = sample_type if price_type in SAMPLE_TYPES else f'{sample_type} ({utils.proper(price_type)})'

        interviewers_per_supervisor = audience_data.get('target', {}).get('interviewers_per_supervisor', 0)

        benchmark = calculate_daily_sup_target(sample_size, interviewer_target, interviewers_per_supervisor)
        is_custom = abs(daily_sup_target - benchmark) > 0.001 if benchmark else daily_sup_target > 0
        daily_sup_text = f"{daily_sup_target:.2f}"
        daily_sup_text += " (custom)" if is_custom else f" ({sample_size} / {interviewer_target} / {interviewers_per_supervisor})"
     
        comment_text = self.format_comment(comment)
        price_comment_text = self.format_comment(price_comment)
        if price_comment_text:
            comment_text += "\n" + price_comment_text

        tooltip_text = self.format_comment_tooltip(comment)
        price_tooltip_text = self.format_comment_tooltip(price_comment)
        if price_tooltip_text:
            tooltip_text += "<hr>" + price_tooltip_text
        
        # Populate cells
        self.table.setItem(row_index, 0, create_item(province))
        self.table.item(row_index, 0).setData(Qt.UserRole, province)

        self.table.setItem(row_index, 1, create_item(self.format_audience_name(audience_data)))
        self.table.item(row_index, 1).setData(Qt.UserRole, audience_data)

        type_item = create_item(sample_type_label)
        type_item.setData(Qt.UserRole, utils.proper(price_type))
        self.table.setItem(row_index, 2, type_item)

        self.table.setItem(row_index, 3, create_item(f"{price:,}", Qt.AlignRight | Qt.AlignVCenter))
        self.table.setItem(row_index, 4, create_item(str(sample_size), Qt.AlignRight | Qt.AlignVCenter))
        self.table.setItem(row_index, 5, create_item(f"{extra_rate}%", Qt.AlignRight | Qt.AlignVCenter))
        self.table.setItem(row_index, 6, create_item(f"{price_growth:.1f}%", Qt.AlignRight | Qt.AlignVCenter))
        self.table.setItem(row_index, 7, create_item(str(interviewer_target), Qt.AlignRight | Qt.AlignVCenter))

        daily_item = create_item(daily_sup_text, Qt.AlignRight | Qt.AlignVCenter)
        if is_custom:
            daily_item.setBackground(QColor(255, 235, 230))
        self.table.setItem(row_index, 8, daily_item)

        comment_item = create_item(comment_text)
        comment_item.setData(Qt.TextWordWrap, True)
        comment_item.setToolTip(f"<div style='white-space:pre-wrap; max-width:400px;'>{tooltip_text}</div>")
        comment_item.setBackground(QColor(255, 255, 220))
        self.table.setItem(row_index, 9, comment_item)

        # Edit Button (Column 7)
        edit_button_container = QWidget()
        edit_button_layout = QHBoxLayout(edit_button_container)
        edit_button_layout.setContentsMargins(4, 4, 4, 4)
        edit_button_layout.setAlignment(Qt.AlignCenter)
        
        # Use the custom EditButton class to avoid lambda closure issues
        edit_button = EditButton(row_index, self.edit_row)
        
        edit_button_layout.addWidget(edit_button)
        self.table.setCellWidget(row_index, 10, edit_button_container)
    
    def format_comment(self, comment):
        """Format comment dictionary into a readable string."""
        titles = {
            "price_growth": "Price Growth",
            "target_for_interviewer": "Target for Interviewer",
            "interviewers_per_supervisor": "Interviewers per Supervisor",
            "daily_interview_target": "Daily Interview Target" 
        }

        comment_parts = []

        for key, value in comment.items():
            comment_parts.append(f"{titles.get(key, key).capitalize()}: {shortten_string(value, 30)}")

        return "\n".join(comment_parts) if comment_parts else ""
    
    def format_comment_tooltip(self, comment):
        """Format comment dictionary into a tooltip string."""
        titles = {
            "price_growth": "Price Growth",
            "target_for_interviewer": "Target for Interviewer",
            "interviewers_per_supervisor": "Interviewers per Supervisor",
            "daily_interview_target": "Daily Interview Target"  
        }

        tooltip_parts = []

        for key, value in comment.items():
            tooltip_parts.append(f"<b>{titles.get(key, key).capitalize()}:</b><br> {value}")

        tooltip_text = "<hr>".join(tooltip_parts) if tooltip_parts else ""

        return tooltip_text;
        
    def resizeRowsToContents(self):
        """Resize rows to fit content better, especially for rows with comments."""
        for row in range(self.table.rowCount()):
            comment_item = self.table.item(row, 6)
            if comment_item and comment_item.text():
                # Increase row height for rows with comments to make them more visible
                self.table.setRowHeight(row, 60)  # Fixed increased height for comment rows
            else:
                # Default height for rows without comments
                self.table.setRowHeight(row, self.table.verticalHeader().defaultSectionSize())
    
    def edit_row(self, row):
        """
        Open edit dialog for the specified row.
        
        Args:
            row (int): Row index to edit
        """
        # Get data for this row
        province = self.table.item(row, 0).data(Qt.UserRole)
        audience_data = self.table.item(row, 1).data(Qt.UserRole)
        price_type = self.table.item(row, 2).data(Qt.UserRole)
        rate_card_target = self.project_model.get_rate_card_target(audience_data.get('incident_rate', 100))
        
        # Open edit dialog
        dialog = SampleEditDialog(
            province,
            audience_data,
            price_type,
            rate_card_target,
            self
        )
        
        if dialog.exec():
            # Update model with new data
            updated_audience_data = dialog.get_updated_data()
            
            self.project_model.update_sample(province, updated_audience_data)
            
            # Resize rows after update to accommodate any new comments
            self.resizeRowsToContents()
            
            # Display a brief status message in the status bar if available
            main_window = self.window()
            if hasattr(main_window, 'statusBar'):
                main_window.statusBar().showMessage(f"Updated sample for {updated_audience_data.get('sample_type')} - {updated_audience_data.get('name')}", 3000)

    def format_audience_name(self, audience):
        lines = [audience["target_audience_name"]]

        # Gender (nếu khác Both)
        if audience.get("gender") and audience["gender"] != "Both":
            lines.append(f"- Giới tính: {audience['gender']}")

        # Age group (nếu không phải 0 - 100)
        if audience.get("age_group", 0)[0] > 0 and audience.get("age_group", 0)[1] == 0:
            lines.append("- Age group: %s" % audience.get("age_group", 0)[0])
        elif audience.get("age_group", 0)[0] == 0 and audience.get("age_group", 0)[1] > 0:
            lines.append("- Age group: %s" % audience.get("age_group", 0)[1])
        elif audience.get("age_group", 0)[0] > 0 and audience.get("age_group", 0)[1] > 0:
            lines.append("- Age group: %s - %s" % tuple(audience.get("age_group", [0, 0])))

        # Household income (nếu không phải 0 - 100)
        if audience.get("household_income", 0)[0] > 0 and audience.get("household_income", [0, 0])[1] == 0:
            lines.append("- Household income: Above %s" % audience.get("household_income", [0, 0])[0])
        elif audience.get("household_income", 0)[0] > 0 and audience.get("household_income", [0, 0])[1] == 0:
            income_from = f"{audience.get('household_income', [0, 0])[0]:,}"
            income_to = f"{audience.get('household_income', [0, 0])[1]:,}"
            lines.append(f"- Household income: {income_from} - {income_to}")
        elif audience.get("household_income", 0)[0] > 0 and audience.get("household_income", [0, 0])[1] > 0:
            income_from = f"{audience.get('household_income', [0, 0])[0]:,}"
            income_to = f"{audience.get('household_income', [0, 0])[1]:,}"
            lines.append(f"- Household income: {income_from} - {income_to}")

        lines.append(f"-IR: {audience['incident_rate']}%, Complexity: {audience['complexity']}")
        
        # Description (nếu có)
        if audience.get("description"):
            lines.append(f"_ Description: {audience['description']}")

        return "\n".join(lines)