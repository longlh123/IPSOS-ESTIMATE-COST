# Project Cost Calculator - Technical Documentation

## 1. System Architecture

### 1.1 Overview

The Project Cost Calculator is a desktop application built with Python and PySide6 (Qt for Python). It follows a Model-View architecture pattern where data models are separated from the user interface components. The application is designed to calculate project costs based on various parameters including sample sizes, element costs, and project conditions.

### 1.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Main Window                         │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│ General Tab │ Samples Tab │   QC Tab    │ Conditions Tab   │
├─────────────┴─────────────┼─────────────┼──────────────────┤
│     Element Costs Tab     │ Travel Tab  │ Assignment Tab   │
├─────────────────────────────────────────┴──────────────────┤
│                      Project Model                          │
├───────────────────────────┬─────────────────────────────────┤
│     Element Costs Model    │       Database Manager          │
└───────────────────────────┴─────────────────────────────────┘
```

### 1.3 Directory Structure

```
project_cost_calculator/
├── main.py                        # Entry point
├── config/                        # Configuration files
│   ├── __init__.py
│   ├── predefined_values.py       # Constants and dropdown options
│   └── settings.py                # Application settings
│
├── database/                      # Database management
│   ├── __init__.py
│   ├── db_manager.py              # SQLite database operations
│   └── project_costs.db           # SQLite database file
│
├── models/                        # Data models
│   ├── __init__.py
│   ├── project_model.py           # Central data model
│   └── element_costs_model.py     # Element costs model
│
├── ui/                            # User interface components
│   ├── __init__.py
│   ├── main_window.py             # Main application window
│   ├── general_tab.py             # General project info tab
│   ├── samples_tab.py             # Sample size management tab
│   ├── qc_tab.py                  # QC methods tab
│   ├── conditions_tab.py          # Project conditions tab
│   ├── element_costs_tab.py       # Element costs management tab
│   ├── travel_tab.py              # Travel management tab
│   ├── cost_results_dialog.py     # Cost results display
│   ├── models/                    # UI-specific models
│   │   ├── __init__.py
│   │   └── element_costs_table_model.py
│   ├── dialogs/                   # Dialog windows
│   │   ├── __init__.py
│   │   ├── bulk_import_dialog.py
│   │   ├── database_info_dialog.py
│   │   ├── element_cost_edit_dialog.py
│   │   ├── sample_edit_dialog.py
│   │   ├── settings_dialog.py
│   │   ├── hierarchical_cost_results_dialog.py
│   │   └── assigned_people_dialog.py
│   └── widgets/                   # Custom widgets
│       ├── __init__.py
│       ├── editable_table.py
│       ├── multi_select.py
│       └── assigned_people_widget.py
│
├── utils/                         # Utility functions
│   ├── __init__.py
│   └── element_costs_importer.py  # CSV import utility
│
└── icons/                         # Application icons
    ├── add.png
    ├── bulk_import.png
    ├── calculator.ico
    ├── delete.png
    ├── export.png
    ├── hierarchical_calculate.png
    ├── import.png
    ├── new.png
    ├── open.png
    ├── report.png
    ├── save.png
    └── settings.png
