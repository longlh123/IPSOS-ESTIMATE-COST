# Project Cost Calculator

## Overview

The Project Cost Calculator is a comprehensive desktop application designed specifically for market research project managers at IPSOS. It enables users to define detailed project parameters and automatically calculate associated costs, streamlining the project planning and budgeting process.

This application provides an intuitive user interface for capturing project specifications, managing sample sizes, defining quality control methods, setting demographic conditions, and importing element costs. The application then performs complex calculations to determine the total project cost and provide detailed breakdowns by province and cost category.

## Features

- **Comprehensive Project Definition**: Define project parameters including project type, sampling method, interview details, and more
- **Sample Size Management**: Manage sample sizes by province, target audience, and sample type with dynamic pricing
- **Quality Control Configuration**: Define and manage QC methods and rates for different teams
- **Demographic Targeting**: Set age ranges, sex, and income ranges for project conditions
- **Element Costs Management**:
  - Import element costs from CSV files
  - Bulk import from multiple files
  - Filter and search capabilities
  - Direct cost editing
- **Cost Calculation**:
  - Automatic calculation of project costs based on all parameters
  - Detailed breakdown by cost component
  - Visual representations with charts
  - Hierarchical cost calculation with province-specific details
- **Data Export**:
  - Export calculation results to Excel
  - Export element costs to CSV
- **Database Management**:
  - Built-in SQLite database for persistent storage
  - Database backup and restore functionality

## System Requirements

- Windows 7/8/10/11 (64-bit)
- 4GB RAM (8GB recommended)
- 500MB free disk space
- 1366x768 screen resolution (1920x1080 recommended)

## Installation

### Option 1: Install from Source

