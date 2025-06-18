# utils/element_costs_importer.py
# -*- coding: utf-8 -*-
"""
Utility for importing element costs from CSV files.
"""

import pandas as pd
import logging
import os

class ElementCostsImporter:
    """Utility class for importing element costs from CSV files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def import_csv(self, file_path, element_costs_model):
        """
        Import element costs from a CSV file with dynamic level/length support.
        
        Args:
            file_path (str): Path to the CSV file
            element_costs_model (ElementCostsModel): Model to store the imported costs
                
        Returns:
            tuple: (success, message)
        """
        try:
            self.logger.info(f"Importing element costs from {file_path}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Extract project type from the first row
            project_type = None
            if not df.empty and "Project Type" in df.columns:
                for i in range(min(5, len(df))):  # Check first few rows
                    if pd.notna(df.iloc[i]["Project Type"]):
                        project_type = df.iloc[i]["Project Type"]
                        break
            
            if not project_type:
                return False, "Could not determine project type from CSV"
            
            # Transform the CSV data with dynamic level/length detection
            transformed_df, metadata = self._transform_csv_data(df)
            
            # Store in the model with metadata
            element_costs_model.costs[project_type] = {
                "data": transformed_df,
                "metadata": metadata
            }
            
            # Save to database
            success = element_costs_model.db_manager.save_element_costs(
                project_type, transformed_df, metadata
            )
            
            # Emit signal that costs have changed
            element_costs_model.costsChanged.emit()
            
            if success:
                levels = metadata.get("levels", [])
                lengths = metadata.get("lengths", [])
                message = (f"Successfully imported costs for {project_type} "
                        f"with {len(levels)} levels and {len(lengths)} length ranges")
                self.logger.info(message)
                return True, message
            else:
                return False, f"Failed to save costs for {project_type} to database"
                
        except Exception as e:
            self.logger.error(f"Failed to import costs: {str(e)}")
            return False, f"Failed to import costs: {str(e)}"
    
    def import_directory(self, directory_path, element_costs_model):
        """
        Import all CSV files from a directory.
        
        Args:
            directory_path (str): Path to the directory containing CSV files
            element_costs_model (ElementCostsModel): Model to store the imported costs
            
        Returns:
            tuple: (success_count, failure_count, messages)
        """
        if not os.path.isdir(directory_path):
            return 0, 0, ["Directory does not exist"]
            
        success_count = 0
        failure_count = 0
        messages = []
        
        for filename in os.listdir(directory_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(directory_path, filename)
                success, message = self.import_csv(file_path, element_costs_model)
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                    
                messages.append(f"{filename}: {message}")
                
        return success_count, failure_count, messages
    
    def _transform_csv_data(self, df):
        """
        Transform the CSV data for storage with dynamic level and length support.
        
        Args:
            df (DataFrame): Raw DataFrame from CSV
            
        Returns:
            tuple: (Transformed DataFrame, metadata dict)
        """
        # Identify the header rows structure
        # Row 0: Column headers including L1, L2, etc.
        # Row 1: Time ranges for each level
        # Row 2+: Actual data
        
        level_columns = {}
        length_ranges = {}
        column_mapping = {}
        
        # First pass: identify level columns from the header row (row 0)
        if len(df) >= 2:  # We need at least header and time range rows
            headers = df.columns
            
            for col_idx, col_name in enumerate(headers):
                col_str = str(col_name).strip()
                
                # Check if this is a level column (L1, L2, L3, etc.)
                if col_str.startswith('L') and len(col_str) > 1 and col_str[1:].isdigit():
                    level = col_str
                    if level not in level_columns:
                        level_columns[level] = []
                    
                    # Look at row 1 (index 0 in the dataframe) for time range
                    time_range = df.iloc[0][col_name] if pd.notna(df.iloc[0][col_name]) else None
                    
                    if time_range and isinstance(time_range, str) and any(keyword in time_range.lower() for keyword in ['phút', 'min']):
                        # This is a valid time range
                        level_columns[level].append((col_idx, time_range, col_name))
                        length_ranges[time_range] = self._parse_length_range(time_range)
                        
                # Also check for Unnamed columns that might have time ranges
                elif 'Unnamed:' in col_str or col_str == '':
                    # Check if row 1 has a time range value
                    time_range = df.iloc[0][col_name] if pd.notna(df.iloc[0][col_name]) else None
                    
                    if time_range and isinstance(time_range, str) and any(keyword in time_range.lower() for keyword in ['phút', 'min']):
                        # Find which level this belongs to by looking at previous columns
                        for prev_idx in range(col_idx - 1, -1, -1):
                            prev_col = headers[prev_idx]
                            if str(prev_col).startswith('L') and str(prev_col)[1:].isdigit():
                                level = str(prev_col)
                                if level not in level_columns:
                                    level_columns[level] = []
                                level_columns[level].append((col_idx, time_range, col_name))
                                length_ranges[time_range] = self._parse_length_range(time_range)
                                break
        
        # Create column mapping
        for level, ranges in level_columns.items():
            for col_idx, time_range, original_col in ranges:
                new_col_name = f"{level} ({time_range})"
                column_mapping[original_col] = new_col_name
        
        # Remove the time range row (row 1) from the DataFrame
        if len(df) > 1:
            df_cleaned = df.iloc[1:].reset_index(drop=True)
        else:
            df_cleaned = df.copy()
        
        # Apply column renaming
        renamed_df = df_cleaned.rename(columns=column_mapping)
        
        # Filter out rows with no valid data (more lenient filtering)
        if "Subtitle Code" in renamed_df.columns and "Project Type" in renamed_df.columns:
            # Keep rows that have either a valid subtitle code OR a valid project type
            # This allows rows with empty subtitle codes (common in CLT) but still have meaningful data
            valid_rows = renamed_df.apply(
                lambda row: (pd.notna(row["Subtitle Code"]) and str(row["Subtitle Code"]).strip() != '') or 
                        (pd.notna(row["Project Type"]) and str(row["Project Type"]).strip() != ''),
                axis=1
            )
            filtered_df = renamed_df[valid_rows].reset_index(drop=True)
        else:
            filtered_df = renamed_df
        
        # Convert cost columns to numeric
        for col in filtered_df.columns:
            if any(col.startswith(f"{level} (") for level in level_columns.keys()):
                filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce').fillna(0)
        
        # Extract metadata about detected levels and lengths
        levels = sorted(list(level_columns.keys()))
        lengths = sorted(list(set(time_range for ranges in level_columns.values() for _, time_range, _ in ranges)))
        
        metadata = {
            "levels": levels,
            "lengths": lengths,
            "length_ranges": length_ranges
        }
        
        return filtered_df, metadata

    def _parse_length_range(self, length_str):
        """
        Parse a length string into minimum and maximum minutes.
        
        Args:
            length_str (str): String like "< 15 phút" or "15-30 phút" or "> 60 phút"
            
        Returns:
            tuple: (min_minutes, max_minutes)
        """
        if not length_str:
            return (0, 60)  # Default range
            
        length_str = length_str.lower().strip()
        
        # Handle "< X phút/min" format
        if "<" in length_str:
            import re
            match = re.search(r'<\s*(\d+)', length_str)
            if match:
                max_val = int(match.group(1))
                return (0, max_val - 1)
        
        # Handle "> X phút/min" format
        if ">" in length_str:
            import re
            match = re.search(r'>\s*(\d+)', length_str)
            if match:
                min_val = int(match.group(1))
                return (min_val + 1, 999)  # Using 999 as a practical maximum
        
        # Handle "X-Y phút/min" format
        if "-" in length_str:
            import re
            parts = re.split(r'\s*-\s*', length_str)
            if len(parts) == 2:
                # Extract numbers from each part
                match1 = re.search(r'(\d+)', parts[0])
                match2 = re.search(r'(\d+)', parts[1])
                
                if match1 and match2:
                    min_val = int(match1.group(1))
                    max_val = int(match2.group(1))
                    return (min_val, max_val)
        
        # Try to extract a single number
        import re
        match = re.search(r'(\d+)', length_str)
        if match:
            val = int(match.group(1))
            return (val, val)
        
        # Default fallback
        return (0, 60)
    
    def get_csv_structure(self, file_path):
        """
        Analyze the structure of a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            dict: Information about the CSV structure
        """
        try:
            df = pd.read_csv(file_path)
            
            structure = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "project_type": df.iloc[0, 0] if not df.empty else None,
                "has_required_columns": all(col in df.columns for col in ["Project Type", "Subtitle Code"]),
                "has_l1_l4_columns": all(col in df.columns for col in ["L1", "L2", "L3", "L4"])
            }
            
            return structure
        except Exception as e:
            self.logger.error(f"Failed to analyze CSV structure: {str(e)}")
            return {
                "error": str(e)
            }