```

### 1.4 Technology Stack

- **Language**: Python 3.8+
- **UI Framework**: PySide6 (Qt for Python)
- **Data Processing**: Pandas, NumPy
- **Database**: SQLite
- **File Formats**: JSON (project files), CSV (element costs)
- **Visualization**: Matplotlib (embedded in Qt)
- **Export**: XLSX (via openpyxl)
- **Distribution**: PyInstaller

## 2. Core Components

### 2.1 Data Models

#### 2.1.1 ProjectModel

The central data model that holds all project information and coordinates with other components.

**Key Responsibilities**:
- Store and manage project data
- Emit signals when data changes
- Provide methods for cost calculation
- Handle data serialization and deserialization

**Key Methods**:
- `to_dict()`: Convert model to dictionary for saving
- `from_dict()`: Load model from dictionary
- `calculate_project_cost()`: Calculate total project cost
- `calculate_hierarchical_project_cost()`: Calculate detailed costs
- `update_general()`, `update_sample()`, etc.: Update specific data sections

**Data Structure**:
```python
self.general = {
    "internal_job": "",
    "symphony": "",
    "project_name": "",
    # ... other general fields
}
self.samples = {
    # Hierarchical structure by province > audience > sample_type
    "province1": {
        "audience1": {
            "sample_type1": {
                "sample_size": 0,
                "price_growth": 0.0,
                "interviewer_target": 0,
                "daily_sup_target": 0.0,
                "comment": {}
            }
        }
    }
}
self.qc_methods = [
    {
        "team": "",
        "method": "",
        "rate": 0.0
    }
]
self.conditions = {
    "age_ranges": [],
    "sex": "male/female",
    "income_ranges": []
}
self.travel = {
    "province1": {
        "fulltime": {
            "travel_days": 0,
            "assigned_people": []
        },
        "parttime": {
            "supervisor": {"distant": 0, "nearby": 0},
            "interviewer": {"distant": 0, "nearby": 0},
            "qc": {"distant": 0, "nearby": 0}
        }
    }
}
self.assignments = [
    {
        "level": "",
        "email": ""
    }
]
```

#### 2.1.2 ElementCostsModel

Model for managing element costs imported from CSV files.

**Key Responsibilities**:
- Load element costs from database
- Import/export element costs from/to CSV
- Provide methods to query and update costs

**Key Methods**:
- `load_costs_from_database()`: Load from SQLite database
- `import_csv()`: Import costs from CSV file
- `export_csv()`: Export costs to CSV file
- `get_cost()`: Get specific cost value
- `update_cost()`: Update specific cost value

**Data Structure**:
```python
self.costs = {
    "project_type1": DataFrame,
    "project_type2": DataFrame,
    # ... more project types
}
```

### 2.2 Database Management

#### 2.2.1 DatabaseManager

Handles SQLite database operations for persistent storage.

**Key Responsibilities**:
- Initialize and manage the SQLite database
- Perform CRUD operations on element costs
- Provide database backup and restore functionality

**Key Methods**:
- `_init_database()`: Create database tables if they don't exist
- `save_element_costs()`: Save element costs to database
- `get_element_costs()`: Retrieve element costs from database
- `get_database_stats()`: Get statistics about the database

**Database Schema**:
```sql
-- Project types table
CREATE TABLE IF NOT EXISTS project_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Element costs table
CREATE TABLE IF NOT EXISTS element_costs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_type_id INTEGER NOT NULL,
    subtitle_code TEXT NOT NULL,
    subtitle_1 TEXT,
    subtitle_2 TEXT,
    subtitle_3 TEXT,
    subtitle_4 TEXT,
    subtitle_5 TEXT,
    unit TEXT,
    l1_lt15 REAL,
    l1_15_30 REAL,
    l1_30_45 REAL,
    l1_45_60 REAL,
    l2_lt15 REAL,
    l2_15_30 REAL,
    l2_30_45 REAL,
    l2_45_60 REAL,
    l3_lt15 REAL,
    l3_15_30 REAL,
    l3_30_45 REAL,
    l3_45_60 REAL,
    l4_lt15 REAL,
    l4_15_30 REAL,
    l4_30_45 REAL,
    l4_45_60 REAL,
    FOREIGN KEY (project_type_id) REFERENCES project_types (id) ON DELETE CASCADE,
    UNIQUE (project_type_id, subtitle_code)
);
```

### 2.3 UI Components

#### 2.3.1 MainWindow

The application's main window that contains the tab widget, menu bar, and toolbar.

**Key Responsibilities**:
- Initialize all UI components
- Handle menu and toolbar actions
- Manage project files (open, save, new)
- Coordinate between tabs

#### 2.3.2 Tab Structure

The application uses a tab-based interface to organize different aspects of project data:

1. **GeneralTab**: Basic project information and dimensions
2. **SamplesTab**: Sample sizes by province, audience, and type
3. **QCMethodTab**: Quality control methods and rates
4. **ProjectConditionsTab**: Demographic targeting
5. **ElementCostsTab**: Element costs management
6. **TravelTab**: Travel management for provinces

#### 2.3.3 Custom Widgets

The application includes several custom widgets:

- **MultiSelectWidget**: Widget for selecting multiple items from a list
- **EditableTable**: Table widget with editing capabilities
- **AssignedPeopleWidget**: Widget for selecting people to assign

#### 2.3.4 Dialogs

The application includes several dialog windows:

- **BulkImportDialog**: Dialog for bulk importing element costs
- **ElementCostEditDialog**: Dialog for editing element costs
- **SampleEditDialog**: Dialog for editing sample properties
- **DatabaseInfoDialog**: Dialog to display database information
- **HierarchicalCostResultsDialog**: Dialog for displaying detailed costs

## 3. Data Flow and Processing

### 3.1 Project Data Flow

1. User inputs data in UI tabs
2. Tab components update ProjectModel
3. ProjectModel emits dataChanged signal
4. UI components update their display based on signals
5. Changes are saved to JSON when user saves the project

### 3.2 Element Costs Data Flow

1. User imports CSV files
2. ElementCostsImporter processes the files
3. Data is stored in ElementCostsModel
4. ElementCostsModel saves to database via DatabaseManager
5. ElementCostsTableModel presents data in UI

### 3.3 Cost Calculation Process

#### 3.3.1 Basic Cost Calculation

1. User triggers calculation
2. ProjectModel aggregates data from all sections
3. Calculation method applies rules to each component
4. Results are displayed in CostResultsDialog

#### 3.3.2 Hierarchical Cost Calculation

1. User triggers hierarchical calculation
2. ProjectModel builds a hierarchical cost structure
3. Costs are organized by province and subtitle categories
4. Calculation applies complex rules based on element properties
5. Results are displayed in HierarchicalCostResultsDialog

### 3.4 CSV Import Process

1. User selects CSV file(s)
2. ElementCostsImporter reads and validates file
3. Data is transformed into the correct format
4. ElementCostsModel stores the data
5. Data is saved to database

## 4. Application Workflows

### 4.1 Creating a New Project

1. User selects "New Project" from menu or toolbar
2. ProjectModel is reset to default values
3. User fills in General tab information
4. User selects dimensions (provinces, audiences, sample types)
5. User moves to Samples tab to enter sample sizes
6. User defines QC methods in QC tab
7. User sets demographic conditions in Conditions tab
8. User optionally manages travel assignments
9. User saves the project

### 4.2 Calculating Project Costs

1. User completes project data entry
2. User ensures element costs are imported
3. User clicks "Calculate" button
4. ProjectModel performs calculations
5. Results are displayed in CostResultsDialog
6. User can view charts and detailed breakdowns

### 4.3 Managing Element Costs

1. User navigates to Element Costs tab
2. User selects project type
3. User imports element costs from CSV
4. User can edit individual costs by double-clicking
5. User can filter and search for specific costs
6. Changes are automatically saved to database

## 5. Cost Calculation Logic

### 5.1 Cost Components

The total project cost is calculated as the sum of several components:

1. **Base Cost**: Fixed base fee from settings
2. **Sample Cost**: Based on sample sizes and price growth rates
3. **Element Cost**: Based on imported element costs and classification
4. **HUT Cost**: Calculated from HUT test products and usage duration
5. **CLT Cost**: Calculated from CLT parameters
6. **Print Cost**: Based on printing requirements
7. **QC Cost**: Based on QC methods and rates

### 5.2 Hierarchical Cost Calculation

The hierarchical cost calculation provides a more detailed breakdown:

1. **Province-Specific Costs**: Costs are calculated per province
2. **Subtitle Hierarchy**: Costs are organized by subtitle hierarchy
3. **Element Properties**: Calculation rules depend on:
   - First subtitle category (INTERVIEWER, SUPERVISOR, QC, etc.)
   - Element cost name (subtitle 5)
   - Unit type
   - Target audience
   - Sample sizes

### 5.3 Key Calculation Rules

The application applies specific rules for different cost categories:

#### 5.3.1 INTERVIEWER Category

- Sample size based on sample type
- Special handling for "thuê tablet" based on platform
- Parking fees from settings
- Distant district support from settings

#### 5.3.2 SUPERVISOR Category

- Based on daily supervisor targets
- Excludes Pilot sample type for management costs

#### 5.3.3 QC Category

- Applies QC rates from QC methods
- Special handling for tablet costs
- Management costs based on total sample size

#### 5.3.4 TRAVEL Category

- Fulltime travel based on assigned people
- Costs vary by level (Junior, Senior, Manager, Director)
- Parttime travel for distant and nearby districts

## 6. File Formats

### 6.1 Project JSON Format

Projects are saved as JSON files with the following structure:

```json
{
  "general": {
    "internal_job": "...",
    "symphony": "...",
    "project_name": "...",
    "...": "..."
  },
  "samples": {
    "province1": {
      "audience1": {
        "sample_type1": {
          "sample_size": 100,
          "price_growth": 5.0,
          "interviewer_target": 2,
          "daily_sup_target": 6.25,
          "comment": {
            "price_growth": "Increased due to complexity"
          }
        }
      }
    }
  },
  "qc_methods": [
    {
      "team": "QC",
      "method": "QC tai nha",
      "rate": 10.0
    }
  ],
  "conditions": {
    "age_ranges": [[18, 35], [36, 50]],
    "sex": "male/female",
    "income_ranges": [[5000000, 10000000]]
  },
  "travel": {
    "province1": {
      "fulltime": {
        "travel_days": 5,
        "assigned_people": ["user1@example.com", "user2@example.com"]
      },
      "parttime": {
        "supervisor": {"distant": 2, "nearby": 3},
        "interviewer": {"distant": 10, "nearby": 20},
        "qc": {"distant": 1, "nearby": 2}
      }
    }
  },
  "assignments": [
    {
      "level": "Senior",
      "email": "user1@example.com"
    }
  ],
  "settings": {
    "interviewers_per_supervisor": 8,
    "bw_photo_fee": 250,
    "...": "..."
  }
}
```

### 6.2 Element Costs CSV Format

Element costs are imported from CSV files with the following structure:

| Project Type | Subtitle 1 | Subtitle 2 | ... | Subtitle Code | Unit | L1 | L1 (15-30) | ... | L4 (45-60) |
|-------------|------------|------------|-----|--------------|------|-------|-----------|-----|-----------|
| F2F/D2D | INTERVIEWER | FW | ... | 1.1 | Per person | 200000 | 300000 | ... | 800000 |

- First row: Headers (may vary in naming)
- First column: Project type
- Subtitle columns: Hierarchical categorization
- Cost columns: 16 columns (4 classifications × 4 time ranges)

## 7. Deployment

### 7.1 Requirements

- Python 3.8 or higher
- Required libraries:
  - PySide6 (≥ 6.4.0)
  - pandas (≥ 1.5.0) 
  - openpyxl (≥ 3.0.10)
  - matplotlib (≥ 3.6.0)

### 7.2 Packaging with PyInstaller

To create a distributable package with PyInstaller:

```python
# project_cost_calculator.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 ('icons/*', 'icons/'),
                 ('database/project_costs.db', 'database/'),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='ProjectCostCalculator',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ProjectCostCalculator')
