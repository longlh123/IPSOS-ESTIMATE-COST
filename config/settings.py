# config/settings.py
# -*- coding: utf-8 -*-
"""
Application settings for the Project Cost Calculator.
"""

# Application version
VERSION = "1.0.0"

# Default save directory
DEFAULT_SAVE_DIR = "projects"

# Currency symbol (for display only)
CURRENCY_SYMBOL = "VND"

# Default values for new projects
DEFAULT_VALUES = {
    "interview_length": 30,
    "questionnaire_length": 20,
    "open_ended_count": 5,
    "hut_usage_duration": 7,
    "clt_sample_size_per_day": 50
}

# Cost calculation constants
# These would be used in the cost calculation logic
COST_CONSTANTS = {
    "base_fee": 5000000,
    "per_respondent_fee": 200000,
    "open_ended_fee": 50000,
    "hut_day_fee": 100000,
    "clt_location_fee": 3000000,
    "print_page_fee": 5000,
    "color_print_fee": 10000,
    "laminated_fee": 15000,
    # New cost constants
    "bw_photo_fee": 250,           # Black and white photo fee
    "color_photo_fee": 5000,       # Color photo fee  
    "lamination_fee": 4000,        # Plastic lamination fee
    "dropcard_fee": 1000,          # Dropcard fee
    "parking_fee": 5000,           # Parking fee
    "distant_district_fee": 5000   # Distant district support fee
}