# database/db_manager.py
# -*- coding: utf-8 -*-
import sqlite3
import pandas as pd
import os
import logging
import sys
import json
from pathlib import Path

class DatabaseManager:
    """Manages database connections and operations for element costs storage."""
    
    def __init__(self, db_path=None):
        """Initialize the database manager.
        
        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, a default path will be used.
        """
        self.logger = logging.getLogger(__name__)
        
        if db_path is None:
            # Determine if running as bundled executable
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller bundle
                base_path = Path(sys._MEIPASS)
                # First try to use a database from the bundle
                bundled_db = base_path / "database" / "project_costs.db"
                
                # If this is first run, copy the bundled DB to user directory
                data_dir = Path.home() / ".project_cost_calculator"
                data_dir.mkdir(exist_ok=True)
                user_db_path = data_dir / "project_costs.db"
                
                if bundled_db.exists() and not user_db_path.exists():
                    # Copy the bundled DB to user directory
                    import shutil
                    shutil.copy2(str(bundled_db), str(user_db_path))
                    self.logger.info(f"Copied bundled database to: {user_db_path}")
                
                # Always use the user directory DB for actual operations
                db_path = user_db_path
            else:
                # Running in development mode
                # Try local directory first, then fall back to user home
                local_db = Path("database/project_costs.db")
                if local_db.exists():
                    db_path = local_db
                else:
                    data_dir = Path.home() / ".project_cost_calculator"
                    data_dir.mkdir(exist_ok=True)
                    db_path = data_dir / "project_costs.db"
            
        self.db_path = str(db_path)
        self.logger.info(f"Using database at: {self.db_path}")
        
        # Initialize the database
        self._init_database()
        
    def _init_database(self):
        """Initialize the database structure with support for dynamic levels and lengths."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create project_types table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Create base element_costs table without level/length columns
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS element_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_type_id INTEGER NOT NULL,
                subtitle_code TEXT,
                subtitle_1 TEXT,
                subtitle_2 TEXT,
                subtitle_3 TEXT,
                subtitle_4 TEXT,
                subtitle_5 TEXT,
                row_order INTEGER,
                unit TEXT,
                FOREIGN KEY (project_type_id) REFERENCES project_types (id) ON DELETE CASCADE
            )
            ''')
            
            # Create new table for level/length combinations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS element_costs_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element_cost_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                length_min INTEGER NOT NULL,
                length_max INTEGER NOT NULL,
                cost_value REAL,
                FOREIGN KEY (element_cost_id) REFERENCES element_costs (id) ON DELETE CASCADE
            )
            ''')
            
            # Create metadata table to store level and length information for each project type
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_type_id INTEGER NOT NULL,
                levels TEXT NOT NULL,  -- JSON array of levels
                lengths TEXT NOT NULL,  -- JSON array of length ranges
                FOREIGN KEY (project_type_id) REFERENCES project_types (id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully with dynamic level/length support")
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                conn.close()
    
    def _get_connection(self):
        """Get a connection to the database.
        
        Returns:
            sqlite3.Connection: A connection to the SQLite database.
        """
        # Enable foreign key support
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = 1")
        return conn
    
    def get_project_types(self):
        """Get all project types from the database.
        
        Returns:
            list: List of project type names.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM project_types")
            project_types = [row[0] for row in cursor.fetchall()]
            
            return project_types
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting project types: {e}")
            return []
            
        finally:
            if conn:
                conn.close()
    
    def get_project_type_id(self, project_type):
        """Get the ID for a project type.
        
        Args:
            project_type (str): The project type name.
            
        Returns:
            int: The project type ID, or None if not found.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM project_types WHERE name = ?", (project_type,))
            result = cursor.fetchone()
            
            return result[0] if result else None
            
        except sqlite3.Error as e:
            self.logger.error(f"Error getting project type ID: {e}")
            return None
            
        finally:
            if conn:
                conn.close()
    
    def add_project_type(self, project_type):
        """Add a new project type to the database.
        
        Args:
            project_type (str): The project type name.
            
        Returns:
            int: The ID of the new project type, or None if error.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO project_types (name) VALUES (?)", (project_type,))
            conn.commit()
            
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            self.logger.error(f"Error adding project type: {e}")
            if conn:
                conn.rollback()
            return None
            
        finally:
            if conn:
                conn.close()
    
    def delete_project_type(self, project_type):
        """Delete a project type and all its element costs.
        
        Args:
            project_type (str): The project type name.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM project_types WHERE name = ?", (project_type,))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting project type: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if conn:
                conn.close()
    
    def get_element_costs(self, project_type):
        """
        Get all element costs for a project type with dynamic level/length support.
        
        Args:
            project_type (str): The project type name
            
        Returns:
            tuple: (DataFrame of costs, metadata dict) or (None, None) if error
        """
        conn = None
        try:
            conn = self._get_connection()
            
            # Get project type ID
            project_type_id = self.get_project_type_id(project_type)
            if project_type_id is None:
                return None, None
            
            # Get metadata for this project type
            cursor = conn.cursor()
            cursor.execute(
                "SELECT levels, lengths FROM project_metadata WHERE project_type_id = ?",
                (project_type_id,)
            )
            
            metadata_row = cursor.fetchone()
            if metadata_row is None:
                self.logger.warning(f"No metadata found for project type {project_type}")
                return None, None
            
            levels = json.loads(metadata_row[0])
            lengths = json.loads(metadata_row[1])
            
            # Create length_ranges dictionary
            length_ranges = {}
            for length in lengths:
                length_ranges[length] = self._parse_length_range(length)
            
            metadata = {
                "levels": levels,
                "lengths": lengths,
                "length_ranges": length_ranges
            }
            
            # Fetch base element costs
            base_query = """
            SELECT 
                e.id,
                '{0}' as "Project Type",
                e.subtitle_1 as "Subtitle 1",
                e.subtitle_2 as "Subtitle 2",
                e.subtitle_3 as "Subtitle 3",
                e.subtitle_4 as "Subtitle 4",
                e.subtitle_5 as "Subtitle 5",
                e.subtitle_code as "Subtitle Code",
                e.unit as "Unit",
                e.row_order
            FROM element_costs e
            WHERE e.project_type_id = ?
            ORDER BY e.row_order
            """.format(project_type)
            
            base_df = pd.read_sql_query(base_query, conn, params=(project_type_id,))
            
            if base_df.empty:
                return base_df, metadata
            
            # Fetch cost values for each element
            for level in levels:
                for length in lengths:
                    # Create column name
                    col_name = f"{level} ({length})"
                    base_df[col_name] = 0.0  # Initialize with zeros
            
            # Fetch all cost values
            values_query = """
            SELECT 
                e.id as element_id,
                v.level,
                v.length_min,
                v.length_max,
                v.cost_value
            FROM element_costs e
            JOIN element_costs_values v ON e.id = v.element_cost_id
            WHERE e.project_type_id = ?
            """
            
            values_df = pd.read_sql_query(values_query, conn, params=(project_type_id,))
            
            # Map each cost value to the appropriate column
            for _, value_row in values_df.iterrows():
                element_id = value_row['element_id']
                level = value_row['level']
                min_length = value_row['length_min']
                max_length = value_row['length_max']
                cost_value = value_row['cost_value']
                
                # Find the matching length range
                matching_length = None
                for length in lengths:
                    range_min, range_max = length_ranges.get(length, (0, 60))
                    if min_length == range_min and max_length == range_max:
                        matching_length = length
                        break
                
                if matching_length:
                    col_name = f"{level} ({matching_length})"
                    # Find the row index for this element_id
                    row_idx = base_df[base_df['id'] == element_id].index
                    if not row_idx.empty:
                        base_df.at[row_idx[0], col_name] = cost_value
            
            # Remove the id column as it's not needed in the result
            if 'id' in base_df.columns:
                base_df = base_df.drop(columns=['id'])
            
            # Hide row_order column from the result if needed
            if "row_order" in base_df.columns:
                base_df = base_df.drop(columns=["row_order"])

            return base_df, metadata
            
        except (sqlite3.Error, pd.io.sql.DatabaseError) as e:
            self.logger.error(f"Error getting element costs: {e}")
            return None, None
            
        finally:
            if conn:
                conn.close()

    def update_element_cost(self, project_type, subtitle_code, classification, interview_length, value):
        """
        Update a specific element cost with dynamic level/length support.
        
        Args:
            project_type (str): The project type name
            subtitle_code (str): The subtitle code
            classification (str): The classification (L1, L2, L3, L4, etc.)
            interview_length (str): The interview length category or minutes
            value (float): The new cost value
            
        Returns:
            bool: True if successful, False otherwise
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get project type ID
            project_type_id = self.get_project_type_id(project_type)
            if project_type_id is None:
                return False
            
            # Get the element cost ID
            cursor.execute(
                "SELECT id FROM element_costs WHERE project_type_id = ? AND subtitle_code = ?",
                (project_type_id, subtitle_code)
            )
            result = cursor.fetchone()
            if result is None:
                return False
                
            element_cost_id = result[0]
            
            # Parse the interview length to get min and max values
            min_length, max_length = self._parse_length_range(interview_length)
            
            # Check if this level/length combination already exists
            cursor.execute(
                """
                SELECT id FROM element_costs_values 
                WHERE element_cost_id = ? AND level = ? AND length_min = ? AND length_max = ?
                """,
                (element_cost_id, classification, min_length, max_length)
            )
            
            result = cursor.fetchone()
            
            if result:
                # Update existing value
                cursor.execute(
                    """
                    UPDATE element_costs_values SET cost_value = ?
                    WHERE element_cost_id = ? AND level = ? AND length_min = ? AND length_max = ?
                    """,
                    (value, element_cost_id, classification, min_length, max_length)
                )
            else:
                # Insert new value
                cursor.execute(
                    """
                    INSERT INTO element_costs_values (element_cost_id, level, length_min, length_max, cost_value)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (element_cost_id, classification, min_length, max_length, value)
                )
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Error updating element cost: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if conn:
                conn.close()
    
    def save_element_costs(self, project_type, df, metadata=None):
        """
        Save element costs for a project type with dynamic level/length support.
        
        Args:
            project_type (str): The project type name
            df (pandas.DataFrame): DataFrame containing element costs
            metadata (dict): Metadata about levels and lengths
            
        Returns:
            bool: True if successful, False otherwise
        """
        if df is None or df.empty:
            self.logger.warning(f"Cannot save empty element costs for {project_type}")
            return False
        
        if metadata is None:
            # Try to extract metadata from DataFrame columns
            metadata = {
                "levels": [],
                "lengths": [],
                "length_ranges": {}
            }
            
            for col in df.columns:
                if " (" in col and col.startswith("L"):
                    level, length = col.split(" (", 1)
                    length = length.rstrip(")")
                    if level not in metadata["levels"]:
                        metadata["levels"].append(level)
                    if length not in metadata["lengths"]:
                        metadata["lengths"].append(length)
                        metadata["length_ranges"][length] = self._parse_length_range(length)
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get or create project type
            project_type_id = self.get_project_type_id(project_type)
            if project_type_id is None:
                project_type_id = self.add_project_type(project_type)
                if project_type_id is None:
                    return False
            
            # Save metadata for this project type
            cursor.execute(
                "DELETE FROM project_metadata WHERE project_type_id = ?",
                (project_type_id,)
            )
            
            cursor.execute(
                "INSERT INTO project_metadata (project_type_id, levels, lengths) VALUES (?, ?, ?)",
                (project_type_id, json.dumps(metadata["levels"]), json.dumps(metadata["lengths"]))
            )
            
            # Delete existing costs for this project type
            cursor.execute(
                "DELETE FROM element_costs_values WHERE element_cost_id IN (SELECT id FROM element_costs WHERE project_type_id = ?)",
                (project_type_id,)
            )
            cursor.execute(
                "DELETE FROM element_costs WHERE project_type_id = ?",
                (project_type_id,)
            )
            
            # Insert new costs
            for _, row in df.iterrows():
                # Skip rows without subtitle code
                if pd.isna(row.get("Subtitle Code")):
                    continue
                    
                # Insert base element cost
                cursor.execute(
                    """
                    INSERT INTO element_costs 
                    (project_type_id, subtitle_code, subtitle_1, subtitle_2, subtitle_3, subtitle_4, subtitle_5, row_order, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_type_id,
                        str(row.get("Subtitle Code", "")),
                        str(row.get("Subtitle 1", "")),
                        str(row.get("Subtitle 2", "")),
                        str(row.get("Subtitle 3", "")),
                        str(row.get("Subtitle 4", "")),
                        str(row.get("Subtitle 5", "")),
                        int(row.get("row_order", 0) if "row_order" in row else 0),
                        str(row.get("Unit", ""))
                    )
                )
                
                # Get the ID of the inserted element
                element_cost_id = cursor.lastrowid
                
                # Insert cost values for each level/length combination
                for level in metadata["levels"]:
                    for length in metadata["lengths"]:
                        col_name = f"{level} ({length})"
                        if col_name in row and not pd.isna(row[col_name]):
                            cost_value = float(row[col_name])
                            min_length, max_length = metadata["length_ranges"].get(length, (0, 60))
                            
                            cursor.execute(
                                """
                                INSERT INTO element_costs_values
                                (element_cost_id, level, length_min, length_max, cost_value)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (element_cost_id, level, min_length, max_length, cost_value)
                            )
            
            conn.commit()
            self.logger.info(f"Saved {len(df)} element costs for {project_type} with {len(metadata['levels'])} levels and {len(metadata['lengths'])} length ranges")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Error saving element costs: {e}")
            if conn:
                conn.rollback()
            return False
            
        finally:
            if conn:
                conn.close()

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

    def get_database_stats(self):
        """Get statistics about the database.
        
        Returns:
            dict: Statistics about the database.
        """
        stats = {
            "path": self.db_path,
            "size_bytes": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
            "project_types": [],
            "total_elements": 0
        }
        
        # Get project types and element counts
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.name, COUNT(e.id)
                FROM project_types p
                LEFT JOIN element_costs e ON p.id = e.project_type_id
                GROUP BY p.name
                ORDER BY p.name
            """)
            
            for name, count in cursor.fetchall():
                stats["project_types"].append({"name": name, "elements": count})
                stats["total_elements"] += count
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting database stats: {e}")
            
        finally:
            if conn:
                conn.close()
                
        return stats