```

Run PyInstaller with:
```
pyinstaller project_cost_calculator.spec
```

The executable and all dependencies will be in the `dist/ProjectCostCalculator` directory.

### 7.3 Database Handling in Deployed Application

When deploying the application, the database handling requires special attention:

```python
def __init__(self, db_path=None):
    self.logger = logging.getLogger(__name__)
    
    if db_path is None:
        # Determine if running as bundled executable
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            base_path = Path(sys._MEIPASS)
            bundled_db = base_path / "database" / "project_costs.db"
            
            # Create user data directory
            data_dir = Path.home() / ".project_cost_calculator"
            data_dir.mkdir(exist_ok=True)
            user_db_path = data_dir / "project_costs.db"
            
            # Copy bundled DB to user directory on first run
            if bundled_db.exists() and not user_db_path.exists():
                import shutil
                shutil.copy2(str(bundled_db), str(user_db_path))
                self.logger.info(f"Copied bundled database to: {user_db_path}")
            
            # Use user directory DB for operations
            db_path = user_db_path
        else:
            # Development mode - try local first, then home
            local_db = Path("database/project_costs.db")
            if local_db.exists():
                db_path = local_db
            else:
                data_dir = Path.home() / ".project_cost_calculator"
                data_dir.mkdir(exist_ok=True)
                db_path = data_dir / "project_costs.db"
    
    self.db_path = str(db_path)
    self.logger.info(f"Using database at: {self.db_path}")
