
# database/db_migrator.py
# -*- coding: utf-8 -*-
"""
Migration script to convert from fixed levels/lengths schema to dynamic schema.
"""

import sqlite3
import pandas as pd
import logging
import json
import os
import shutil
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("migration")

def migrate_database(db_path):
    """
    Migrate the database from fixed to dynamic level/length schema.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    # Create a backup of the original database
    backup_path = f"{db_path}.bak"
    if os.path.exists(db_path):
        logger.info(f"Creating backup of database at {backup_path}")
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"Backup created successfully")
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return
    else:
        logger.warning(f"Database file not found at {db_path}")
        return

    shutil.copy2(db_path, backup_path)
    
    # Connect to the original database
    old_conn = sqlite3.connect(backup_path)
    old_cursor = old_conn.cursor()
    
    # Create a new database with the updated schema
    if os.path.exists(db_path):
        os.remove(db_path)
    
    new_conn = sqlite3.connect(db_path)
    new_cursor = new_conn.cursor()
    
    # Initialize new schema
    logger.info("Creating new schema")
    new_cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    new_cursor.execute('''
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
    
    new_cursor.execute('''
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
    
    new_cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_type_id INTEGER NOT NULL,
        levels TEXT NOT NULL,  -- JSON array of levels
        lengths TEXT NOT NULL,  -- JSON array of length ranges
        FOREIGN KEY (project_type_id) REFERENCES project_types (id) ON DELETE CASCADE
    )
    ''')
    
    new_conn.commit()
    
    try:
        # Get project types from old database
        old_cursor.execute("SELECT id, name FROM project_types")
        project_types = old_cursor.fetchall()
        
        # Default level and length information for old schema
        default_levels = ["L1", "L2", "L3", "L4"]
        default_lengths = ["<15 min", "15-30 min", "30-45 min", "45-60 min"]
        default_length_ranges = {
            "<15 min": (0, 14),
            "15-30 min": (15, 30),
            "30-45 min": (31, 45),
            "45-60 min": (46, 60)
        }
        
        # Process each project type
        for project_type_id, project_type_name in project_types:
            logger.info(f"Migrating project type: {project_type_name}")
            
            # Insert project type into new database
            new_cursor.execute("INSERT INTO project_types (id, name) VALUES (?, ?)", (project_type_id, project_type_name))
            
            # Save metadata
            new_cursor.execute(
                "INSERT INTO project_metadata (project_type_id, levels, lengths) VALUES (?, ?, ?)",
                (project_type_id, json.dumps(default_levels), json.dumps(default_lengths))
            )
            
            # Get all element costs for this project type
            old_cursor.execute("""
                SELECT * FROM element_costs WHERE project_type_id = ?
            """, (project_type_id,))
            
            columns = [col[0] for col in old_cursor.description]
            element_costs = [dict(zip(columns, row)) for row in old_cursor.fetchall()]
            
            # Process each element cost
            for element in element_costs:
                # Insert the base element information into new schema
                new_cursor.execute("""
                    INSERT INTO element_costs 
                    (id, project_type_id, subtitle_code, subtitle_1, subtitle_2, subtitle_3, subtitle_4, subtitle_5, row_order, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    element["id"], 
                    element["project_type_id"], 
                    element.get("subtitle_code", ""),
                    element.get("subtitle_1", ""),
                    element.get("subtitle_2", ""),
                    element.get("subtitle_3", ""),
                    element.get("subtitle_4", ""),
                    element.get("subtitle_5", ""),
                    element.get("row_order", 0),
                    element.get("unit", "")
                ))
                
                # Map old columns to new level/length combinations
                column_mapping = {
                    "l1_lt15": ("L1", "<15 min", 0, 14),
                    "l1_15_30": ("L1", "15-30 min", 15, 30),
                    "l1_30_45": ("L1", "30-45 min", 31, 45),
                    "l1_45_60": ("L1", "45-60 min", 46, 60),
                    "l2_lt15": ("L2", "<15 min", 0, 14),
                    "l2_15_30": ("L2", "15-30 min", 15, 30),
                    "l2_30_45": ("L2", "30-45 min", 31, 45),
                    "l2_45_60": ("L2", "45-60 min", 46, 60),
                    "l3_lt15": ("L3", "<15 min", 0, 14),
                    "l3_15_30": ("L3", "15-30 min", 15, 30),
                    "l3_30_45": ("L3", "30-45 min", 31, 45),
                    "l3_45_60": ("L3", "45-60 min", 46, 60),
                    "l4_lt15": ("L4", "<15 min", 0, 14),
                    "l4_15_30": ("L4", "15-30 min", 15, 30),
                    "l4_30_45": ("L4", "30-45 min", 31, 45),
                    "l4_45_60": ("L4", "45-60 min", 46, 60),
                }
                
                # Insert cost values for each level/length combination
                for old_col, (level, length, min_len, max_len) in column_mapping.items():
                    if old_col in element and element[old_col] is not None:
                        cost_value = element[old_col]
                        
                        new_cursor.execute("""
                            INSERT INTO element_costs_values
                            (element_cost_id, level, length_min, length_max, cost_value)
                            VALUES (?, ?, ?, ?, ?)
                        """, (element["id"], level, min_len, max_len, cost_value))
            
            # Commit after each project type
            new_conn.commit()
            logger.info(f"Migrated {len(element_costs)} elements for {project_type_name}")
    
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        # Restore from backup
        new_conn.close()
        old_conn.close()
        os.remove(db_path)
        shutil.copy2(backup_path, db_path)
        logger.info(f"Restored from backup due to error")
        raise
    
    finally:
        new_conn.close()
        old_conn.close()
    
    logger.info("Migration completed successfully")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Default path
        db_path = "database/project_costs.db"
    
    migrate_database(db_path)