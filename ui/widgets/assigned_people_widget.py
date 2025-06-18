# ui/widgets/assigned_people_widget.py
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QPushButton, QLabel, QVBoxLayout, QWidget
)
from ui.dialogs.assigned_people_dialog import AssignedPeopleDialog

class AssignedPeopleWidget(QWidget):
    """Widget for selecting assigned people for travel."""
    
    def __init__(self, project_model, province, parent=None):
        super().__init__(parent)
        self.project_model = project_model
        self.province = province
        self.init_ui()
        
        # Connect to model's data changed signal
        self.project_model.dataChanged.connect(self.update_from_model)
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a button to show selection dialog
        self.select_btn = QPushButton("Select People...")
        self.select_btn.clicked.connect(self.show_selection_dialog)
        
        # Create a label to display selected people
        self.selection_label = QLabel()
        self.update_selection_label()
        
        layout.addWidget(self.selection_label)
        layout.addWidget(self.select_btn)
        
    def get_assigned_people(self):
        """Get the list of emails currently assigned to this province."""
        if self.province in self.project_model.travel:
            return self.project_model.travel[self.province].get("fulltime", {}).get("assigned_people", [])
        return []
        
    def update_selection_label(self):
        """Update the label showing selected people."""
        assigned_people = self.get_assigned_people()
        
        if not assigned_people:
            self.selection_label.setText("No people assigned")
            return
            
        # Format selected people for display
        if len(assigned_people) <= 2:
            # Show all if only 1-2 people
            people_text = ", ".join(assigned_people)
        else:
            # Show first two and a count
            people_text = f"{assigned_people[0]}, {assigned_people[1]} +{len(assigned_people)-2} more"
            
        self.selection_label.setText(people_text)
        
    def show_selection_dialog(self):
        """Show dialog for selecting people."""
        # Get current assigned people
        assigned_people = self.get_assigned_people()
        
        dialog = AssignedPeopleDialog(
            self.project_model.assignments,
            assigned_people,
            self
        )
        
        if dialog.exec():
            # Update assigned people
            new_assigned_people = dialog.get_selected_people()
            
            # Update the model
            if self.province not in self.project_model.travel:
                self.project_model.travel[self.province] = {
                    "fulltime": {
                        "travel_days": 0,
                        "assigned_people": []
                    },
                    "parttime": {
                        "supervisor": {"distant": 0, "nearby": 0},
                        "interviewer": {"distant": 0, "nearby": 0},
                        "qc": {"distant": 0, "nearby": 0}
                    },
                    "interviewer": {"distant": 0, "nearby": 0},
                    "qc": {"distant": 0, "nearby": 0}
                }
            
            if "fulltime" not in self.project_model.travel[self.province]:
                self.project_model.travel[self.province]["fulltime"] = {
                    "travel_days": 0,
                    "assigned_people": []
                }
                
            # Update the assigned_people in the model
            self.project_model.travel[self.province]["fulltime"]["assigned_people"] = new_assigned_people
            
            # Emit dataChanged signal
            self.project_model.dataChanged.emit()
            
            # Update display
            self.update_selection_label()
            
    @Slot()
    def update_from_model(self):
        """Update widget when model changes."""
        self.update_selection_label()