```

This approach:
1. Detects if running as PyInstaller bundle
2. Copies the bundled database to user directory on first run
3. Uses the user directory database for all operations
4. Maintains backward compatibility with development mode

### 7.4 Directory Structure of Deployed Application

```
ProjectCostCalculator/
├── ProjectCostCalculator.exe     # Main executable
├── python3.dll                   # Python DLL
├── PySide6/                      # PySide6 libraries and plugins
│   └── ...
├── database/                     # Database directory
│   └── project_costs.db          # SQLite database
├── icons/                        # Application icons
│   └── ...
└── ...                           # Other dependencies
```

## 8. Extension and Customization

### 8.1 Adding New Cost Categories

To add new cost categories:

1. Update `predefined_values.py` with new constants
2. Extend CSV import functionality in `element_costs_importer.py`
3. Add new calculation logic in `_calculate_coefficient_by_rules()` in `project_model.py`
4. Update UI components to display new categories

### 8.2 Modifying Calculation Rules

To modify calculation rules:

1. Locate the relevant calculation method in `project_model.py`
2. Modify the logic in methods like:
   - `_calculate_interviewer_coefficient()`
   - `_calculate_supervisor_coefficient()`
   - `_calculate_qc_coefficient()`
3. Update any constants in `settings.py`

### 8.3 Adding New UI Features

To add new UI features:

1. Create new widget or dialog in the `ui` directory
2. Add it to the main window or appropriate tab
3. Connect it to the project model
4. Update menu and toolbar actions if needed

## 9. Troubleshooting

### 9.1 Common Issues

#### 9.1.1 Database Issues

- **Database not found**: Check user directory permissions
- **Database corruption**: Use the backup/restore function
- **Sqlite3 operational error**: Check file locks, close and reopen app

#### 9.1.2 CSV Import Issues

- **CSV parsing error**: Check CSV format, encoding, and delimiter
- **Duplicate subtitle codes**: CSV contains duplicate identifiers
- **Missing columns**: CSV format doesn't match expected format

#### 9.1.3 Calculation Issues

- **Zero costs**: Check if element costs are imported correctly
- **Incorrect results**: Verify sample sizes and QC rates
- **Missing results**: Check that all required fields are filled

### 9.2 Logging

The application uses Python's logging module:

```python
# Log file locations
# Windows: %USERPROFILE%\debug.log
# macOS/Linux: ~/debug.log

