# models/element_costs_model.py
# -*- coding: utf-8 -*-
from PySide6.QtCore import Signal, QObject
import pandas as pd
import logging
from database.db_manager import DatabaseManager
from utils.element_costs_importer import ElementCostsImporter

class ElementCostsModel(QObject):
    """Model for managing element costs for different project types."""
    
    costsChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self.costs = {}  # {project_type: {"data": DataFrame, "metadata": dict}}
        self.logger = logging.getLogger(__name__)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Load costs from database
        self.load_costs_from_database()
    
    def load_costs_from_database(self):
        """Load all element costs from the database with dynamic level/length support."""
        try:
            # Get all project types
            project_types = self.db_manager.get_project_types()
            
            # Load costs for each project type
            for project_type in project_types:
                df, metadata = self.db_manager.get_element_costs(project_type)
                if df is not None and not df.empty:
                    self.costs[project_type] = {
                        "data": df,
                        "metadata": metadata
                    }
            
            self.logger.info(f"Loaded costs for {len(self.costs)} project types from database")
            self.costsChanged.emit()
            
        except Exception as e:
            self.logger.error(f"Failed to load costs from database: {str(e)}")

    def import_csv(self, file_path):
        """Import element costs from a CSV file with dynamic level/length support."""
        try:
            # Use the ElementCostsImporter utility
            importer = ElementCostsImporter()
            success, message = importer.import_csv(file_path, self)
            
            if success:
                self.costsChanged.emit()
            
            return success, message
            
        except Exception as e:
            self.logger.error(f"Failed to import costs: {str(e)}")
            return False, f"Failed to import costs: {str(e)}"
    
    def get_cost(self, project_type, subtitle_code, classification, interview_length):
        """
        Get a specific cost value with dynamic level/length support.
        
        Args:
            project_type (str): The project type name
            subtitle_code (str): The subtitle code
            classification (str): The classification (L1, L2, L3, etc.)
            interview_length (int): The interview length in minutes
            
        Returns:
            float: The cost value, or 0 if not found
        """
        if project_type not in self.costs:
            return 0
            
        df = self.costs[project_type]["data"]
        metadata = self.costs[project_type].get("metadata", {})
        
        # Find the row with the matching subtitle code
        matching_rows = df[df["Subtitle Code"] == subtitle_code]
        if matching_rows.empty:
            return 0
        
        # Determine the appropriate column based on classification and interview length
        available_levels = metadata.get("levels", [])
        available_lengths = metadata.get("lengths", [])
        length_ranges = metadata.get("length_ranges", {})
        
        if classification not in available_levels:
            return 0
        
        # Find the appropriate length range
        matching_length = None
        for length in available_lengths:
            min_length, max_length = length_ranges.get(length, (0, 60))
            if min_length <= interview_length <= max_length:
                matching_length = length
                break
        
        if not matching_length:
            return 0
            
        column = f"{classification} ({matching_length})"
        if column not in df.columns:
            return 0
        
        # Return the cost value
        return matching_rows.iloc[0][column]
    
    def _get_column_name(self, classification, interview_length):
        """
        Get the column name based on classification and interview length with dynamic support.
        
        Args:
            classification (str): The classification (L1, L2, etc.)
            interview_length (int): The interview length in minutes
            
        Returns:
            str: The column name
        """
        # Get the project type
        project_type = self.general.get("project_type")
        
        # Check if the project type has dynamic metadata
        if (project_type in self.element_costs.costs and 
            isinstance(self.element_costs.costs[project_type], dict) and
            "metadata" in self.element_costs.costs[project_type]):
            
            metadata = self.element_costs.costs[project_type]["metadata"]
            
            # Get available length ranges
            available_lengths = metadata.get("lengths", [])
            length_ranges = metadata.get("length_ranges", {})
            
            # Find the appropriate length range
            for length in available_lengths:
                min_length, max_length = length_ranges.get(length, (0, 60))
                if min_length <= interview_length <= max_length:
                    return f"{classification} ({length})"
        
        # Fall back to standard ranges if no metadata or no match
        if interview_length < 15:
            suffix = "(<15 min)"
        elif interview_length < 30:
            suffix = "(15-30 min)"
        elif interview_length < 45:
            suffix = "(30-45 min)"
        else:
            suffix = "(45-60 min)"
            
        return f"{classification} {suffix}"
    
    def update_cost(self, project_type, subtitle_code, classification, interview_length, value):
        """
        Update a specific cost value with dynamic level/length support.
        
        Args:
            project_type (str): The project type name
            subtitle_code (str): The subtitle code
            classification (str): The classification (L1, L2, etc.)
            interview_length (int): The interview length in minutes
            value (float): The new cost value
            
        Returns:
            bool: True if successful, False otherwise
        """
        if project_type not in self.costs:
            return False
            
        df = self.costs[project_type]["data"]
        metadata = self.costs[project_type].get("metadata", {})
        
        # Find the row with the matching subtitle code
        row_idx = df.index[df["Subtitle Code"] == subtitle_code].tolist()
        if not row_idx:
            return False
        
        # Determine the appropriate column based on classification and interview length
        available_levels = metadata.get("levels", [])
        available_lengths = metadata.get("lengths", [])
        length_ranges = metadata.get("length_ranges", {})
        
        if classification not in available_levels:
            return False
        
        # Find the appropriate length range
        matching_length = None
        for length in available_lengths:
            min_length, max_length = length_ranges.get(length, (0, 60))
            if min_length <= interview_length <= max_length:
                matching_length = length
                break
        
        if not matching_length:
            return False
            
        column = f"{classification} ({matching_length})"
        if column not in df.columns:
            return False
        
        # Update the value in the DataFrame
        try:
            df.at[row_idx[0], column] = float(value)
            
            # Update the value in the database
            success = self.db_manager.update_element_cost(
                project_type, subtitle_code, classification, matching_length, value
            )
            
            if success:
                self.costsChanged.emit()
                return True
            else:
                # Revert the change in the DataFrame if database update failed
                self.logger.warning(f"Database update failed for {project_type}, {subtitle_code}, {classification} {matching_length}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating cost: {e}")
            return False
    
    def _get_interview_length_string(self, interview_length):
        """Convert numeric interview length to string representation."""
        if interview_length < 15:
            return "<15 min"
        elif interview_length < 30:
            return "15-30 min"
        elif interview_length < 45:
            return "30-45 min"
        else:
            return "45-60 min"
    
    def get_project_types(self):
        """Get a list of all project types with costs."""
        return list(self.costs.keys())
    
    def get_subtitles(self, project_type):
        """Get a list of all subtitles for a project type."""
        if project_type not in self.costs:
            return []
            
        df = self.costs[project_type]["data"]
        return df["Subtitle 1"].dropna().unique().tolist()

    def get_levels_and_lengths(self, project_type):
        """
        Get the available levels and lengths for a project type.
        
        Args:
            project_type (str): The project type name
            
        Returns:
            dict: Dictionary with 'levels' and 'lengths' lists
        """
        if project_type not in self.costs or "metadata" not in self.costs[project_type]:
            return {"levels": [], "lengths": []}
            
        metadata = self.costs[project_type]["metadata"]
        return {
            "levels": metadata.get("levels", []),
            "lengths": metadata.get("lengths", [])
        }

    def add_project_type(self, project_type, levels=None, lengths=None):
        """
        Add a new project type with empty costs.
        
        Args:
            project_type (str): Name of the project type to add
            levels (list, optional): List of levels to use. Defaults to ["L1", "L2", "L3", "L4"]
            lengths (list, optional): List of length ranges. Defaults to ["<15 min", "15-30 min", "30-45 min", "45-60 min"]
            
        Returns:
            tuple: (success, message)
        """
        if project_type in self.costs:
            return False, "Project type already exists"
        
        # Use default levels and lengths if not provided
        if levels is None:
            levels = ["L1", "L2", "L3", "L4"]
        
        if lengths is None:
            lengths = ["<15 min", "15-30 min", "30-45 min", "45-60 min"]
        
        # Create length_ranges dictionary
        length_ranges = {}
        for length in lengths:
            length_ranges[length] = self._parse_length_range(length)
        
        # Create metadata dictionary
        metadata = {
            "levels": levels,
            "lengths": lengths,
            "length_ranges": length_ranges
        }
        
        # Create base columns for the DataFrame
        base_columns = [
            "Project Type", "Subtitle 1", "Subtitle 2", "Subtitle 3", "Subtitle 4", "Subtitle 5", 
            "Subtitle Code", "Unit"
        ]
        
        # Add columns for each level/length combination
        for level in levels:
            for length in lengths:
                base_columns.append(f"{level} ({length})")
        
        # Create empty DataFrame
        df = pd.DataFrame(columns=base_columns)
        
        # Set project type for all rows
        df["Project Type"] = project_type
        
        # Store in the model using the new format
        self.costs[project_type] = {
            "data": df,
            "metadata": metadata
        }
        
        # Save to database with metadata
        success = self.db_manager.save_element_costs(project_type, df, metadata)
        
        if success:
            self.costsChanged.emit()
            return True, f"Successfully added project type {project_type} with {len(levels)} levels and {len(lengths)} length ranges"
        else:
            # Remove from memory if database save failed
            del self.costs[project_type]
            return False, f"Failed to add project type {project_type} to database"

    def _parse_length_range(self, length_str):
        """
        Parse a length string into minimum and maximum minutes.
        
        Args:
            length_str (str): String like "< 15 min" or "15-30 min"
            
        Returns:
            tuple: (min_minutes, max_minutes)
        """
        if not length_str:
            return (0, 60)  # Default range
            
        length_str = length_str.lower().strip()
        
        # Handle "< X min" format
        if "<" in length_str:
            import re
            match = re.search(r'<\s*(\d+)', length_str)
            if match:
                max_val = int(match.group(1))
                return (0, max_val - 1)
        
        # Handle "X-Y min" format
        if "-" in length_str:
            parts = length_str.split("-")
            if len(parts) == 2:
                min_str = parts[0].strip()
                max_str = parts[1].split(" ")[0].strip()
                try:
                    min_val = int(min_str)
                    max_val = int(max_str)
                    return (min_val, max_val)
                except ValueError:
                    pass
        
        # Try to extract a single number
        import re
        match = re.search(r'(\d+)', length_str)
        if match:
            val = int(match.group(1))
            return (val, val)
            
        # Default fallback
        return (0, 60)

    def delete_project_type(self, project_type):
        """Delete a project type."""
        if project_type not in self.costs:
            return False, "Project type does not exist"
        
        # Delete from database
        success = self.db_manager.delete_project_type(project_type)
        
        if success:
            # Delete from memory
            del self.costs[project_type]
            self.costsChanged.emit()
            return True, f"Successfully deleted project type {project_type}"
        else:
            return False, f"Failed to delete project type {project_type} from database"
    
    def export_csv(self, project_type, file_path):
        """Export costs for a project type to CSV."""
        if project_type not in self.costs:
            return False, "Project type does not exist"
            
        try:
            self.costs[project_type].to_csv(file_path, index=False)
            return True, f"Successfully exported costs for {project_type}"
        except Exception as e:
            return False, f"Failed to export costs: {str(e)}"