1. Ensure you have Python 3.8+ installed
2. Clone or download the source code
3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python main.py
   ```

### Option 2: Build Your Own Executable with PyInstaller

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create a spec file named `project_cost_calculator.spec`:
   ```python
   # -*- mode: python ; coding: utf-8 -*-

   block_cipher = None

   a = Analysis(['main.py'],
                pathex=['.'],
                binaries=[],
                datas=[
                    ('icons/*', 'icons/'),
                    ('database/*.db', 'database/'),
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

3. Run PyInstaller:
   ```
   pyinstaller project_cost_calculator.spec
   ```

4. The executable and all dependencies will be in the `dist/ProjectCostCalculator` directory
5. Copy any additional resources manually if needed, such as sample data files

## Quick Start Guide

1. **General Tab**: Enter basic project information and define dimensions
2. **Samples Tab**: Set sample sizes for each province, target audience, and sample type
3. **QC Method Tab**: Define quality control methods and rates
4. **Project Conditions Tab**: Set demographic targeting parameters
5. **Element Costs Tab**: Import or manage element costs
6. **Calculate Costs**: Click the "Calculate" button in the toolbar to see results

## Data Structure

### Project Files

Projects are saved as JSON files with the following structure:
- General project information
- Sample size data by province, audience, and type
- QC methods and rates
- Project conditions (demographics)
- References to element costs

### Element Costs CSV Format

Element costs are imported from CSV files with the following structure:
- Project Type identifier
- Subtitle hierarchy (5 levels)
- Subtitle Code (unique identifier)
- Unit of measurement
- Cost columns for each classification (L1-L4) and interview length

## Database

The application uses an SQLite database to store element costs. The database is located at:
- Windows: `C:\Users\[Username]\.project_cost_calculator\project_costs.db`
- macOS/Linux: `~/.project_cost_calculator/project_costs.db`

You can manage the database through the application's "Database Info" dialog.

## Development

### Project Structure

```
project_cost_calculator/
├── main.py                       # Entry point
├── config/                       # Configuration layer
│   ├── predefined_values.py      # All dropdown lists and fixed options
│   └── settings.py               # Application settings and calculation constants
├── database/                     # Database layer
│   ├── __init__.py
│   └── db_manager.py             # SQLite database management
├── models/                       # Data layer
│   ├── project_model.py          # Central data model with signal handling
│   └── element_costs_model.py    # Model for handling element costs
├── ui/                           # UI layer
│   ├── main_window.py            # Main application window
│   ├── general_tab.py            # Tab 1: General project information
│   ├── samples_tab.py            # Tab 2: Sample size management
│   ├── qc_tab.py                 # Tab 3: QC methods configuration
│   ├── conditions_tab.py         # Tab 4: Project conditions
│   ├── element_costs_tab.py      # Tab 5: Element costs management
│   ├── travel_tab.py             # Tab for travel management
│   ├── dialogs/                  # Additional dialogs
│   │   └── ...
│   ├── models/                   # UI-specific models
│   │   └── element_costs_table_model.py
│   └── widgets/                  # Custom UI components
│       └── ...
└── utils/                        # Utility functions and classes
    └── element_costs_importer.py # Utility for importing and processing costs
```

### Architecture

The application implements a clean Model-View pattern with distinct separation of concerns:

1. **Model Layer**: Manages data and business logic
   - Project data storage
   - Element cost calculations
   - Database interaction

2. **View Layer**: Handles user interface
   - Tab-based interface
   - Dialogs for specific operations
   - Custom widgets for specialized input

3. **Signal-Slot Communication**: Qt's event system connects models and views
   - Models emit signals when data changes
   - Views listen for signals and update accordingly

### Design Patterns

The application implements several design patterns:

1. **Model-View Pattern**: Separation of data (models) from presentation (UI)
2. **Signal-Slot Communication**: Qt's event system for updating UI when model changes
3. **Dependency Injection**: Project model shared across all tabs
4. **Factory Methods**: Used for widget creation in tabs
5. **Command Pattern**: For undo/redo functionality (future implementation)

### 1.4 Core Data Models

#### 1.4.1 ProjectModel

The central data store with signals to notify UI of changes:

```python
class ProjectModel(QObject):
    """Central model class that stores all project data and emits signals when data changes."""
    
    dataChanged = Signal()  # Signal emitted whenever data changes
    
    def __init__(self):
        self.general = {}         # Tab 1 data (general project info)
        self.samples = {}         # Tab 2 data (sample sizes by dimensions)
        self.qc_methods = []      # Tab 3 data (QC methods and rates)
        self.conditions = {}      # Tab 4 data (demographic conditions)
        self.element_costs = ElementCostsModel()  # Tab 5 data (element costs)
```

#### 1.4.2 ElementCostsModel

Specialized model for handling element costs from CSV files:

```python
class ElementCostsModel(QObject):
    """Model for managing element costs for different project types."""
    
    costsChanged = Signal()  # Signal emitted when costs change
    
    def __init__(self):
        self.costs = {}  # {project_type: DataFrame of costs}
```

### 1.5 Data Flow

1. User inputs data in the UI tabs
2. Tab controllers update the relevant section in ProjectModel
3. ProjectModel emits `dataChanged` signal
4. UI components listen for signals and update their display
5. For cost calculations, ProjectModel aggregates data from all sections
6. Calculation results are displayed in the Cost Results Dialog

## 2. UI Description

### 2.1 Main Window

The main window serves as the container for all application components:

- **Window Title**: "Project Cost Calculator"
- **Default Size**: 1100 × 800 pixels
- **Components**:
  - Menu Bar
  - Toolbar
  - Tab Widget
  - Status Bar

#### 2.1.1 Menu Bar

- **File Menu**:
  - New Project (Ctrl+N)
  - Open Project (Ctrl+O)
  - Save Project (Ctrl+S)
  - Import Element Costs
  - Export Element Costs
  - Exit (Ctrl+Q)

- **Calculate Menu**:
  - Calculate Cost (F5)
  - Generate Report (F6)

- **Help Menu**:
  - About

#### 2.1.2 Toolbar

- New Project button
- Open Project button
- Save Project button
- Import Element Costs button
- Calculate Cost button
- Generate Report button

#### 2.1.3 Status Bar

Displays information about:
- Current project name
- Number of element costs project types loaded
- Operation status messages

### 2.2 Tab Structure

The application is organized into five main tabs:

1. **General Tab**: Basic project information and dimensions
2. **Samples Tab**: Sample sizes by province, audience, and type
3. **QC Method Tab**: Quality control methods and rates
4. **Project Conditions Tab**: Demographic targeting
5. **Element Costs Tab**: Element costs management

### 2.3 Tab Details

#### 2.3.1 General Tab

Contains project basics, interview details, and dimension selection:

**Region 1 - General Information**:
- Internal job: String input
- Symphony: String input
- Project name: String input
- Project type: Dropdown list
- Sampling method: Dropdown list
- Resp. Classification: Dropdown list (L1, L2, L3, L4)
- Length of interview: Integer input (minutes)
- Length of questionnaire: Integer input
- Open-ended questions count: Integer input
- Interview method: Multi-select dropdown
- Service line: Dropdown list
- Industry: Multi-select dropdown (dependent on service line)
- Province: Multi-select dropdown (63 provinces in Vietnam)
- Target audience: Multi-select dropdown
- Sample types: Multi-select dropdown

**Region 2 - HUT (Home Use Test)**:
- Number of test products: Integer input
- Product usage duration (days): Integer input

**Region 3 - CLT (Central Location Test)**:
- Number of test products: Integer input
- Number of respondent visits to CLT location: Integer input
- Sample size target per day of CLT: Integer input

**Region 4 - Printer**:
- SHOWCARD page count: Integer input
- DROPCARD page count: Integer input
- COLOR page count: Integer input
- Laminated page count: Integer input

#### 2.3.2 Samples Tab

Dynamic table for entering sample sizes and price growth rates:

- **Structure**: Each province selected in General Tab gets its own region
- **Content per Province**:
  - Table with M × N rows, where:
    - M = number of target audiences selected
    - N = number of sample types selected
  - Four columns:
    - Target audience
    - Sample type
    - Sample size (integer input)
    - Price growth rate (percentage input)

#### 2.3.3 QC Method Tab

Table for managing Quality Control methods:

- Three-column table:
  - Team: Dropdown selection
  - QC method: Dropdown selection
  - QC rate: Percentage input
- Add/Remove buttons for managing rows
- Validation to prevent duplicate entries

#### 2.3.4 Project Conditions Tab

Demographic targeting for the project:

- **Ages**: Multiple age ranges can be added
  - Min age: Integer input
  - Max age: Integer input
  - Add/Remove buttons
- **Sex**: Radio button selection
  - Male
  - Female
  - Male/Female
- **Income**: Multiple income ranges can be added
  - Min income: Integer input
  - Max income: Integer input
  - Add/Remove buttons

#### 2.3.5 Element Costs Tab

Management of element costs imported from CSV files:

- **Header Controls**:
  - Project Type selector: Dropdown
  - Add/Delete Project Type buttons
  - Import/Export/Bulk Import buttons

- **Filter Controls**:
  - Filter by Subtitle: Dropdown
  - Search: Text input
  - Reset Filters button

- **Costs Table**:
  - Columns:
    - Project Type
    - Subtitle 1-5
    - Subtitle Code
    - Unit
    - L1 (<15 min), L1 (15-30 min), L1 (30-45 min), L1 (45-60 min)
    - L2 (<15 min), L2 (15-30 min), L2 (30-45 min), L2 (45-60 min)
    - L3 (<15 min), L3 (15-30 min), L3 (30-45 min), L3 (45-60 min)
    - L4 (<15 min), L4 (15-30 min), L4 (30-45 min), L4 (45-60 min)
  - Double-click on cost values to edit them

### 2.4 Dialogs

#### 2.4.1 Cost Results Dialog

Displays calculation results:

- **Header**: Title and total cost display
- **Tabs**:
  - **Summary Tab**: Table with cost breakdown
    - Base Cost
    - Sample Cost
    - Element Cost
    - HUT Cost
    - CLT Cost
    - Print Cost
    - QC Cost
  - **Charts Tab**: Visual representation of costs
    - Pie chart showing cost distribution
    - Bar chart showing cost components
- **Buttons**:
  - Export Results (future implementation)
  - Close

#### 2.4.2 Element Cost Edit Dialog

For editing individual element costs:

- **Element Information**:
  - Subtitle Code (read-only)
  - Subtitle Name (read-only)
- **Cost Editor**:
  - Classification: Dropdown (L1, L2, L3, L4)
  - Interview Length: Dropdown (<15 min, 15-30 min, 30-45 min, 45-60 min)
  - Cost Value: Numeric input with VND suffix
- **Buttons**:
  - Save
  - Cancel

#### 2.4.3 Bulk Import Dialog

For importing multiple CSV files at once:

- **File Selection**:
  - File list
  - Add Files button
  - Add Directory button
  - Remove Selected button
  - Clear All button
- **Progress Bar**: Shows import progress
- **Buttons**:
  - Import
  - Cancel

## 3. CSV File Structure

### 3.1 Element Costs CSV

The element costs CSV files have the following structure:

- **First Column** (Project Type): Identifies the project type
- **Subtitle Columns**:
  - Subtitle 1: Main category
  - Subtitle 2-5: Sub-categories (optional)
  - Subtitle Code: Unique identifier for the cost element
  - Unit: Unit of measurement
- **Cost Columns** (16 columns):
  - Four columns for each classification level (L1-L4)
  - For each classification, columns for different interview lengths:
    - <15 minutes
    - 15-30 minutes
    - 30-45 minutes
    - 45-60 minutes

Example:
```
Project Type, Subtitle 1, Subtitle 2, Subtitle 3, Subtitle 4, Subtitle 5, Subtitle Code, Unit, L1, Unnamed: 9, Unnamed: 10, Unnamed: 11, L2, ...
Quanti, Field, Telephone Interviewers, , , , 1.1, Per interviewer, 200000, 300000, 400000, 500000, 250000, ...
```

## 4. Cost Calculation Logic

The project cost calculation is performed by the `calculate_project_cost` method in the `ProjectModel` class:

```python
def calculate_project_cost(self):
    """Calculate the total project cost."""
    # Base fee
    base_cost = COST_CONSTANTS["base_fee"]
    
    # Calculate component costs
    sample_cost = self._calculate_sample_costs()
    element_cost = self._calculate_element_costs()
    hut_cost = self._calculate_hut_costs()
    clt_cost = self._calculate_clt_costs()
    print_cost = self._calculate_printing_costs()
    qc_cost = self._calculate_qc_costs()
    
    # Calculate total cost
    total_cost = base_cost + sample_cost + element_cost + hut_cost + clt_cost + print_cost + qc_cost
    
    # Return breakdown
    return {
        "total_cost": total_cost,
        "base_cost": base_cost,
        "sample_cost": sample_cost,
        "element_cost": element_cost,
        "hut_cost": hut_cost,
        "clt_cost": clt_cost,
        "print_cost": print_cost,
        "qc_cost": qc_cost
    }
```

### 4.1 Component Calculations

#### 4.1.1 Sample Costs

```python
def _calculate_sample_costs(self):
    """Calculate costs related to samples."""
    total_sample_cost = 0
    
    # For each province, audience, and sample type
    for province, audiences in self.samples.items():
        for audience, sample_types in audiences.items():
            for sample_type, data in sample_types.items():
                sample_size = data.get("sample_size", 0)
                price_growth = data.get("price_growth", 0.0)
                
                # Apply price growth to base rate
                base_rate = COST_CONSTANTS["per_respondent_fee"]
                adjusted_rate = base_rate * (1 + price_growth/100)
                
                # Calculate cost for this sample group
                group_cost = sample_size * adjusted_rate
                total_sample_cost += group_cost
    
    return total_sample_cost
```

#### 4.1.2 Element Costs

```python
def _calculate_element_costs(self, project_type, classification, interview_length):
    """Calculate costs based on element costs."""
    # Get the appropriate column based on classification and interview length
    if interview_length < 15:
        col_suffix = "(<15 min)"
    elif interview_length < 30:
        col_suffix = "(15-30 min)"
    elif interview_length < 45:
        col_suffix = "(30-45 min)"
    else:
        col_suffix = "(45-60 min)"
        
    column = f"{classification} {col_suffix}"
    
    # Sum costs from the appropriate column
    total_element_cost = 0
    if project_type in self.element_costs.costs:
        df = self.element_costs.costs[project_type]
        if column in df.columns:
            total_element_cost = df[column].sum()
    
    return total_element_cost
```

## 5. Project File Format

The project is saved in a JSON format with the following structure:

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
          "price_growth": 5.0
        },
        "...": {}
      },
      "...": {}
    },
    "...": {}
  },
  "qc_methods": [
    {
      "team": "...",
      "method": "...",
      "rate": 10.0
    },
    "..."
  ],
  "conditions": {
    "age_ranges": [[18, 35], [36, 50]],
    "sex": "male/female",
    "income_ranges": [[5000000, 10000000]]
  },
  "element_costs": {
    "project_type1": [
      {"Project Type": "...", "Subtitle 1": "...", "...": "..."},
      "..."
    ],
    "...": {}
  }
}
```