# Log levels
# DEBUG: Detailed information for debugging
# INFO: Confirmation that things are working as expected
# WARNING: Indication of potential issues
# ERROR: Error that prevented a function from working
# CRITICAL: Critical error that may prevent the program from continuing
```

### 9.3 Data Recovery

1. **Project files**: JSON files can be edited manually if corrupted
2. **Database**: Use the backup/restore function in Database Info dialog
3. **Settings**: Reset to defaults by deleting the settings file

## Appendix A: API Reference

### A.1 Project Model API

Key methods of the ProjectModel class:

```python
# Data management
reset()                          # Reset to initial state
to_dict()                        # Convert to dictionary
from_dict(data)                  # Load from dictionary

# Data updates
update_general(field, value)     # Update general field
update_sample(province, audience, sample_type, field, value, comment=None)
add_qc_method(team, method, rate)
remove_qc_method(index)
add_age_range(min_age, max_age)
set_sex(sex)
add_income_range(min_income, max_income)
update_travel(province, category, sub_category, field, value)

# Cost calculation
calculate_project_cost()         # Basic calculation
calculate_hierarchical_project_cost()  # Detailed calculation
```

### A.2 Element Costs Model API

Key methods of the ElementCostsModel class:

```python
# Database operations
load_costs_from_database()      # Load from SQLite
import_csv(file_path)           # Import from CSV
export_csv(project_type, file_path)  # Export to CSV

# Data access
get_project_types()             # Get list of project types
get_subtitles(project_type)     # Get list of subtitles
get_cost(project_type, subtitle_code, classification, interview_length)

# Data updates
update_cost(project_type, subtitle_code, classification, interview_length, value)
add_project_type(project_type)  # Add new project type
delete_project_type(project_type)  # Delete project type
```

### A.3 Database Manager API

Key methods of the DatabaseManager class:

```python
# Table operations
get_project_types()              # Get all project types
get_project_type_id(project_type)  # Get ID for a project type
add_project_type(project_type)   # Add a new project type
delete_project_type(project_type)  # Delete a project type

# Element costs operations
get_element_costs(project_type)  # Get costs for a project type
save_element_costs(project_type, df)  # Save costs for a project type
update_element_cost(project_type, subtitle_code, classification, interview_length, value)

# Database information
get_database_stats()             # Get database statistics
```

## Appendix B: Signals and Slots

### B.1 Project Model Signals

- `dataChanged`: Emitted when any project data changes

### B.2 Element Costs Model Signals

- `costsChanged`: Emitted when element costs change

### B.3 UI Component Signals and Slots

- Tab components connect to `project_model.dataChanged`
- EditableTable emits `dataChanged(row, column, value)`
- MultiSelectWidget emits `selectionChanged(items)`
- CostResultsDialog connects to element costs signals