# models/project_model.py
# -*- coding: utf-8 -*-
"""
Central data model for the Project Cost Calculator application.
Handles all data storage, validation, and emits signals when data changes.
"""

import sys
import os
import logging
import math
import pandas as pd
from PySide6.QtCore import QObject, Signal
import json

from config.predefined_values import *
from config.settings import COST_CONSTANTS
from config.predefined_values import ASSIGNED_PEOPLE_LEVELS, DEFAULT_TRAVEL_COSTS, SAMPLE_TYPES
from models.element_costs_model import ElementCostsModel
from components.validation_field import FieldValidator
from formulars.pricing_formulas import (
    calculate_daily_sup_target
)
from models.cost_mappings import map_cost_for_element
from models.quanty_mappings import (
    map_quanty_for_element,
    map_quanty_for_price,
    get_chi_phi_phieu_pv_title,
    MAPPING_STATIONARY
)

class ProjectModel(QObject):
    """
    Central model class that stores all project data and emits signals when data changes.
    """
    dataChanged = Signal()  # Signal emitted whenever data changes
    
    def __init__(self):
        super().__init__()
        self.reset()
        
        # Initialize element costs model
        self.element_costs = ElementCostsModel()
    
    def resource_path(self, path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, path)
        return os.path.join(os.getcwd(), path)
    
    def reset(self):
        """Reset the model to its initial state."""
        # Tab 1: General data
        self.general = {
            # Region - General information
            "internal_job": "",
            "symphony": "",
            "project_name": "",
            "project_type": "",
            "clients": [],
            "project_objectives" : "",
            "platform": "iField",  # Default platform value
            "interview_methods": [],
            "recruit_methods": [],
            "type_of_quota_control": "",
            "quota_description": [],
            "service_line": "",
            "provinces": [],
            "industries": [],
            "target_audiences": [],
            "interview_length": 0,
            "questionnaire_length": 0,

            # Region - Device
            "device_type": "",
            "tablet_usage_duration": "",

            # Region 4 - Printer
            "bw_page_count": 0,
            "showphoto_page_count": 0,
            "showcard_page_count": 0,
            "dropcard_page_count": 0,
            "color_page_count": 0,
            "decal_page_count": 0,
            "laminated_page_count": 0,
            "interview_form_package_count" : 0,
            "stimulus_material_production_count" : 0,

            # Region - Data & Processing
            "scripting": False,
            "data_processing": False,
            "coding": False,
            "data_entry": False,
            "open_ended_main_count": 0,
            "open_ended_booster_count": 0,
            "data_processing_method": []
        }

        self.sampling_methods = []

        self.clt_settings = {
            # Region - CLT
            "clt_test_products": 0, #Tổng số lượng sản phẩm trên dự án
            "clt_respondent_visits": 0, #Tổng số lượng mẫu dùng trên một đáp viên
            "clt_sample_usage_details": "", #Chi tiết về cách sử dụng
            "clt_number_of_samples_to_label" : 0, #Số mẫu cần dán mẫu
            "clt_description_howtolabelthesample" : "", # Mô tả cách dán mẫu
            "clt_sample_split_method": "", # Yêu cầu về chiết mẫu
            "clt_preparation_steps": "", # Chi tiết về cách chuẩn bị mẫu
            "clt_supplies_required": "", # Yêu cầu mua vật dụng
            "clt_sample_delivery_method": "", # yêu cầu về chuyển mẫu
            "clt_other_requirements": "", # Các yêu cầu khác
            "clt_return_unused_samples": "Yes", #Có thu hồi mẫu nguyên vẹn còn dư không?
            "clt_return_used_samples": "Yes", #Có thu hồi sản phẩm đã dùng không?

            "clt_total_concepts": 0,
            "clt_concepts_per_respondent": 0,

            "clt_dan_mau_days": 0,
            "clt_sample_size_per_day": 0,
            "clt_desk_interviewers_count": 0,
            "clt_provincial_desk_interviewers_count": 0,

            "clt_assistant_setup_days": 0,
            "clt_failure_rate": 0,
            "clt_sample_recruit_idi" : 0,
        } 

        self.hut_settings = {
            "hut_test_products": 0,
            "hut_usage_duration": 0,
        }

        self.cost_toggles = {
            "device_rental_costs" : {
                "Chi phí thuê tablet < 9 inch" : False,
                "Chi phí thuê tablet >= 9 inch" : False,
                "Chi phí thuê laptop" : False
            },
            "idi_costs" : {
                "Chi phí Tuyển đáp viên IDI" : False,
                "Chi phí Quản lý IDI" : False,
                "Chi phí QC - IDI" : False,
                "Quà Phiếu PV - IDI" : False
            },
            "failure_rate_costs" : {
                "Chi phí Phiếu PV - Bài rớt giữa chừng" : False
            },
            "qc_method_costs" : {
                "Chi phí QC - In home" : False,
                "Chi phí QC - In Location" : False,
                "Chi phí QC - DP" : False,
                "Chi phí thuê laptop" : False,
                "Chi phí Quản lý - On-field" : False
            },
            "qc_communication_costs" : {
                "Chi phí Card điện thoại": False
            },
            "dp_costs" : {
                "Chi phí Coding" : False,
                "Chi phí Input" : False,
                "Chi phí Quản lý - On-field" : False
            },
            "incentive_costs": {
                "Quà Phiếu PV - Pilot": False,
                "Quà Phiếu PV - Main": False,
                "Quà Phiếu PV - Booster": False,
                "Quà Phiếu PV - Non": False
            },
            "stationary_costs" : {
                "Photo trắng đen" : False,
                "Showphoto" : False,
                "Showcard" : False,
                "Dropcard" : False,
                "In màu \ In concept" : False,
                "Decal" : False,
                "Ép Plastic" : False,
                "Hồ sơ biểu mẫu" : False,
                "Chi phí đóng cuốn" : False
            }
        }

        self.subcontracts = []

        # Application settings
        self.settings = {
            "interviewers_per_supervisor": 10,   # Default value
            
            # Other settings
            "parking_fee": 5000,                # Parking fee
            "distant_district_fee": 5000,       # Distant district support fee

            # Stationary settings by province
            "stationary": {
                "Hồ Chí Minh": {
                    "bw_page_fee": 350,
                    "showphoto_page_fee": 2500,
                    "showcard_page_fee": 4000,
                    "dropcard_page_fee": 9000,
                    "color_page_fee": 2500,
                    "decal_page_fee": 3500,
                    "laminated_page_fee": 6000,
                    "interview_form_package_fee" : 350,
                    "stimulus_material_production_fee" : 4000
                },
                "Hà Nội": {
                    "bw_page_fee": 400,
                    "showphoto_page_fee": 3000,
                    "showcard_page_fee": 6000,
                    "dropcard_page_fee": 9000,
                    "color_page_fee": 3000,
                    "decal_page_fee": 2500,
                    "laminated_page_fee": 5000,
                    "interview_form_package_fee" : 400,
                    "stimulus_material_production_fee" : 4000
                },
                "Đà Nẵng": {
                    "bw_page_fee": 450,
                    "showphoto_page_fee": 2500,
                    "showcard_page_fee": 4000,
                    "dropcard_page_fee": 9000,
                    "color_page_fee": 3500,
                    "decal_page_fee": 3500,
                    "laminated_page_fee": 7000,
                    "interview_form_package_fee" : 450,
                    "stimulus_material_production_fee" : 4000
                },
                "Cần Thơ": {
                    "bw_page_fee": 400,
                    "showphoto_page_fee": 2500,
                    "showcard_page_fee": 3500,
                    "dropcard_page_fee": 9000,
                    "color_page_fee": 2500,
                    "decal_page_fee": 3500,
                    "laminated_page_fee": 6000,
                    "interview_form_package_fee" : 400,
                    "stimulus_material_production_fee" : 4000
                },
                "Others": {
                    "bw_page_fee": 350,
                    "showphoto_page_fee": 2500,
                    "showcard_page_fee": 4000,
                    "dropcard_page_fee": 9000,
                    "color_page_fee": 2500,
                    "decal_page_fee": 3500,
                    "laminated_page_fee": 6000,
                    "interview_form_package_fee" : 400,
                    "stimulus_material_production_fee" : 4000
                }
            },
            # Transportation settings by province
            "transportation": {
                "Others": {
                    "flight": 1000000,
                    "train": 400000
                }
            }
        }

        # Initialize travel cost settings
        # for level in ASSIGNED_PEOPLE_LEVELS:
        #     for cost_type in ["hotel", "food"]:
        #         setting_key = f"travel_{level.lower()}_{cost_type}"
        #         if setting_key not in self.settings:
        #             self.settings[setting_key] = DEFAULT_TRAVEL_COSTS[level][cost_type]

        # Tab 2: Samples data
        # Structure: {province: {target_audience: {sample_type: {"sample_size": int, "price_growth": float}}}}
        self.samples = {}
        
        # Tab 3: QC Method data
        # List of dictionaries with team, method, and rate
        self.qc_methods = []
        
        # Tab 5: Assignments data
        self.assignments = []
        
        # Tab 6: Travel data
        # Structure: {province: {
            # "travel_days": int,
            # "travel_nights": 0,
            # "assigned_people": []  # List of emails
        #     "parttime": {
        #         "supervisor": {"distant": int, "nearby": int},
        #         "interviewer": {"distant": int, "nearby": int},
        #         "qc": {"distant": int, "nearby": int}
        #     }
        # }}
        self.travel = {}
        
        # Tab 7: Additional Costs data
        self.additional_costs = []  # List of dictionaries with category, name, unit_price, quantity, description, is_dp_coding

        json_path = self.resource_path(r'config/industries.json')

        with open(json_path, mode = 'r', encoding="utf-8") as f:
            self.industries_data = json.load(f)

        self.rate_card_settings = {}

        json_path = self.resource_path(r'config/rate_card_settings.json')

        with open(json_path, mode='r', encoding="utf-8") as f:
            self.rate_card_settings = json.load(f)

        self.dataChanged.emit()

    ### Validate
    def validate(self) -> bool:
        validator = FieldValidator()
        is_valid, error_message = True, ""

        for field_name, value in self.general.items():
            if field_name == "quota_description":
                is_valid, error_message = validator.validate(field_name, value, condition=self.general["type_of_quota_control"])
            elif field_name == "open_ended_main_count":
                is_valid, error_message = validator.validate(field_name, value, condition=self.general["coding"] and "Main" in self.general["sample_types"])
            elif field_name == "open_ended_booster_count":
                is_valid, error_message = validator.validate(field_name, value, condition=self.general["coding"] and "Booster" in self.general["sample_types"])
            else:
                is_valid, error_message = validator.validate(field_name, value)

            if not is_valid:
                return field_name, is_valid, error_message
        
        for field_name, value in self.clt_settings.items():
            if field_name == "clt_concepts_per_respondent":
                is_valid, error_message = validator.validate(field_name, value, condition=self.clt_settings["clt_total_concepts"] > 0)
            else:
                is_valid, error_message = validator.validate(field_name, value)

            if not is_valid:
                return field_name, is_valid, error_message
        
        for field_name, value in self.hut_settings.items():
            is_valid, error_message = validator.validate(field_name, value)

            if not is_valid:
                return field_name, is_valid, error_message
        
        return "", True, ""

    def set_tablet_usage_duration(self, value):
        if self.general["device_type"] != "Tablet < 9 inch":
            self.general["tablet_usage_duration"] = ""

    def set_selected_device_cost(self, selected_name: str):
        for name in self.cost_toggles.get('device_rental_costs', {}).keys():
            self.cost_toggles['device_rental_costs'][name] = selected_name.lower() in name.lower()

    def set_selected_idi_costs(self, selected):
        for name in self.cost_toggles.get('idi_costs', {}).keys():
            self.cost_toggles['idi_costs'][name] = selected
    
    def set_selected_failure_rate_costs(self, selected):
        for name in self.cost_toggles.get('failure_rate_costs', {}).keys():
            self.cost_toggles['failure_rate_costs'][name] = selected

    def set_selected_stationary_costs(self):
        
        for cost_name, field_name in MAPPING_STATIONARY.items():
            self.cost_toggles['stationary_costs'][cost_name] = self.general.get(field_name, 0) != 0

    def set_selected_incentive_costs(self):
        for sample_type in SAMPLE_TYPES:
            cost_name = f"Quà Phiếu PV - {sample_type}"

            self.cost_toggles['incentive_costs'][cost_name] = sample_type in self.general.get('sample_types', [])

    def set_selected_qc_method_costs(self):
        qc_methods = [item.get('qc_method') for item in self.qc_methods if item.get('team') == 'QC']

        self.cost_toggles['qc_method_costs']["Chi phí thuê laptop"] = len(qc_methods) > 0
        self.cost_toggles['qc_method_costs']["Chi phí Quản lý - On-field"] = len(qc_methods) > 0

        MAPPING_QC_METHODS = {
            "Chi phí QC - In home" : "QC - In home",
            "Chi phí QC - In Location" : "QC - In Location",
            "Chi phí QC - DP" : "QC - DP"
        }

        for qc_cost, qc_method in MAPPING_QC_METHODS.items():
            self.cost_toggles['qc_method_costs'][qc_cost] = qc_method in qc_methods

    def qc_communication_costs(self, selected):
        for name in self.cost_toggles.get('qc_communication_costs', {}).keys():
            self.cost_toggles['qc_communication_costs'][name] = selected

    def set_selected_dp_costs(self):
        self.cost_toggles['dp_costs']["Chi phí Coding"] = self.general.get('coding', False)
        self.cost_toggles['dp_costs']["Chi phí Input"] = self.general.get('data_entry', False)

        self.cost_toggles['dp_costs']["Chi phí Quản lý - On-field"] = any([self.general.get('coding', False), self.general.get('data_entry', False)])

    def is_enabled(self, cost_name: str, cost_group=''):
        if cost_group:
            selected_costs = self.cost_toggles.get(cost_group, {})

            for name, enabled in selected_costs.items():
                if name.lower() == cost_name.lower():
                    return enabled
        else:
            for group, costs in self.cost_toggles.items():
                for name, enabled in costs.items():
                    if name.lower() == cost_name.lower():
                        return enabled
            return True

    def generate_settings_table(self) -> str:
        rows = ""

        objectives = self.general.get("project_objectives", "").strip()
        rows += f"<tr><td style='border: 1px solid black;'><b>Project Objectives</b></td><td style='border: 1px solid black;'>{objectives}</td></tr>"

        if self.general['project_type'] == 'CLT':
            clt_mappings = {
                "clt_test_products": "Tổng số lượng sản phẩm trên dự án",
                "clt_respondent_visits": "Tổng số lượng mẫu dùng trên một đáp viên",
                "clt_sample_usage_details": "Chi tiết về cách sử dụng",
                "clt_number_of_samples_to_label" : "Số mẫu cần dán mẫu",
                "clt_description_howtolabelthesample" : "Mô tả cách dán mẫu",
                "clt_sample_split_method": "Yêu cầu về chiết mẫu",
                "clt_preparation_steps": "Chi tiết về cách chuẩn bị mẫu",
                "clt_supplies_required": "Yêu cầu mua vật dụng",
                "clt_sample_delivery_method": "yêu cầu về chuyển mẫu",
                "clt_other_requirements": "Các yêu cầu khác",
                "clt_return_unused_samples": "Có thu hồi mẫu nguyên vẹn còn dư không?",
                "clt_return_used_samples": "Có thu hồi sản phẩm đã dùng không?",
            }
            
            for key, label in clt_mappings.items():
                if key in ["clt_test_products", "clt_respondent_visits", "clt_number_of_samples_to_label"]:
                    if self.clt_settings[key] > 0: 
                        rows += f"<tr><td style='border: 1px solid black;'><b>{clt_mappings[key]}</b></td><td style='border: 1px solid black;'>{self.clt_settings[key]}</td></tr>"
                else:
                    if len(self.clt_settings[key]) > 0: 
                        rows += f"<tr><td style='border: 1px solid black;'><b>{clt_mappings[key]}</b></td><td style='border: 1px solid black;'>{self.clt_settings[key]}</td></tr>"

        html_table = f"""
            <table border="1" cellspacing="0" cellpadding="4" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th style='border: 1px solid black;'>Setting</th>
                        <th style='border: 1px solid black;'>Value</th>
                    </tr>
                </thead>
                <tbody style='border: 1px solid black;'>{rows}</tbody>
            </table>
        """
        return html_table
    
    def update_qc_methods(self, items):
        self.qc_methods = items.copy()
        self.dataChanged.emit()

    def update_subcontracts(self, items):
        self.subcontracts = items.copy()
        self.dataChanged.emit()

    def update_sampling_methods(self, items):
        self.sampling_methods = items.copy()
        
        sample_types = self.get_sample_types()

        for s in self.sampling_methods:
            if "Main" not in sample_types:
                self.general["open_ended_main_count"] = 0
            if "Booster" not in sample_types:
                self.general["open_ended_booster_count"] = 0

        self.update_samples_structure()

        self.dataChanged.emit()

    def update_settings(self, field, value):
        """
        Update a field in the settings.
        
        Args:
            field (str): Field name to update
            value: New value for the field
        """
        self.settings[field] = value
        self.dataChanged.emit()
        
        # If interviewers_per_supervisor is updated, recalculate daily_sup_target for all samples
        if field == "interviewers_per_supervisor":
            self._recalculate_daily_sup_targets()
    
    def get_sample_types(self):
        return [s['sample_type'] for s in self.sampling_methods]

    def get_industries(self):
        return [name for name in self.industries_data.keys() if name != 'default']

    def get_audiences(self, industry_name):
        target_audience_names = list()

        for industry_data in self.industries_data.get(industry_name, {}).values():
            target_audience_names.append(industry_data.get('target_audience'))

        return target_audience_names

    def make_pricing_entry(self, price, price_growth, type):
        return {
            "price": price,
            "price_growth": price_growth,
            "type": type,
            "comment": {}
        }

    def make_audience_entry(self, new_audience_data, audience_id, pricing, target):
        audience_entry = {
            "audience_id": audience_id,
            "sample_type": new_audience_data.get('sample_type'),
            "industry_name": new_audience_data.get('industry_name'),
            "target_audience_name": new_audience_data.get('target_audience_name'),
            "gender": new_audience_data.get("gender"),
            "age_group": new_audience_data.get("age_group"),
            "household_income": new_audience_data.get("household_income"),
            "incident_rate": new_audience_data.get("incident_rate", 100),
            "complexity": new_audience_data.get("complexity", "Standard"),
            "description": new_audience_data.get("description", ""),
            "sample_size": new_audience_data.get("sample_size", 0),
            "extra_rate": new_audience_data.get("extra_rate", 0),
            "pricing": pricing,
            "target" : target,
            "comment": {},
        }
        return audience_entry

    def _make_price_entry(self, price, price_growth, type):
        return {
            "price": price,
            "price_growth": price_growth,
            "type": type,
            "comment": {}
        }

    def _make_pricing_entry(self, sample_type, pricing):

        if sample_type == 'Pilot':
            return [self._make_price_entry(pricing.get('pilot'), 0, 'pilot')]
        elif sample_type == 'None':
            return [self._make_price_entry(pricing.get('non'), 0, 'non')]
        elif sample_type == 'Main':
            return [
                self._make_price_entry(pricing.get('main', {}).get('recruit'), 0, 'recruit'),
                self._make_price_entry(pricing.get('main', {}).get('location'), 0, 'location')
            ]
        elif sample_type == 'Booster':
            return [
                self._make_price_entry(pricing.get('main', {}).get('booster'), 0, 'recruit'),
                self._make_price_entry(pricing.get('main', {}).get('booster'), 0, 'location')
            ]
        else:
            raise ValueError(f"[RateCard Error] Sample type {sample_type} isn't defined in rate card settings.")

    def _make_target_rate_card(self, rate_card):
        return {
            "daily_interview_target" : rate_card.get('daily_interview_target'),
            "target_for_interviewer" : rate_card.get('target_for_interviewer'),
            "interviewers_per_supervisor" : rate_card.get('interviewers_per_supervisor'),
        }

    def _get_rate_card(self, sample_type, interview_length):
        project_type = self.general['project_type']

        if project_type not in self.rate_card_settings.keys():
            raise ValueError(f"[RateCard Error] Project type {project_type} isn't defined in rate card settings.")
        
        levels = list([level for level in self.rate_card_settings[project_type].keys()])

        #Determine the level based on total number of levels
        interval = 100 / len(levels)
        level = int(100 // interval) + 1

        rate_cards = self.rate_card_settings[project_type].get(f"L{level}")

        if not rate_cards:
            raise ValueError(f"[RateCard Error] No rate cards found for level {level} in project type {project_type}.")

        for rate_card in rate_cards:
            min_len, max_len = rate_card['interview_length_range']

            if min_len <= interview_length <= max_len:
                try:
                    rate_card_pricing = self._make_pricing_entry(sample_type, rate_card.get('pricing', {}))
                    rate_card_target = self._make_target_rate_card(rate_card)

                    return rate_card_pricing, rate_card_target
                except ValueError as e:
                    raise str(e)
            
        raise ValueError(
            f"[RateCard Error] No rate card found for interview_length = {interview_length} "
            f"in project_type '{project_type}', level {level}."
        )
    
    def get_audience(self, new_audience_data):
        try:
            rate_card_pricing, rate_card_target  = self._get_rate_card(new_audience_data.get('sample_type'), self.general.get('interview_length', 0))
            
            rate_card_audience_data = self.make_audience_entry(new_audience_data, "default", rate_card_pricing, rate_card_target)

            industry_data = self.industries_data.get(new_audience_data.get('industry_name'), {})

            for ta_id, ta_data in industry_data.items():
                if ta_data["target_audience"] == new_audience_data.get('target_audience_name'):
                    pricing = self._make_pricing_entry(new_audience_data.get('sample_type'), ta_data.get('pricing', {}))
                    audience_data = self.make_audience_entry(new_audience_data, ta_id, pricing, rate_card_target)
                    return audience_data
            
            return rate_card_audience_data
        
        except ValueError as e:
            raise str(e)
                    
    def to_dict(self):
        """Convert model to dictionary for saving."""
        data = {
            "general": self.general,
            "sampling_methods" : self.sampling_methods,
            "clt_settings" : self.clt_settings,
            "hut_settings" : self.hut_settings,
            "cost_toggles" : self.cost_toggles,
            "settings": self.settings,
            "samples": self.samples,
            "qc_methods": self.qc_methods,
            "travel": self.travel,
            "assignments": self.assignments,  # Add assignments to saved data
            "additional_costs": self.additional_costs,
            "subcontracts": self.subcontracts
        }
        
        return data
        
    def from_dict(self, data):
        """Load model from dictionary."""
        # Reset the model first
        self.reset()
        
        # Load basic data
        self.general.update(data.get("general", {}))
        self.sampling_methods = data.get("sampling_methods", [])
        self.clt_settings.update(data.get("clt_settings", {}))
        self.hut_settings.update(data.get('hut_settings', {}))
        self.cost_toggles.update(data.get("cost_toggles", {}))
        self.settings.update(data.get("settings", {}))
        self.samples = data.get("samples", {})
        self.qc_methods = data.get("qc_methods", [])
        self.travel = data.get("travel", {})
        self.assignments = data.get("assignments", [])  # Load assignments data
        self.additional_costs = data.get("additional_costs", [])
        self.subcontracts = data.get("subcontracts", [])

        # Emit signal for UI update
        self.dataChanged.emit()

    def update_general(self, field, value):
        """
        Update a field in the general data.
        
        Args:
            field (str): Field name to update
            value: New value for the field
        """
        self.general[field] = value
        
        if field == "device_type":
            self.set_tablet_usage_duration(value)
            self.set_selected_device_cost(value)

        if field == "type_of_quota_control":
            if self.general[field] != "Interlocked Quota":
                self.general["quota_description"] = []

        if field in ["provinces", "target_audiences"]:
            # Update samples structure when any of these fields change
            self.update_samples_structure()
            # Update travel structure when provinces change
            if field == "provinces":
                self.update_travel_structure()
            
        self.dataChanged.emit()
        
    def update_samples_structure(self):
        """
        Update the structure of the samples dictionary based on chosen provinces,
        target audiences, and sample types.
        """
        provinces = self.general.get("provinces", [])
        target_audiences = self.general.get("target_audiences", [])
        sample_types = self.get_sample_types()
        interviewers_per_supervisor = self.settings.get("interviewers_per_supervisor", 8)
        
        new_target_audiences = []

        for audience in target_audiences:
            if audience.get('sample_type') in sample_types:
                new_target_audiences.append(audience)

        self.general["target_audiences"] = new_target_audiences

        # Initialize new samples structure
        new_samples = {}
        
        for province in provinces:
            new_samples[province] = {}

            for audience in new_target_audiences:
                audience_name = audience.get("target_audience_name")
                sample_type = audience.get("sample_type")
                sample_size = audience.get("sample_size", audience.get("sample_size", 0))
                target_for_interviewer = audience.get('target', {}).get('target_for_interviewer', 0)
                interviewers_per_supervisor = audience.get('target', {}).get('interviewers_per_supervisor', 0)

                if sample_type in sample_types:
                    
                    daily_sup_target = calculate_daily_sup_target(sample_size, 
                                                                 target_for_interviewer, 
                        
                    
                                                             interviewers_per_supervisor)
                    
                    # Construct audience entry
                    audience_entry = {
                        **audience
                    }

                    audience_entry["target"]["daily_sup_target"] = daily_sup_target
                    
                    new_samples[province][f"{sample_type} - {audience_name}"] = audience_entry

        self.samples = new_samples
        self.dataChanged.emit()
    
    def update_sample(self, province, audience_data):
        """
        Update the sample data for a specific audience in a given province.

        Args:
            province (str): Province name
            audience_data (dict): A complete audience data dictionary
        """
        audience_name = audience_data.get("target_audience_name")
        sample_type = audience_data.get("sample_type")
        audience_key = f"{sample_type} - {audience_name}"

        if not province or not audience_name:
            return

        # Ensure province exists
        if province not in self.samples:
            self.samples[province] = {}

        # Update the audience in the model
        self.samples[province][audience_key] = audience_data

        # Emit signal to notify change
        self.dataChanged.emit()

    def update_clt_settings(self, field, value):
        if field == "clt_number_of_samples_to_label":
            if value == 0:
                self.clt_settings["clt_description_howtolabelthesample"] = ""
                self.clt_settings["clt_sample_split_method"] = ""
        if field == "clt_test_products":
            if value == 0:
                self.clt_settings["clt_respondent_visits"] = 0
        if field == "clt_total_concepts":
            if value == 0:
                self.clt_settings["clt_concepts_per_respondent"] = 0

        self.clt_settings[field] = value

        self.dataChanged.emit()

    def clt_settings_clear(self):
        for key, value in self.clt_settings.items():
            if key == "clt_assistant_setup_days":
                self.clt_settings[key] = 1
            elif key in ["clt_description_howtolabelthesample", "clt_sample_usage_details", "clt_sample_split_method", "clt_preparation_steps", "clt_supplies_required", "clt_sample_delivery_method", "clt_other_requirements"]:
                self.clt_settings[key] = ""
            elif key in ["clt_return_unused_samples", "clt_return_used_samples"]:
                self.clt_settings[key] = "Yes"
            else:
                self.clt_settings[key] = 0

    def update_hut_settings(self, field, value):
        self.hut_settings[field] = value
        self.dataChanged.emit()

    def hut_settings_clear(self):
        for key, value in self.hut_settings.items():
            self.hut_settings[key] = 0

    def update_travel_structure(self):
        """
        Update the structure of the travel dictionary based on chosen provinces.
        """
        provinces = self.general["provinces"]
        
        # Initialize new travel structure
        new_travel = {}
        
        for province in provinces:
            if province not in new_travel:
                # Copy existing data or initialize new data
                if province in self.travel:
                    new_travel[province] = self.travel[province]
                else:
                    new_travel[province] = {
                        "fulltime": {
                            "travel_days": 0,
                            "travel_nights": 0,
                            "assigned_people": []
                        },
                        "parttime": {
                            "supervisor": {
                                "distant": 0, 
                                "nearby": 0,
                                "recruit_distant": 0, 
                                "recruit_nearby": 0,
                                "ngoi_ban_distant": 0, 
                                "ngoi_ban_nearby": 0
                            },
                            "interviewer": {
                                "distant": 0, 
                                "nearby": 0,
                                "recruit_distant": 0, 
                                "recruit_nearby": 0,
                                "ngoi_ban_distant": 0, 
                                "ngoi_ban_nearby": 0
                            },
                            "qc": {"distant": 0, "nearby": 0}
                        }
                    }
        
        self.travel = new_travel
        self.dataChanged.emit()

    def flatten_cost_hierarchy(self, hierarchy):
        flat_rows = []

        def get_comment(comment_item):
            comment_titles = {
                "price_growth": "Price Growth",
                "target_for_interviewer": "Target for Interviewer",
                "daily_sup_target": "Daily SUP Target" 
            }

            comment = ""

            if comment_item:
                for key, value in comment_item.items():
                    comment += ('' if len(comment) == 0 else '\n') + f'{comment_titles[key]}: {value}'

            return comment
    
        def create_element_from_pricing(current_title, province, target_audience):
            
            for price in target_audience.get('pricing', {}):
                cost = price.get('price', 0) * abs(1 + price.get('price_growth', 0) / 100) 
                quanty = map_quanty_for_price(self, price, province, target_audience)
                total_cost = quanty * cost
                comment = get_comment(price.get('comment', {}))

                row = [
                    current_title,
                    province,
                    get_chi_phi_phieu_pv_title(price.get('type', '').lower()),
                    target_audience.get('name', ''),
                    0,
                    "Phiếu",
                    0 if not cost or cost == 0 else cost,
                    0 if not quanty or quanty == 0 else quanty,
                    0 if not total_cost or total_cost == 0 else total_cost,
                    comment
                ]

                flat_rows.append(row)

        def create_element(current_title, elements):
            for province in self.samples.keys():
                if current_title == "INTERVIEWER":
                    sample_type_order = {
                        "Pilot" : 0,
                        "Main" : 1,
                        "Booster" : 2,
                        "Non" : 3
                    }

                    sorted_target_audiences = sorted(
                        self.samples.get(province, {}).items(),
                        key = lambda item: sample_type_order.get(item[1].get("sample_type", ""), 99)
                    )

                    for key, target_audience in sorted_target_audiences:
                        create_element_from_pricing(current_title, province, target_audience)

                if current_title == "SUPERVISOR/ ASSISTANT":
                    sup_comment = ""
                    
                    for key, target_audience in self.samples.get(province, {}).items():
                        comment = get_comment(target_audience.get('comment', {}))

                        if comment:
                            sup_comment += ("\n" if len(sup_comment) > 0 else "") + comment

                for element in elements:
                    cost_description = element.get("description", "")

                    if "Chi phí Card điện thoại" in cost_description:
                        a = ""

                    titles = current_title.split(" / ")

                    if titles[0] == "QC" and "IDI" not in cost_description:
                        cost_group = "qc_method_costs"
                    elif titles[0] == "COMMUNICATION" and titles[1] == "QC":
                        cost_group = "qc_communication_cost"
                    else:
                        cost_group = ""

                    if self.is_enabled(cost_description, cost_group=cost_group):
                        cost = map_cost_for_element(self, element)
                        quanty = map_quanty_for_element(self, element, province, title=current_title)
                        total_cost = cost * quanty
                        
                        row = [
                            element.get("name", current_title),
                            province,
                            cost_description,
                            element.get("target_audience", ""),
                            element.get("code", ""),
                            element.get("unit", ""),
                            0 if not cost or cost == 0 else cost,
                            0 if not quanty or quanty == 0 else quanty,
                            0 if not total_cost or total_cost == 0 else total_cost,
                            sup_comment if cost_description == "Chi phí Quản lý recruit - On-field" else ""
                        ]

                        flat_rows.append(row)

        def traverse(subtree, parent_title=""):
            for title, node in subtree.items():
                if title == "TRAVEL" and len(self.travel.keys()) == 0:
                    continue

                current_title = f"{parent_title} / {title}" if parent_title else title

                if len(node['children']) == 0 and len(node['elements']):
                    create_element(current_title, node['elements'])
                else:
                    traverse(node.get("children", {}), current_title)

        traverse(hierarchy[self.general.get('project_type', "")].get("children", {}))

        return flat_rows
    

    # def _recalculate_daily_sup_targets(self):
    #     """Recalculate all daily supervisor targets based on the new interviewers_per_supervisor value."""
    #     for province, audiences in self.samples.items():
    #         for audience, sample_types in audiences.items():
    #             for sample_type, data in sample_types.items():
    #                 sample_size = data.get("sample_size", 0)
    #                 interviewer_target = data.get("interviewer_target", TARGET_AUDIENCE_INTERVIEWER_TARGETS.get(audience, 2))
    #                 interviewers_per_supervisor = self.settings.get("interviewers_per_supervisor", 8)
                    
    #                 if interviewer_target > 0 and interviewers_per_supervisor > 0:
    #                     daily_sup_target = round(sample_size / interviewer_target / interviewers_per_supervisor, 2)
    #                 else:
    #                     daily_sup_target = 0
                    
    #                 self.samples[province][audience][sample_type]["daily_sup_target"] = daily_sup_target

    # def _update_all_audience_price_growth(self, audience, sample_type, value, comment=None):
    #     """
    #     Update price growth for a target audience across all provinces and sample types.
        
    #     Args:
    #         audience (str): Target audience name
    #         sample_type (str): Sample type to update
    #         value (float): New price growth value
    #         comment (str, optional): Comment for the change
    #     """
    #     # Keep track of changes for logging
    #     changes_count = 0
        
    #     # Update each province
    #     for province in self.samples:
    #         if audience in self.samples[province]:
    #             # Update all sample types for this audience in this province
    #             for sample_type_key in self.samples[province][audience]:
    #                 # Update price growth
    #                 self.samples[province][audience][sample_type_key]["price_growth"] = value
                    
    #                 # Update comment if provided
    #                 if comment is not None:
    #                     if "comment" not in self.samples[province][audience][sample_type_key]:
    #                         self.samples[province][audience][sample_type_key]["comment"] = {}
                        
    #                     self.samples[province][audience][sample_type_key]["comment"]["price_growth"] = comment
                    
    #                 changes_count += 1
        
    #     logging.info(f"Updated price growth for target audience '{audience}' in {changes_count} entries")
        
    #     # Emit signal that data has changed
    #     self.dataChanged.emit()
            
    # def add_qc_method(self, team, method, rate):
    #     """
    #     Add a QC method.
        
    #     Args:
    #         team (str): Team name
    #         method (str): QC method name
    #         rate (float): QC rate percentage
            
    #     Returns:
    #         bool: True if added successfully, False if this combination already exists
    #     """
    #     # Check if this combination already exists
    #     for qc in self.qc_methods:
    #         if qc["team"] == team and qc["method"] == method:
    #             return False
                
    #     self.qc_methods.append({
    #         "team": team,
    #         "method": method,
    #         "rate": rate
    #     })
    #     self.dataChanged.emit()
    #     return True
        
    # def remove_qc_method(self, index):
    #     """
    #     Remove a QC method by index.
        
    #     Args:
    #         index (int): Index of the QC method to remove
            
    #     Returns:
    #         bool: True if removed successfully, False if index is out of range
    #     """
    #     if 0 <= index < len(self.qc_methods):
    #         self.qc_methods.pop(index)
    #         self.dataChanged.emit()
    #         return True
    #     return False

    # def _should_separate_by_target_audience(self, first_subtitle, element_cost_name):
    #     """
    #     Determine if an element should be separated by target audience based on the requirement.
        
    #     Args:
    #         first_subtitle (str): First subtitle (category) of the element
    #         element_cost_name (str): Element cost name (subtitle 5)
            
    #     Returns:
    #         bool: True if element should be separated by target audience
    #     """
    #     # INTERVIEWER: Chi phí thuê tablet, Chi phí thuê laptop, Chi phí gửi xe, Chi phí IDI
    #     if self._contains_term(first_subtitle, ["INTERVIEWER"]):
    #         return not (self._contains_term(element_cost_name, ["thuê tablet"]) or
    #                 self._contains_term(element_cost_name, ["thuê laptop"]) or
    #                 self._contains_term(element_cost_name, ["gửi xe"]) or
    #                 self._contains_term(element_cost_name, ["IDI"]))
        
    #     # SUP/SUPERVISOR/ASSISTANT: Chi phí set up - Pre-field, Chi phí quản lý recruit - On-field, 
    #     # Chi phí quản lý ngồi bàn - On-field, Chi phí IDI
    #     elif self._contains_term(first_subtitle, ["SUPERVISOR", "ASSISTANT", "SUP"]):
    #         return not (self._contains_term(element_cost_name, ["set up - Pre-field"]) or
    #                 self._contains_term(element_cost_name, ["quản lý recruit - On-field"]) or
    #                 self._contains_term(element_cost_name, ["quản lý ngồi bàn - On-field"]) or
    #                 self._contains_term(element_cost_name, ["IDI"]))
        
    #     # QC, DP, COMMUNICATION, STATIONARY: all elements
    #     elif self._contains_term(first_subtitle, ["QC", "DP", "COMMUNICATION", "STATIONARY"]):
    #         return False
        
    #     # INCENTIVE: Chi phí IDI
    #     elif self._contains_term(first_subtitle, ["INCENTIVE"]):
    #         return not self._contains_term(element_cost_name, ["IDI"])
        
    #     # All other elements should NOT be separated by target audience
    #     return True

    # # Update to_dict and from_dict methods
    

    # # New methods for assignments
    # def add_assignment(self, level, email):
    #     """
    #     Add a person assignment.
        
    #     Args:
    #         level (str): Person's level
    #         email (str): Person's email
        
    #     Returns:
    #         bool: True if added successfully, False if already exists
    #     """
    #     # Check if person already exists
    #     for assignment in self.assignments:
    #         if assignment["email"] == email:
    #             return False
                
    #     # Add new assignment
    #     self.assignments.append({
    #         "level": level,
    #         "email": email
    #     })
        
    #     self.dataChanged.emit()
    #     return True

    # def remove_assignment(self, index):
    #     """
    #     Remove a person assignment by index.
        
    #     Args:
    #         index (int): Index of the assignment to remove
            
    #     Returns:
    #         bool: True if removed successfully, False if index out of range
    #     """
    #     if 0 <= index < len(self.assignments):
    #         # Get the email being removed
    #         removed_email = self.assignments[index]["email"]
            
    #         # Remove the assignment
    #         self.assignments.pop(index)
            
    #         # Remove this person from any province's travel assignments
    #         for province in self.travel:
    #             if "fulltime" in self.travel[province]:
    #                 assigned_people = self.travel[province]["fulltime"].get("assigned_people", [])
    #                 if removed_email in assigned_people:
    #                     assigned_people.remove(removed_email)
    #                     self.travel[province]["fulltime"]["assigned_people"] = assigned_people
            
    #         self.dataChanged.emit()
    #         return True
    #     return False

    # def update_travel(self, province, category, role=None, field=None, value=0):
    #     """
    #     Update travel data for a province.
        
    #     Args:
    #         province (str): Province name
    #         category (str): Category (fulltime, parttime)
    #         role (str, optional): Role (supervisor, interviewer, qc)
    #         field (str, optional): Field name (distant, nearby, recruit_distant, etc.)
    #         value: Value to set
    #     """
    #     if province not in self.travel:
    #         # Initialize with all possible fields including transportation_type
    #         self.travel[province] = {
    #             "fulltime": {
    #                 "travel_days": 0,
    #                 "travel_nights": 0,
    #                 "assigned_people": [],
    #                 "transportation_type": "tàu/xe"  # Add default transportation type
    #             },
    #             "parttime": {
    #                 "supervisor": {
    #                     "distant": 0, 
    #                     "nearby": 0,
    #                     "recruit_distant": 0, 
    #                     "recruit_nearby": 0,
    #                     "ngoi_ban_distant": 0, 
    #                     "ngoi_ban_nearby": 0
    #                 },
    #                 "interviewer": {
    #                     "distant": 0, 
    #                     "nearby": 0,
    #                     "recruit_distant": 0, 
    #                     "recruit_nearby": 0,
    #                     "ngoi_ban_distant": 0, 
    #                     "ngoi_ban_nearby": 0
    #                 },
    #                 "qc": {"distant": 0, "nearby": 0}
    #             }
    #         }
        
    #     if category == "fulltime":
    #         if field and field in ["travel_days", "travel_nights", "assigned_people", "transportation_type"]:
    #             self.travel[province]["fulltime"][field] = value
    #     elif category == "parttime" and role and field:
    #         # Ensure parttime structure exists
    #         if "parttime" not in self.travel[province]:
    #             self.travel[province]["parttime"] = {
    #                 "supervisor": {
    #                     "distant": 0, "nearby": 0,
    #                     "recruit_distant": 0, "recruit_nearby": 0,
    #                     "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
    #                 },
    #                 "interviewer": {
    #                     "distant": 0, "nearby": 0,
    #                     "recruit_distant": 0, "recruit_nearby": 0,
    #                     "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
    #                 },
    #                 "qc": {"distant": 0, "nearby": 0}
    #             }
            
    #         # Ensure role exists
    #         if role not in self.travel[province]["parttime"]:
    #             if role in ["supervisor", "interviewer"]:
    #                 self.travel[province]["parttime"][role] = {
    #                     "distant": 0, "nearby": 0,
    #                     "recruit_distant": 0, "recruit_nearby": 0,
    #                     "ngoi_ban_distant": 0, "ngoi_ban_nearby": 0
    #                 }
    #             elif role == "qc":
    #                 self.travel[province]["parttime"][role] = {"distant": 0, "nearby": 0}
            
    #         # Update the field if it exists
    #         if field in self.travel[province]["parttime"][role]:
    #             self.travel[province]["parttime"][role][field] = value
    #         else:
    #             # Debug message
    #             print(f"Warning: Field '{field}' not found in {role}")
        
    #     self.dataChanged.emit()

    # def add_additional_cost(self, category, name, unit_price, quantity, description="", is_dp_coding=False, provinces=None):
    #     """
    #     Add an additional custom cost.
        
    #     Args:
    #         category (str): First subtitle category
    #         name (str): Cost name
    #         unit_price (float): Unit price
    #         quantity (float): Quantity
    #         description (str): Optional description
    #         is_dp_coding (bool): Whether this is a DP Coding cost
    #         provinces (list): List of provinces this cost applies to
            
    #     Returns:
    #         bool: True if added successfully, False if name already exists
    #     """
    #     # Check if cost name already exists
    #     for cost in self.additional_costs:
    #         if cost["name"] == name:
    #             # Check if there's any overlap between existing provinces and new provinces
    #             existing_provinces = set(cost.get("provinces", []))
    #             new_provinces = set(provinces)
                
    #             # If there's any intersection, it means the same cost name exists for at least one of the same provinces
    #             if existing_provinces.intersection(new_provinces):
    #                 overlapping_provinces = existing_provinces.intersection(new_provinces)
    #                 return False, f"Cost name '{name}' already exists for province(s): {', '.join(overlapping_provinces)}"
                
    #     # Add new cost
    #     self.additional_costs.append({
    #         "category": category,
    #         "name": name,
    #         "unit_price": unit_price,
    #         "quantity": quantity,
    #         "description": description,
    #         "is_dp_coding": is_dp_coding,
    #         "provinces": provinces or []  # Default to empty list if None
    #     })
        
    #     self.dataChanged.emit()
    #     return True

    # def remove_additional_cost(self, index):
    #     """
    #     Remove an additional cost by index.
        
    #     Args:
    #         index (int): Index of the cost to remove
            
    #     Returns:
    #         bool: True if removed successfully, False if index out of range
    #     """
    #     if 0 <= index < len(self.additional_costs):
    #         self.additional_costs.pop(index)
    #         self.dataChanged.emit()
    #         return True
    #     return False
    
    # def has_custom_dp_coding_cost(self):
    #     """
    #     Check if there's a custom DP Coding cost in additional costs.
        
    #     Returns:
    #         bool: True if a custom DP Coding cost exists
    #     """
    #     for cost in self.additional_costs:
    #         if cost.get("is_dp_coding", False):
    #             return True
    #     return False
    
    # def get_custom_dp_coding_costs(self):
    #     """
    #     Get all custom DP Coding costs.
        
    #     Returns:
    #         list: List of DP Coding costs
    #     """
    #     return [cost for cost in self.additional_costs if cost.get("is_dp_coding", False)]

    # def get_custom_dp_coding_unit_price(self):
    #     """
    #     Get the unit price from custom DP Coding costs.
        
    #     Returns:
    #         float or None: Unit price if custom DP Coding cost exists, None otherwise
    #     """
    #     for cost in self.additional_costs:
    #         if cost.get("is_dp_coding", False):
    #             return cost.get("unit_price", 0)
    #     return None

    # def _get_audience_identifiers(self):
    #     """
    #     Transform target_audiences to a set of unique audience identifier strings.
        
    #     Returns:
    #         set: Set of audience identifier strings
    #     """
    #     target_audiences = set(
    #         [
    #             f"{ele['name']} - Age {ele['age_range']} - Income {ele['income_range']} - IR {ele['incident_rate']} - Complexity: {ele['complexity']}" 
    #             for ele in self.general.get("target_audiences", [])
    #         ]
    #     )
    #     return target_audiences

    # def _parse_audience_identifier(self, audience_id):
    #     """
    #     Parse audience identifier string back to components.
        
    #     Args:
    #         audience_id (str): Audience identifier string
            
    #     Returns:
    #         dict: Dictionary with parsed components
    #     """
    #     import re
        
    #     # Parse the audience identifier string
    #     # Format: "Name - Age [x, y] - Income [a, b] - IR z - Complexity: complexity_value"
    #     pattern = r"^(.+?) - Age (\[.+?\]) - Income (\[.+?\]) - IR (\d+) - Complexity: (.+)$"
    #     match = re.match(pattern, audience_id)
        
    #     if not match:
    #         return None
            
    #     name, age_range_str, income_range_str, incident_rate_str, complexity = match.groups()
        
    #     # Convert string representations back to proper types
    #     age_range = eval(age_range_str)  # Convert "[18, 65]" back to [18, 65]
    #     income_range = eval(income_range_str)  # Convert "[0, 0]" back to [0, 0]
    #     incident_rate = int(incident_rate_str)
        
    #     return {
    #         'name': name,
    #         'age_range': age_range,
    #         'income_range': income_range,
    #         'incident_rate': incident_rate,
    #         'complexity': complexity
    #     }

    # def _add_additional_costs_to_hierarchy(self, hierarchy, province):
    #     """
    #     Add additional costs to the cost hierarchy for a specific province.
        
    #     Args:
    #         hierarchy (dict): The hierarchical cost structure to update
    #         province (str): Province name (for filtering costs)
    #     """
    #     if not self.additional_costs:
    #         return
        
    #     # Process each additional cost
    #     for additional_cost in self.additional_costs:
    #         # Check if this cost applies to the current province
    #         cost_provinces = additional_cost.get("provinces", [])
    #         if province not in cost_provinces:
    #             continue  # Skip this cost for this province
                
    #         category = additional_cost.get("category", "OTHER")
    #         cost_name = additional_cost.get("name", "")
    #         unit_price = additional_cost.get("unit_price", 0)
    #         quantity = additional_cost.get("quantity", 0)
    #         description = additional_cost.get("description", "")
    #         is_dp_coding = additional_cost.get("is_dp_coding", False)
        
    #         # Skip DP Coding costs as they are handled in automatic DP calculation
    #         if is_dp_coding:
    #             continue
            
    #         # Skip if no cost
    #         total_cost = unit_price * quantity
    #         if total_cost == 0:
    #             continue
            
    #         # Find or create the category in hierarchy
    #         if category not in hierarchy:
    #             hierarchy[category] = {
    #                 "children": {},
    #                 "elements": [],
    #                 "cost": 0
    #             }
            
    #         # Create element for this additional cost
    #         element = {
    #             "code": "",  # Additional costs don't have codes
    #             "unit": "custom",
    #             "target_audience": "",  # Additional costs are global
    #             "base_cost": unit_price,
    #             "growth_rate": 100.0,  # No growth rate applied
    #             "element_cost": unit_price,
    #             "element_cost_formula": f"Custom cost: {unit_price:,.0f}",
    #             "coefficient": quantity,
    #             "coefficient_formula": f"Custom quantity: {quantity}",
    #             "total_cost": total_cost,
    #             "name": cost_name,  # Store the custom name
    #             "is_additional_cost": True,  # Flag to identify additional costs
    #             "description": description,
    #             "provinces": cost_provinces  # Store the provinces this cost applies to
    #         }
            
    #         # Add special identifier for DP Coding costs
    #         if is_dp_coding:
    #             element["coefficient_formula"] += " (Custom DP Coding - overrides automatic calculation)"
            
    #         # Add element to the category
    #         hierarchy[category]["elements"].append(element)
    #         hierarchy[category]["cost"] += total_cost

    # def calculate_hierarchical_project_cost(self, hierarchy_data):
    #     """
    #     Calculate detailed project costs organized hierarchically by subtitle levels
    #     and separated by province.
        
    #     Returns:
    #         dict: Hierarchical cost breakdown by province and subtitle levels
    #     """
    #     # Get key parameters
    #     project_type = self.general.get("project_type")
    #     classification = self.general.get("resp_classification", "L1")
    #     interview_length = self.general.get("interview_length", 0)
    #     provinces = self.general.get("provinces", [])
    #     target_audiences = set(
    #         [
    #             f'{ele["name"]} - Age {ele["age_range"]} - Income {ele["income_range"]} - IR {ele["incident_rate"]} - Complexity: {ele["complexity"]}' for ele in 
    #             self.general.get("target_audiences", [])
    #         ]
    #     )
        
    #     if not project_type or not provinces:
    #         return {"error": "Missing required parameters for cost calculation"}
        
    #     # Initialize results structure
    #     results = {
    #         "provinces": {},
    #         "total_cost": 0
    #     }
        
    #     # Check if element costs are available for this project type
    #     if project_type not in self.element_costs.costs:
    #         return results
        
    #     # # Get element costs DataFrame and metadata
    #     # project_costs = self.element_costs.costs[project_type]
        
    #     # # Handle both new format (dict with "data" key) and old format (directly DataFrame)
    #     # if isinstance(project_costs, dict) and "data" in project_costs:
    #     #     df = project_costs["data"]
    #     #     metadata = project_costs.get("metadata", {})
    #     # else:
    #     #     # Fallback for backward compatibility
    #     #     df = project_costs
    #     #     metadata = {}
        
    #     # # Determine column based on classification and interview length
    #     # # Try to use metadata if available
    #     # if metadata and "levels" in metadata and "lengths" in metadata and "length_ranges" in metadata:
    #     #     # Find the appropriate length range in metadata
    #     #     available_lengths = metadata.get("lengths", [])
    #     #     length_ranges = metadata.get("length_ranges", {})
            
    #     #     matching_length = None
    #     #     for length in available_lengths:
    #     #         min_length, max_length = length_ranges.get(length, (0, 60))
    #     #         if min_length <= interview_length <= max_length:
    #     #             matching_length = length
    #     #             break
                    
    #     #     if matching_length and classification in metadata.get("levels", []):
    #     #         cost_column = f"{classification} ({matching_length})"
    #     #     else:
    #     #         # Fall back to the old method if no match in metadata
    #     #         cost_column = self._get_column_name(classification, interview_length)
    #     # else:
    #     #     # Use the old method if no metadata
    #     #     if interview_length < 15:
    #     #         col_suffix = "(<15 min)"
    #     #     elif interview_length < 30:
    #     #         col_suffix = "(15-30 min)"
    #     #     elif interview_length < 45:
    #     #         col_suffix = "(30-45 min)"
    #     #     else:
    #     #         col_suffix = "(45-60 min)"
                
    #     #     cost_column = f"{classification} {col_suffix}"
        
    #     # # Skip if cost column doesn't exist
    #     # if cost_column not in df.columns:
    #     #     return results
        
    #     # # Process each province
    #     # for province in provinces:
    #     #     # Build the hierarchical cost structure for this province
    #     #     province_hierarchy = self._build_province_cost_hierarchy(
    #     #         df, cost_column, target_audiences, province
    #     #     )
            
    #     #     # Calculate total cost for this province
    #     #     province_total = self._calculate_hierarchy_total(province_hierarchy)
            
    #     #     # Add to results
    #     #     results["provinces"][province] = {
    #     #         "hierarchy": province_hierarchy,
    #     #         "total_cost": province_total
    #     #     }
            
    #     #     # Add to total project cost
    #     #     results["total_cost"] += province_total
        
    #     # return results

    # def _build_province_cost_hierarchy(self, df, cost_column, target_audiences, province):
    #     """
    #     Build a hierarchical cost structure for a specific province.
        
    #     Args:
    #         df (DataFrame): Element costs DataFrame
    #         cost_column (str): Column name containing the cost values
    #         target_audiences (list): List of target audiences
    #         province (str): Province name
            
    #     Returns:
    #         dict: Hierarchical cost structure for this province
    #     """
    #     # Make a copy to avoid modifying the original
    #     df_copy = df.copy()
        
    #     # Convert NaN values to empty strings for subtitle columns
    #     for col in df_copy.columns:
    #         if col.startswith("Subtitle ") or col == "Unit":
    #             df_copy[col] = df_copy[col].fillna("")
        
    #     # Create an empty hierarchy
    #     hierarchy = {}
        
    #     # Process each row
    #     for _, row in df_copy.iterrows():
    #         # Skip rows with no cost value or zero cost
    #         base_cost = row.get(cost_column, 0)
    #         # if pd.isna(base_cost) or base_cost == 0:
    #         #     continue
            
    #         # Get all subtitle values and identify first non-empty subtitle
    #         subtitles = []
    #         first_subtitle = None
    #         subtitle_5 = ""
            
    #         for i in range(1, 6):  # Subtitles 1-5
    #             subtitle = row.get(f"Subtitle {i}", "")
    #             if i == 5:
    #                 subtitle_5 = subtitle  # Save Subtitle 5 for element cost name
                    
    #             if subtitle:  # Only add non-empty subtitles
    #                 subtitles.append(subtitle)
    #                 if first_subtitle is None:
    #                     first_subtitle = subtitle
            
    #         # Get element details
    #         subtitle_code = row.get("Subtitle Code", "")
    #         unit = row.get("Unit", "")
            
    #         # Skip if no subtitles found
    #         if not subtitles:
    #             continue

    #         # Check if this is a CLT interview element that needs to be expanded for respondent visits
    #         is_clt_interview = (self.general.get("project_type") == "CLT" and 
    #                         first_subtitle == "INTERVIEWER" and 
    #                         "phỏng vấn tại CLT" in subtitle_5)

    #         # Find the right place in the hierarchy
    #         current_level = hierarchy
    #         for i, subtitle in enumerate(subtitles):
    #             # Create this subtitle level if it doesn't exist
    #             if subtitle not in current_level:
    #                 current_level[subtitle] = {
    #                     "children": {},
    #                     "elements": [],
    #                     "cost": 0
    #                 }
                
    #             # Move to next level if this isn't the last subtitle
    #             if i < len(subtitles) - 1:
    #                 current_level = current_level[subtitle]["children"]
    #             else:
    #                 # This is the last subtitle - add the element
                    
    #                 # Special case for TRAVEL - don't separate by target audience
    #                 if self._contains_term(first_subtitle, ["TRAVEL", "OTHER"]):
    #                     # Prepare element data for coefficient calculation
    #                     element_data = {
    #                         "first_subtitle": first_subtitle,
    #                         "element_cost_name": subtitle_5,
    #                         "unit": unit,
    #                         "base_element_cost": base_cost,
    #                         "subtitles": subtitles
    #                     }
                        
    #                     # Get aggregated sample sizes across all audiences
    #                     aggregated_sample_sizes = self._get_aggregated_sample_sizes(province)
                        
    #                     if self._contains_term(first_subtitle, ["TRAVEL"]):
    #                         # Calculate coefficient using the travel rules with all sample sizes
    #                         result = self._calculate_travel_coefficient(
    #                             province, element_data, aggregated_sample_sizes
    #                         )
    #                     else:
                            
    #                         # Use modified OTHER coefficient calculation without audience
    #                         result = self._calculate_other_coefficient(
    #                             province, None, element_data, aggregated_sample_sizes
    #                         )

    #                     # Check if result is a list (multiple elements by level)
    #                     if isinstance(result, list):
    #                         # Create a separate element for each level
    #                         for coefficient, coefficient_formula, updated_element_cost, element_cost_formula, level in result:
    #                             # Calculate total cost
    #                             total_cost = updated_element_cost * coefficient
                                
    #                             # Skip elements with zero total cost
    #                             if total_cost == 0:
    #                                 continue
                                
    #                             # Create element with level in name
    #                             element = {
    #                                 "code": subtitle_code,
    #                                 "unit": unit,
    #                                 "base_cost": base_cost,
    #                                 "element_cost": updated_element_cost,
    #                                 "element_cost_formula": element_cost_formula,
    #                                 "coefficient": coefficient,
    #                                 "coefficient_formula": coefficient_formula,
    #                                 "total_cost": total_cost,
    #                                 "level": level  # Add level info
    #                             }
                                
    #                             current_level[subtitle]["elements"].append(element)
    #                             current_level[subtitle]["cost"] += total_cost
    #                     else:
    #                         # Regular single element (not split by level)
    #                         if self._contains_term(first_subtitle, ["TRAVEL"]):
    #                             coefficient, coefficient_formula, updated_element_cost, element_cost_formula = result
    #                         else:
    #                             coefficient, coefficient_formula = result
    #                             updated_element_cost = element_data.get("base_element_cost", 0)
    #                             element_cost_formula = ""
    #                         # Calculate total cost with updated element cost
    #                         total_cost = updated_element_cost * coefficient
                            
    #                         # Skip elements with zero total cost
    #                         if total_cost == 0:
    #                             continue
                            
    #                         # Create a single element (not per audience)
    #                         element = {
    #                             "code": subtitle_code,
    #                             "unit": unit,
    #                             "base_cost": base_cost,
    #                             "element_cost": updated_element_cost,
    #                             "element_cost_formula": element_cost_formula if element_cost_formula else f"Base cost: {base_cost:,.0f}",
    #                             "coefficient": coefficient,
    #                             "coefficient_formula": coefficient_formula,
    #                             "total_cost": total_cost
    #                         }
                            
    #                         current_level[subtitle]["elements"].append(element)
    #                         current_level[subtitle]["cost"] += total_cost

    #                 else:
    #                     # Check if this element should be separated by target audience
    #                     should_separate = self._should_separate_by_target_audience(first_subtitle, subtitle_5)
                        
    #                     if should_separate and target_audiences:
    #                         # Separate by target audience (existing logic)
    #                         for audience in target_audiences:
    #                             # Get growth rate for this audience in this province
    #                             growth_rate = self._get_audience_growth_rate(province, audience)
                                
    #                             # Prepare element data for coefficient calculation
    #                             element_data = {
    #                                 "first_subtitle": first_subtitle,
    #                                 "element_cost_name": subtitle_5,
    #                                 "unit": unit,
    #                                 "base_element_cost": base_cost,
    #                                 "subtitles": subtitles
    #                             }
                                
    #                             # Update base_cost from industries.json if conditions are met
    #                             if audience:  # audience is available in this scope
    #                                 updated_base_cost = self._get_updated_base_cost_from_industries(base_cost, subtitle_5, audience)
    #                                 if updated_base_cost != base_cost:
    #                                     element_data["base_element_cost"] = updated_base_cost
                                
    #                             # Get sample sizes for calculations
    #                             sample_sizes = self._get_audience_sample_sizes(province, audience)
                                
    #                             # Special handling for CLT interview with multiple respondent visits
    #                             if is_clt_interview:
    #                                 # Get respondent visits from general tab
    #                                 clt_respondent_visits = self.general.get("clt_respondent_visits", 1)
                                    
    #                                 # Calculate once to get the basic values
    #                                 coefficient, formula, updated_element_cost = self._calculate_coefficient_by_rules(
    #                                     province, audience, element_data, sample_sizes
    #                                 )
                                    
    #                                 # Only proceed if coefficient is non-zero
    #                                 if coefficient > 0:
    #                                     # Create multiple elements - one for each visit
    #                                     for visit_num in range(1, clt_respondent_visits + 1):
    #                                         # Create visit-specific name
    #                                         visit_element_name = f"{subtitle_5} - lần thứ {visit_num}"
    #                                         visit_formula = f"{formula} (visit {visit_num} of {clt_respondent_visits})"
                                            
    #                                         # Calculate adjusted cost with growth rate if applicable
    #                                         if self._contains_term(subtitle_5, ["phiếu"]):
    #                                             adjusted_cost = updated_element_cost * growth_rate / 100
    #                                             element_cost_formula = f"{updated_element_cost:,.0f} * {growth_rate}% = {adjusted_cost:,.0f}"
    #                                         else:
    #                                             adjusted_cost = updated_element_cost
    #                                             element_cost_formula = f"{updated_element_cost:,.0f} (growth rate not applied)"
                                            
    #                                         # Calculate total cost
    #                                         total_cost = adjusted_cost * coefficient
                                            
    #                                         # Create element with visit-specific name
    #                                         element = {
    #                                             "code": subtitle_code,
    #                                             "unit": unit,
    #                                             "target_audience": audience,
    #                                             "base_cost": base_cost,
    #                                             "growth_rate": growth_rate,
    #                                             "element_cost": adjusted_cost,
    #                                             "element_cost_formula": element_cost_formula,
    #                                             "coefficient": coefficient,
    #                                             "coefficient_formula": visit_formula,
    #                                             "total_cost": total_cost,
    #                                             "name": visit_element_name  # Add the visit-specific name
    #                                         }
                                            
    #                                         current_level[subtitle]["elements"].append(element)
    #                                         current_level[subtitle]["cost"] += total_cost
    #                             else:
    #                                 # Calculate coefficient using the complex rules
    #                                 coefficient, coefficient_formula, updated_element_cost = self._calculate_coefficient_by_rules(
    #                                     province, audience, element_data, sample_sizes
    #                                 )
                                    
    #                                 # Only apply growth rate for INTERVIEWER and INCENTIVE categories where element contains "phiếu"
    #                                 if (self._contains_term(first_subtitle, ["INTERVIEWER", "INCENTIVE"]) and
    #                                     self._contains_term(subtitle_5, ["phiếu"])):
    #                                     adjusted_cost = updated_element_cost * growth_rate / 100
    #                                     element_cost_formula = f"{updated_element_cost:,.0f} * {growth_rate}% = {adjusted_cost:,.0f}"
    #                                 else:
    #                                     adjusted_cost = updated_element_cost
    #                                     element_cost_formula = f"{updated_element_cost:,.0f} (growth rate not applied)"
                                    
    #                                 # Calculate total cost
    #                                 total_cost = adjusted_cost * coefficient
                                    
    #                                 # Skip elements with zero total cost
    #                                 if total_cost == 0:
    #                                     continue
                                    
    #                                 # Adjust element cost formula if the cost was updated
    #                                 if updated_element_cost != base_cost:
    #                                     element_cost_formula = f"Updated cost: {updated_element_cost:,.0f} from settings instead of {base_cost:,.0f}\n{element_cost_formula}"

    #                                 # Create element with detailed breakdown
    #                                 element = {
    #                                     "code": subtitle_code,
    #                                     "unit": unit,
    #                                     "target_audience": audience,
    #                                     "base_cost": base_cost,
    #                                     "growth_rate": growth_rate,
    #                                     "element_cost": adjusted_cost,
    #                                     "element_cost_formula": element_cost_formula,
    #                                     "coefficient": coefficient,
    #                                     "coefficient_formula": coefficient_formula,
    #                                     "total_cost": total_cost
    #                                 }
        
    #                                 current_level[subtitle]["elements"].append(element)
    #                                 current_level[subtitle]["cost"] += total_cost                             
    #                     elif target_audiences:
    #                         # Aggregate across all target audiences
    #                         # Get aggregated sample sizes and calculate average growth rate
    #                         aggregated_sample_sizes = self._get_aggregated_sample_sizes(province)
    #                         avg_growth_rate = self._get_average_growth_rate(province, target_audiences)
                            
    #                         # Prepare element data for coefficient calculation
    #                         element_data = {
    #                             "first_subtitle": first_subtitle,
    #                             "element_cost_name": subtitle_5,
    #                             "unit": unit,
    #                             "base_element_cost": base_cost,
    #                             "subtitles": subtitles
    #                         }
                            
    #                         # Calculate coefficient using aggregated data (no specific audience)
    #                         coefficient, coefficient_formula, updated_element_cost = self._calculate_coefficient_by_rules(
    #                             province, None, element_data, aggregated_sample_sizes
    #                         )
                            
    #                         # Only apply growth rate for INTERVIEWER and INCENTIVE categories where element contains "phiếu"
    #                         if (self._contains_term(first_subtitle, ["INTERVIEWER", "INCENTIVE"]) and
    #                             self._contains_term(subtitle_5, ["phiếu"])):
    #                             adjusted_cost = updated_element_cost * avg_growth_rate / 100
    #                             element_cost_formula = f"{updated_element_cost:,.0f} * {avg_growth_rate:.1f}% (avg) = {adjusted_cost:,.0f}"
    #                         else:
    #                             adjusted_cost = updated_element_cost
    #                             element_cost_formula = f"{updated_element_cost:,.0f} (growth rate not applied)"
                            
    #                         # Calculate total cost
    #                         total_cost = adjusted_cost * coefficient
                            
    #                         # Skip elements with zero total cost
    #                         if total_cost == 0:
    #                             continue
                            
    #                         # Adjust element cost formula if the cost was updated
    #                         if updated_element_cost != base_cost:
    #                             element_cost_formula = f"Updated cost: {updated_element_cost:,.0f} from settings instead of {base_cost:,.0f}\n{element_cost_formula}"

    #                         # Create aggregated element
    #                         element = {
    #                             "code": subtitle_code,
    #                             "unit": unit,
    #                             "target_audience": "All Audiences",  # Show as aggregated
    #                             "base_cost": base_cost,
    #                             "growth_rate": avg_growth_rate,
    #                             "element_cost": adjusted_cost,
    #                             "element_cost_formula": element_cost_formula,
    #                             "coefficient": coefficient,
    #                             "coefficient_formula": f"{coefficient_formula} (aggregated across all audiences)",
    #                             "total_cost": total_cost
    #                         }

    #                         current_level[subtitle]["elements"].append(element)
    #                         current_level[subtitle]["cost"] += total_cost
    #                     else:
    #                         # No target audiences - just add the element directly
    #                         # Calculate coefficient using simplified rules
    #                         element_data = {
    #                             "first_subtitle": first_subtitle,
    #                             "element_cost_name": subtitle_5,
    #                             "unit": unit,
    #                             "base_element_cost": base_cost,
    #                             "subtitles": subtitles
    #                         }
                            
    #                         coefficient, coefficient_formula, updated_element_cost = self._calculate_coefficient_by_rules(
    #                             province, None, element_data, {"total": 0, "by_type": {}}
    #                         )
                            
    #                         # Calculate total cost
    #                         total_cost = updated_element_cost * coefficient
                            
    #                         # Skip elements with zero total cost
    #                         if total_cost == 0:
    #                             continue
                            
    #                         # Adjust element cost formula if the cost was updated
    #                         element_cost_formula = f"Base cost: {base_cost:,.0f}"
    #                         if updated_element_cost != base_cost:
    #                             element_cost_formula = f"Updated cost: {updated_element_cost:,.0f}"
                            
    #                         element = {
    #                             "code": subtitle_code,
    #                             "unit": unit,
    #                             "base_cost": base_cost,
    #                             "element_cost": updated_element_cost,
    #                             "element_cost_formula": element_cost_formula,
    #                             "coefficient": coefficient,
    #                             "coefficient_formula": coefficient_formula,
    #                             "total_cost": total_cost
    #                         }
                            
    #                         current_level[subtitle]["elements"].append(element)
    #                         current_level[subtitle]["cost"] += total_cost

    #     # Add additional costs to the hierarchy
    #     self._add_additional_costs_to_hierarchy(hierarchy, province)

    #     # Prune empty branches
    #     self._prune_empty_subtitles(hierarchy)
        
    #     # Calculate rollup costs
    #     self._calculate_rollup_costs(hierarchy)

    #     return hierarchy

    # def _prune_empty_subtitles(self, hierarchy):
    #     """
    #     Recursively remove subtitle nodes that have no elements and no children.
        
    #     Args:
    #         hierarchy (dict): Hierarchical cost structure
    #     """
    #     subtitles_to_remove = []
        
    #     for subtitle, data in hierarchy.items():
    #         # Recursively prune children
    #         if data["children"]:
    #             self._prune_empty_subtitles(data["children"])
            
    #         # Check if this subtitle is empty after pruning children
    #         if not data["elements"] and not data["children"]:
    #             subtitles_to_remove.append(subtitle)
        
    #     # Remove empty subtitles
    #     for subtitle in subtitles_to_remove:
    #         del hierarchy[subtitle]

    # def _calculate_coefficient_by_rules(self, province, audience, element_data, sample_sizes):
    #     """
    #     Calculate coefficient based on complex rules.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_data (dict): Element data including subtitle hierarchy, unit, etc.
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation, updated_element_cost)
    #     """
    #     # Get first subtitle (category)
    #     first_subtitle = element_data.get("first_subtitle", "")
        
    #     # Get element cost name (subtitle 5)
    #     element_cost_name = element_data.get("element_cost_name", "")
    
    #     # Get unit
    #     unit = element_data.get("unit", "")
        
    #     # Get base element cost
    #     base_element_cost = element_data.get("base_element_cost", 0)
        
    #     # Initialize coefficient, formula, and updated element cost
    #     coefficient = 1.0  # Default
    #     formula = "Default coefficient (1.0)"
    #     updated_element_cost = base_element_cost  # Default to no change
        
    #     # Calculate based on first subtitle (case-insensitive)
    #     if self._contains_term(first_subtitle, ["INTERVIEWER"]):
    #         coefficient, formula, updated_element_cost = self._calculate_interviewer_coefficient(
    #             province, audience, element_cost_name, sample_sizes, base_element_cost
    #         )
    #     elif self._contains_term(first_subtitle, ["SUPERVISOR", "ASSISTANT"]):
    #         coefficient, formula = self._calculate_supervisor_coefficient(
    #             province, audience, element_cost_name, sample_sizes
    #         )
    #     elif self._contains_term(first_subtitle, ["QC"]):
    #         coefficient, formula, updated_element_cost = self._calculate_qc_coefficient(
    #             province, audience, element_cost_name, sample_sizes, base_element_cost
    #         )
    #     elif self._contains_term(first_subtitle, ["DP"]):
    #         coefficient, formula, updated_element_cost = self._calculate_dp_coefficient(
    #             province, audience, element_cost_name, unit, sample_sizes, base_element_cost
    #         )
    #     elif self._contains_term(first_subtitle, ["INCENTIVE"]):
    #         coefficient, formula = self._calculate_incentive_coefficient(
    #             province, audience, element_cost_name, sample_sizes
    #         )
    #     elif self._contains_term(first_subtitle, ["OTHER"]):
    #         coefficient, formula = self._calculate_other_coefficient(
    #             province, audience, element_data, sample_sizes
    #         )
    #     elif self._contains_term(first_subtitle, ["STATIONARY"]):
    #         coefficient, formula, updated_element_cost = self._calculate_stationary_coefficient(
    #             element_cost_name, base_element_cost, element_data, sample_sizes, province
    #         )
    #     elif self._contains_term(first_subtitle, ["COMMUNICATION"]):
    #         coefficient, formula = self._calculate_communication_coefficient(
    #             element_data, sample_sizes
    #         )
        
    #     return coefficient, formula, updated_element_cost

    # def _contains_term(self, text, terms, case_sensitive=False):
    #     """
    #     Check if any of the terms appear in the text.
        
    #     Args:
    #         text (str): Text to check
    #         terms (list): List of terms to look for
    #         case_sensitive (bool): Whether the search should be case-sensitive
            
    #     Returns:
    #         bool: True if any term is found, False otherwise
    #     """
    #     if not text or not isinstance(text, str):
    #         return False
        
    #     # Always do case-insensitive comparison for term matching
    #     text = text.lower()
    #     terms = [term.lower() for term in terms if isinstance(term, str)]
        
    #     # Check each term separately to handle substrings properly
    #     for term in terms:
    #         if term in text:
    #             return True
        
    #     return False

    # def _get_audience_sample_sizes(self, province, audience):
    #     """
    #     Get sample sizes for all sample types for a specific audience in a province.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience identifier string
            
    #     Returns:
    #         dict: Dictionary with sample sizes by sample type and total
    #     """
    #     result = {
    #         "by_type": {},
    #         "total": 0,
    #         "daily_sup_targets": {},
    #         "total_daily_sup_target": 0,
    #         "interviewer_target": 2
    #     }
        
    #     # Parse the audience identifier to get components
    #     audience_components = self._parse_audience_identifier(audience)
    #     if not audience_components:
    #         return result
        
    #     # Check if province exists in samples
    #     if province not in self.samples:
    #         return result
        
    #     # Find matching audience entries in the samples list
    #     matching_entries = []
    #     for sample_entry_key, sample_entry_value in self.samples[province].items():
    #         # Check if all components match
    #         if (sample_entry_value.get('name') == audience_components['name'] and
    #             sample_entry_value.get('age_range') == audience_components['age_range'] and
    #             sample_entry_value.get('income_range') == audience_components['income_range'] and
    #             sample_entry_value.get('incident_rate') == audience_components['incident_rate'] and
    #             sample_entry_value.get('complexity') == audience_components['complexity']):
    #             matching_entries.append(sample_entry_value)
        
    #     # Group by sample_type and aggregate
    #     for entry in matching_entries:
    #         sample_type = entry.get('sample_type', 'Unknown')
    #         sample_size = entry.get('sample_size', 0)
    #         daily_sup_target = entry.get('daily_sup_target', 0)
    #         interviewer_target = entry.get('target_for_interviewers', 2)
            
    #         # Update interviewer target (assuming it's the same for all entries)
    #         result["interviewer_target"] = interviewer_target
            
    #         # Aggregate by sample type
    #         if sample_type in result["by_type"]:
    #             result["by_type"][sample_type] += sample_size
    #             result["daily_sup_targets"][sample_type] += daily_sup_target
    #         else:
    #             result["by_type"][sample_type] = sample_size
    #             result["daily_sup_targets"][sample_type] = daily_sup_target
            
    #         # Add to totals
    #         result["total"] += sample_size
    #         result["total_daily_sup_target"] += daily_sup_target
        
    #     return result

    # def _calculate_interviewer_coefficient(self, province, audience, element_cost_name, sample_sizes, base_element_cost):
    #     """
    #     Calculate coefficient for INTERVIEWER category with updated rules.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
    #         base_element_cost (float): Base element cost
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation, updated_element_cost)
    #     """
    #     # Get total sample size
    #     total_sample_size = sample_sizes["total"]

    #     # Default to no cost update
    #     updated_element_cost = base_element_cost

    #     # Check if this is a CLT project with interview elements
    #     project_type = self.general.get("project_type", "")
    #     if project_type == "CLT" or project_type == "HUT":
    #         # Get total sample size excluding Pilot
    #         total_excluding_pilot = total_sample_size
    #         if "Pilot" in sample_sizes["by_type"]:
    #             total_excluding_pilot -= sample_sizes["by_type"]["Pilot"]
            
    #         # Handle CLT-specific INTERVIEWER conditions
    #         if self._contains_term(element_cost_name, ["recruit"]) or self._contains_term(element_cost_name, ["phỏng vấn tại CLT"]):
    #             # Chi phí phiếu recruit and Chi phí phỏng vấn tại CLT
    #             return total_excluding_pilot, f"Tổng sample size (không tính Pilot): {total_excluding_pilot}", updated_element_cost

    #         elif self._contains_term(element_cost_name, ["khác"]):
    #             # Chi phí khác
    #             clt_respondent_visits = self.general.get("clt_respondent_visits", 1)
    #             clt_failure_rate = self.general.get("clt_failure_rate", 0) / 100  # Convert percentage to decimal
                
    #             if clt_respondent_visits > 1:
    #                 coefficient = total_excluding_pilot * clt_failure_rate
    #                 formula = f"Total sample size (excluding Pilot) * Failure rate = {total_excluding_pilot} * {clt_failure_rate:.2f} = {coefficient:.2f}"
    #                 return coefficient, formula, updated_element_cost
    #             else:
    #                 return 0, "Respondent visits <= 1: Qty = 0", updated_element_cost
                    
    #         elif self._contains_term(element_cost_name, ["IDI"]):
    #             # Chi phí IDI
    #             clt_sample_recruit_idi = self.general.get("clt_sample_recruit_idi", 0)
    #             return clt_sample_recruit_idi, f"Sample recruit IDI count: {clt_sample_recruit_idi}", updated_element_cost
                
    #         elif self._contains_term(element_cost_name, ["thuê tablet < 9 inch", "thuê tablet >= 9 inch", "thuê laptop"]):
    #             # Check if device type matches
    #             clt_device_type = self.general.get("clt_device_type", "Tablet >= 9 inch")
                
    #             if self._contains_term(element_cost_name, ["thuê tablet < 9 inch"]) and self._contains_term(clt_device_type, ["Tablet < 9 inch"]):
    #                 # Device type matches - apply different cost based on usage duration
    #                 tablet_duration = self.general.get("clt_tablet_usage_duration", "<= 15 phút")
    #                 if tablet_duration == "<= 15 phút":
    #                     updated_element_cost = 5000
    #                 else:  # "> 15 phút"
    #                     updated_element_cost = 8000
    #                 return total_excluding_pilot, f"Device type matches ({clt_device_type}, {tablet_duration}): Total sample size (excluding Pilot) = {total_excluding_pilot}", updated_element_cost
    #             elif (self._contains_term(element_cost_name, ["thuê tablet >= 9 inch"]) and self._contains_term(clt_device_type, ["Tablet >= 9 inch"])) or \
    #             (self._contains_term(element_cost_name, ["thuê laptop"]) and self._contains_term(clt_device_type, ["Laptop"])):
    #                 # Device type matches
    #                 return total_excluding_pilot, f"Device type matches ({clt_device_type}): Total sample size (excluding Pilot) = {total_excluding_pilot}", updated_element_cost
    #             else:
    #                 # Device type doesn't match
    #                 return 0, f"Device type doesn't match (using {clt_device_type}): Qty = 0", updated_element_cost

    #     # If not a CLT interview or not handling respondent visits, continue with original logic
    #     # Check for specific sample types in element cost name
    #     for sample_type in SAMPLE_TYPES:
    #         if self._contains_term(element_cost_name, [sample_type]):
    #             sample_size = sample_sizes["by_type"].get(sample_type, 0)
    #             return sample_size, f"Sample size phiếu {sample_type}: {sample_size}", updated_element_cost
        
    #     # Check for "thuê tablet" term
    #     if self._contains_term(element_cost_name, ["thuê tablet"]):
    #         # Check if platform is iField
    #         if self._contains_term(self.general.get("platform", ""), ["ifield"]):
    #             return total_sample_size, f"Tổng sample size (iField platform): {total_sample_size}", updated_element_cost
    #         else:
    #             return 0, "Platform is not iField: Qty = 0", updated_element_cost
        
    #     # Check for "thuê table" term
    #     if self._contains_term(element_cost_name, ["thuê table"]):
    #         return total_sample_size, f"Tổng sample size: {total_sample_size}", updated_element_cost
        
    #     # Check for "gửi xe" term
    #     if self._contains_term(element_cost_name, ["gửi xe"]):
    #         # Update element cost to parking fee from settings
    #         parking_fee = self.settings.get("parking_fee", 5000)
    #         updated_element_cost = parking_fee
    #         # New rule: Use total sample size of all sample types for this audience and province
    #         total_audience_sample_size = sum(sample_sizes["by_type"].values())
    #         return total_audience_sample_size, f"Tổng sample size for audience '{audience}': {total_audience_sample_size}", updated_element_cost
        
    #     # Check for "quận xa" term
    #     if self._contains_term(element_cost_name, ["quận xa"]):
    #         # Update element cost to distant district fee from settings
    #         distant_district_fee = self.settings.get("distant_district_fee", 5000)
    #         updated_element_cost = distant_district_fee
    #         total_audience_sample_size = sum(sample_sizes["by_type"].values())
    #         return 0.2 * total_audience_sample_size, f"20% of total sample size for distant districts: {total_audience_sample_size} * 20%\nCost updated to {distant_district_fee:.0f})", updated_element_cost
        
    #     # Default
    #     return 1, "Default interviewer Qty: 1", updated_element_cost

    # def _calculate_supervisor_coefficient(self, province, audience, element_cost_name, sample_sizes):
    #     """
    #     Calculate coefficient for SUPERVISOR/ASSISTANT category.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation)
    #     """
    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     clt_sample_size_per_day = self.general.get("clt_sample_size_per_day", 1)

    #     if project_type == "CLT" or project_type == "HUT":
    #         # Get total sample size excluding Pilot
    #         total_sample_size = sample_sizes["total"]
    #         total_excluding_pilot = total_sample_size
    #         if "Pilot" in sample_sizes["by_type"]:
    #             total_excluding_pilot -= sample_sizes["by_type"]["Pilot"]
            
    #         # Get daily SUP target excluding Pilot
    #         daily_sup_target_excluding_pilot = sample_sizes["total_daily_sup_target"]
    #         if "Pilot" in sample_sizes["daily_sup_targets"]:
    #             daily_sup_target_excluding_pilot -= sample_sizes["daily_sup_targets"]["Pilot"]
            
    #         # Get clt_respondent_visits from general data
    #         clt_respondent_visits = self.general.get("clt_respondent_visits", 1)
            
    #         # Handle CLT-specific SUPERVISOR/ASSISTANT conditions
    #         if self._contains_term(element_cost_name, ["set up - Pre-field"]):
    #             return clt_respondent_visits, f"Số ngày CLT: {clt_respondent_visits}"

    #         # (Sample size (Main, Booster)/ Số lượng PVV/(Target/PVV))+2
    #         elif self._contains_term(element_cost_name, ["quản lý recruit - On-field"]):
    #             # Calculate total daily SUP target Main + Booster
    #             coefficient = 0
    #             formula_parts = ["Target ngày của SUP (Main + Booster) + 2:"]

    #             for sample_type in ["Main", "Booster"]:
    #                 daily_sup_target = sample_sizes["daily_sup_targets"].get(sample_type, 0)
    #                 if daily_sup_target > 0:
    #                     coefficient += round(daily_sup_target, 1)
    #                     formula_parts.append(f"  - {sample_type}: {daily_sup_target:.2f}")

    #             formula = "\n".join(formula_parts)
    #             formula += f"\nChi phí SUP recruit: Qty = {coefficient}"

    #             return coefficient, formula

    #         elif self._contains_term(element_cost_name, ["quản lý ngồi bàn - On-field"]):
    #             # Calculate Qty = (Sample size (Main, booster)/ (Target/ngay))+2
    #             if clt_sample_size_per_day:
    #                 coefficient = round(total_excluding_pilot / clt_sample_size_per_day + 2, 1)
    #                 formula = (
    #                     f"[Sample size (không tính Pilot) / Target ngày của SUP] + 2 = " +
    #                     f"{total_excluding_pilot} / {clt_sample_size_per_day} + 2 = {coefficient}"
    #                 )
    #             else:
    #                 coefficient = 0
    #                 formula = "Target ngày của SUP không hợp lệ: Qty = 0"
                
    #             return coefficient, formula
            
    #         elif self._contains_term(element_cost_name, ["clean data, report - Post-field"]):
    #             return 1, "Fixed coefficient: 1"
            
    #         elif self._contains_term(element_cost_name, ["Assistant - set up"]):
    #             # Use the value from general tab instead of hardcoded 1
    #             assistant_setup_days = self.general.get("clt_assistant_setup_days", 1)
    #             return assistant_setup_days, f"Chi phí Assistant - set up: Qty = {assistant_setup_days} days"

    #         elif self._contains_term(element_cost_name, ["Assistant - on field"]):
    #             coefficient = round(total_excluding_pilot / clt_sample_size_per_day, 1)
    #             formula = (
    #                 f"[Sample size (không tính Pilot) / Target ngày của SUP]:" +
    #                 f"{total_excluding_pilot} / {clt_sample_size_per_day} = {coefficient}"
    #             )
    #             return coefficient, formula
                    
    #         elif self._contains_term(element_cost_name, ["IDI"]):
    #             # Chi phí IDI
    #             clt_sample_recruit_idi = self.general.get("clt_sample_recruit_idi", 0)
    #             coefficient = round(clt_sample_recruit_idi / 15, 1)
    #             formula = f"Số sample recruit IDI / 15: {clt_sample_recruit_idi} / 15 = {coefficient}"
    #             return coefficient, formula

    #     # Proceed with standard calculation for non-CLT or unmatched CLT items

    #     # For costs containing "Chi phí quản lý", exclude "Pilot" sample type from daily SUP target
    #     if self._contains_term(element_cost_name, ["quản lý"]):
    #         # Calculate total daily SUP target excluding Pilot
    #         total_daily_sup_target = sample_sizes["total_daily_sup_target"]
    #         if "Pilot" in sample_sizes["daily_sup_targets"]:
    #             pilot_target = sample_sizes["daily_sup_targets"]["Pilot"]
    #             total_daily_sup_target -= pilot_target
            
    #         # Build formula details
    #         formula_parts = ["Daily SUP targets (excluding Pilot):"]
    #         for sample_type, daily_sup_target in sample_sizes["daily_sup_targets"].items():
    #             if sample_type != "Pilot" and daily_sup_target > 0:
    #                 formula_parts.append(f"  - {sample_type}: {daily_sup_target:.2f}")
            
    #         formula = "\n".join(formula_parts)
    #         formula += f"\nTotal Daily SUP Target (excluding Pilot): {total_daily_sup_target:.2f}"
            
    #         return total_daily_sup_target, formula
    #     else:
    #         # Sum of all daily SUP targets
    #         total_daily_sup_target = sample_sizes["total_daily_sup_target"]
            
    #         # Build formula details
    #         formula_parts = ["Daily SUP targets:"]
    #         for sample_type, daily_sup_target in sample_sizes["daily_sup_targets"].items():
    #             if daily_sup_target > 0:
    #                 formula_parts.append(f"  - {sample_type}: {daily_sup_target:.2f}")
            
    #         formula = "\n".join(formula_parts)
    #         formula += f"\nTotal Daily SUP Target: {total_daily_sup_target:.2f}"
            
    #         return total_daily_sup_target, formula

    # def _calculate_qc_coefficient(self, province, audience, element_cost_name, sample_sizes, base_element_cost):
    #     """
    #     Calculate coefficient for QC category with updated rules.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
    #         base_element_cost (float): Base element cost
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation, updated_element_cost)
    #     """
    #     # Get total sample size
    #     total_sample_size = sample_sizes["total"]
        
    #     # Get total sample size excluding Pilot
    #     total_excluding_pilot = total_sample_size
    #     if "Pilot" in sample_sizes["by_type"]:
    #         total_excluding_pilot -= sample_sizes["by_type"]["Pilot"]
        
    #     # Get CLT sample size per day from General Tab
    #     clt_sample_size_per_day = self.general.get("clt_sample_size_per_day", 1)

    #     # Default to no cost update
    #     updated_element_cost = base_element_cost

    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     if project_type == "CLT":
    #         # Handle CLT-specific QC conditions
    #         if self._contains_term(element_cost_name, ["IDI"]):
    #             # Chi phí IDI
    #             clt_sample_recruit_idi = self.general.get("clt_sample_recruit_idi", 0)
    #             return clt_sample_recruit_idi, f"Sample recruit IDI count: {clt_sample_recruit_idi}", updated_element_cost
    #         elif self._contains_term(element_cost_name, ["CLT"]):
    #             # Chi phí QC tại CLT
    #             coefficient = round(total_excluding_pilot / clt_sample_size_per_day * 2, 1)
    #             formula = f"Tổng sample (không tính Pilot) / Target ngày * 2: {total_excluding_pilot} / {clt_sample_size_per_day} * 2= {coefficient}"
    #             return coefficient, formula, updated_element_cost

    #     # Check for "thuê tablet" term
    #     if self._contains_term(element_cost_name, ["thuê laptop"]):
    #         coefficient = round(total_excluding_pilot / clt_sample_size_per_day, 1)
    #         formula = f"Tổng sample (không tính Pilot) / Target ngày: {total_excluding_pilot} / {clt_sample_size_per_day} = {coefficient}"
    #         return coefficient, formula, updated_element_cost

    #     # Check for "gửi xe" term
    #     elif self._contains_term(element_cost_name, ["gửi xe"]):
    #         # Update element cost to parking fee from settings
    #         parking_fee = self.settings.get("parking_fee", 5000)
    #         updated_element_cost = parking_fee
    #         return 1, f"Fixed Qty for parking: 1 (Cost updated to {parking_fee:,.0f})", updated_element_cost

    #     # Check for "quận xa" term
    #     elif self._contains_term(element_cost_name, ["quận xa"]):
    #         # Update element cost to distant district fee from settings
    #         distant_district_fee = self.settings.get("distant_district_fee", 5000)
    #         updated_element_cost = distant_district_fee
    #         total_audience_sample_size = sum(sample_sizes["by_type"].values())
    #         return 0.2 * total_audience_sample_size, f"20% of total sample size for distant districts: {total_audience_sample_size} * 20%\nCost updated to {distant_district_fee:.0f})", updated_element_cost

    #     # Check for "QC" term - original logic
    #     elif self._contains_term(element_cost_name, ["QC"]):# Find applicable QC methods with team = "QC"
    #         applicable_methods = []
    #         for qc_method in self.qc_methods:
    #             if qc_method["team"] == "QC" and self._contains_term(element_cost_name, [qc_method["method"]]):
    #                 applicable_methods.append(qc_method)
            
    #         # Calculate combined rate from applicable methods
    #         combined_rate = sum(method["rate"] / 100 for method in applicable_methods)
            
    #         # Calculate coefficient
    #         coefficient = total_sample_size * combined_rate
            
    #         # Build formula
    #         if applicable_methods:
    #             method_details = []
    #             for method in applicable_methods:
    #                 method_details.append(f"  - {method['method']}: {method['rate']}%")
                
    #             formula = f"Tổng sample size * Combined QC rate:\n{total_sample_size} * {combined_rate:.4f} = {coefficient:.1f}\n\nQC Methods applied:\n" + "\n".join(method_details)
    #         else:
    #             formula = f"No applicable QC methods found with team 'QC' in element cost: {element_cost_name}"
    #             coefficient = 0
            
    #         return coefficient, formula, updated_element_cost
        
    #     # Check for "quản lý" term
    #     if self._contains_term(element_cost_name, ["quản lý"]):
    #         if project_type == "CLT":
    #             coefficient = total_excluding_pilot / 50 + 1
    #             return coefficient, f"Chi phí SUP QC CLT: Tổng sample size (không tính Pilot) / 50 + 1 = {total_sample_size} / 50 + 1 = {coefficient:.1f}", updated_element_cost
    #         elif project_type == "F2F/D2D":
    #             coefficient = total_sample_size / 100
    #             return coefficient, f"Chi phí SUP QC F2F/D2D: Qty = Tổng sample / 100 = {coefficient}", updated_element_cost

    #     # Check for "kiểm tra contact sheet" term
    #     if self._contains_term(element_cost_name, ["kiểm tra contact sheet"]):
    #         coefficient = total_sample_size / 2 / 10
    #         return coefficient, f"Tổng sample size / 2 / 10: {total_sample_size} / 2 / 10 = {coefficient:.1f}", updated_element_cost
        
    #     # Check for "hỗ trợ xăng" term
    #     if self._contains_term(element_cost_name, ["hỗ trợ xăng"]):
    #         return total_sample_size, f"Tổng sample size: {total_sample_size}", updated_element_cost
        
    #     # Default
    #     return 1, "Default QC Qty: 1", updated_element_cost

    # def _calculate_dp_coefficient(self, province, audience, element_cost_name, unit, sample_sizes, base_element_cost):
    #     """
    #     Calculate coefficient for DP category.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         unit (str): Element unit
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation)
    #     """
    #     # Get total sample size
    #     total_sample_size = sample_sizes["total"]

    #     # Default to no cost update
    #     updated_element_cost = base_element_cost

    #     # Check if there are custom DP Coding costs and update unit price
    #     if self.has_custom_dp_coding_cost() and self._contains_term(element_cost_name, ["coding"]):
    #         # Get custom DP coding unit price and use it instead of base cost
    #         custom_unit_price = self.get_custom_dp_coding_unit_price()
    #         if custom_unit_price is not None:
    #             updated_element_cost = custom_unit_price
    #         # Continue with normal coefficient calculation using the custom unit price
        
    #     # Get total sample size excluding Pilot
    #     total_excluding_pilot = total_sample_size
    #     if "Pilot" in sample_sizes["by_type"]:
    #         total_excluding_pilot -= sample_sizes["by_type"].get("Pilot", 0)

    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     if project_type == "CLT" or project_type == "HUT":
    #         # Handle CLT-specific DP conditions
    #         if element_cost_name.endswith("Input"):
    #             # Chi phí Input
    #             interview_methods = self.general.get("interview_methods", [])
    #             if "PAPI" in interview_methods:
    #                 return total_excluding_pilot, f"Tổng sample size (không tính Pilot) with PAPI: {total_excluding_pilot}", updated_element_cost
    #             else:
    #                 return 0, "PAPI not in interview methods: Qty = 0", updated_element_cost

    #     # Proceed with standard calculation for non-CLT or unmatched CLT items

    #     # Get open-ended questions count
    #     open_ended_count = self.general.get("open_ended_count", 0)

    #     # Check for "quản lý" term
    #     if self._contains_term(element_cost_name, ["quản lý"]):
    #         # Complex logic for management coefficient
    #         if total_sample_size < 100:
    #             if open_ended_count <= 5 and open_ended_count > 0:
    #                 return 1, "Tổng sample size < 100: Qty = 1", updated_element_cost
    #             else:
    #                 return 0, f"0% Qty for Số câu hỏi mở > 5 or = 0: {open_ended_count}", updated_element_cost
    #         elif total_sample_size <= 200:
    #             if open_ended_count <= 2 and open_ended_count > 0:
    #                 return 1, "Tổng sample size <= 200 and Số câu hỏi mở <= 2: Qty = 1", updated_element_cost
    #             elif open_ended_count <= 5 and open_ended_count >= 3:
    #                 coefficient = total_sample_size / 100
    #                 return coefficient, f"Tổng sample size / 100: {total_sample_size} / 100 = {coefficient:.1f}", updated_element_cost
    #             else:
    #                 coefficient = 0
    #                 return coefficient, f"0% Qty for Số câu hỏi mở > 5 or = 0: {open_ended_count}", updated_element_cost
    #         else:  # total_sample_size > 200
    #             if open_ended_count <= 2 and open_ended_count > 0:
    #                 coefficient = total_sample_size / 200
    #                 return coefficient, f"Tổng sample size / 200: {total_sample_size} / 200 = {coefficient:.1f}", updated_element_cost
    #             elif open_ended_count <= 5 and open_ended_count >= 3:
    #                 coefficient = total_sample_size / 150
    #                 return coefficient, f"Tổng sample size / 150: {total_sample_size} / 150 = {coefficient:.1f}", updated_element_cost
    #             elif open_ended_count <= 8 and open_ended_count >= 6:
    #                 coefficient = total_sample_size / 10
    #                 return coefficient, f"Tổng sample size / 10: {total_sample_size} / 10 = {coefficient:.1f}", updated_element_cost
    #             else:
    #                 coefficient = 0
    #                 return coefficient, f"0% Qty for Số câu hỏi mở > 8 or = 0: {open_ended_count}", updated_element_cost

    #     # Check for "QC" term
    #     if self._contains_term(element_cost_name, ["QC"]):
    #         # Find applicable QC methods with team = "DP"
    #         applicable_methods = []
    #         for qc_method in self.qc_methods:
    #             if qc_method["team"] == "DP" and self._contains_term(element_cost_name, [qc_method["method"]]):
    #                 applicable_methods.append(qc_method)
            
    #         # Calculate combined rate from applicable methods
    #         combined_rate = sum(method["rate"] / 100 for method in applicable_methods)
            
    #         # Calculate coefficient
    #         coefficient = total_sample_size * combined_rate
            
    #         # Build formula
    #         if applicable_methods:
    #             method_details = []
    #             for method in applicable_methods:
    #                 method_details.append(f"  - {method['method']}: {method['rate']}%")
                
    #             formula = f"Tổng sample size * Combined DP QC rate:\n{total_sample_size} * {combined_rate:.4f} = {coefficient:.1f}\n\nDP QC Methods applied:\n" + "\n".join(method_details)
    #         else:
    #             formula = f"No applicable QC methods found with team 'DP' in element cost: {element_cost_name}"
    #             coefficient = 0
            
    #         return coefficient, formula, updated_element_cost

    #     # Check unit type
    #     if unit.lower() == "phiếu":
    #         # Same as INTERVIEWER
    #         return self._calculate_interviewer_coefficient(province, audience, element_cost_name, sample_sizes, base_element_cost)
        
    #     # Check if unit is "câu"
    #     if unit.lower() == "câu":
    #         coefficient = total_excluding_pilot * (open_ended_count + 2)
    #         formula = f"Tổng sample Main, Boosters * (Open-ended questions + 2):\n{total_excluding_pilot} * ({open_ended_count} + 2) = {coefficient}"
    #         return coefficient, formula, updated_element_cost
        
    #     # Default
    #     return 1, "Default DP Qty: 1", updated_element_cost

    # def _calculate_incentive_coefficient(self, province, audience, element_cost_name, sample_sizes):
    #     """
    #     Calculate coefficient for INCENTIVE category.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation)
    #     """
    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     if project_type == "CLT" or project_type == "HUT":
    #         # Get total sample size excluding Pilot
    #         total_sample_size = sample_sizes["total"]
    #         total_excluding_pilot = total_sample_size
    #         if "Pilot" in sample_sizes["by_type"]:
    #             total_excluding_pilot -= sample_sizes["by_type"]["Pilot"]
            
    #         # Handle CLT-specific INCENTIVE conditions
    #         if self._contains_term(element_cost_name, ["PV chính thức"]):
    #             qty = sample_sizes["by_type"].get("Main", 0) + sample_sizes["by_type"].get("Extra for Main", 0) 
    #             return qty, f"Tổng phiếu Main + Extra Main: {qty}"
            
    #         elif self._contains_term(element_cost_name, ["PV pilot"]):
    #             qty = sample_sizes["by_type"].get("Pilot", 0)
    #             return qty, f"Tổng phiếu Pilot: {qty}"

    #         elif self._contains_term(element_cost_name, ["IDI"]):
    #             # Chi phí IDI
    #             clt_sample_recruit_idi = self.general.get("clt_sample_recruit_idi", 0)
    #             return clt_sample_recruit_idi, f"Sample recruit IDI count: {clt_sample_recruit_idi}"
                
    #         elif self._contains_term(element_cost_name, ["PV Booster", "Boosters"]):
    #             # Quà phiếu PV boosters
    #             qty = sample_sizes["by_type"].get("Boosters", 0) + sample_sizes["by_type"].get("Extra for Boosters", 0)
    #             return qty, f"Tổng phiếu Boosters + Extra Boosters: {qty}"

    #     # Proceed with standard calculation for non-CLT or unmatched CLT items

    #     # Check for specific sample types in element cost name
    #     for sample_type in SAMPLE_TYPES:
    #         if self._contains_term(element_cost_name, [sample_type]):
    #             sample_size = sample_sizes["by_type"].get(sample_type, 0)
    #             return sample_size, f"Sample size phiếu {sample_type}: {sample_size}"
        
    #     # Default
    #     return 1, "Default incentive Qty: 1"

    # def _calculate_communication_coefficient(self, element_data, sample_sizes):
    #     """
    #     Calculate coefficient for COMMUNICATION category.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_data (dict): Element data including subtitle hierarchy, unit, etc.
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation)
    #     """
    #     # Get total sample size
    #     total_sample_size = sample_sizes["total"]

    #     # Get total sample size excluding Pilot
    #     total_excluding_pilot = total_sample_size
    #     if "Pilot" in sample_sizes["by_type"]:
    #         total_excluding_pilot = total_sample_size - sample_sizes["by_type"]["Pilot"]
        
    #     # Get element cost name and subtitles
    #     element_cost_name = element_data.get("element_cost_name", "")
    #     subtitles = element_data.get("subtitles", [])
        
    #     # Check for "cước điện thoại cố định" term
    #     if self._contains_term(element_cost_name, ["cước điện thoại cố định"]):
    #         # Get project type and check if it's CATI
    #         project_type = self.general.get("project_type", "")
            
    #         # Get second subtitle (if available) to determine if it's FW or QC
    #         second_subtitle = subtitles[1] if len(subtitles) > 1 else ""
            
    #         if project_type == "CATI":
    #             # For CATI projects, always use total sample size for both FW and QC
    #             return total_sample_size, f"CATI project type: Total sample size = {total_sample_size}"
    #         else:
    #             coefficient = round(total_excluding_pilot * 0.75, 1)
    #             formula = f"Tổng sample (không tính Pilot) * 75% = {total_excluding_pilot} * 0.75 = {coefficient}"
    #             return coefficient, formula
        
    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     subtitles = element_data.get("subtitles", [])
    #     if project_type == "CLT":
    #         if self._contains_term(element_cost_name, ["card điện thoại"]):
    #             if subtitles[1] == "FW":
    #                 coefficient = round(total_excluding_pilot / 75, 1)
    #                 formula = f"Tổng sample (không tính Pilot) / 75 = {total_excluding_pilot} / 75 = {coefficient}"
    #                 return coefficient, formula
    #             elif subtitles[1] == "QC":
    #                 coefficient = round(total_excluding_pilot / 150, 1)
    #                 formula = f"Tổng sample (không tính Pilot) / 150 = {total_excluding_pilot} / 150 = {coefficient}"
    #                 return coefficient, formula
        
    #     # Default
    #     return 1, "Default COMMUNICATION Qty: 1"

    # def _calculate_other_coefficient(self, province, audience, element_data, sample_sizes):
    #     """
    #     Calculate coefficient for OTHER category.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         sample_sizes (dict): Dictionary with sample sizes by sample type and total
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation)
    #     """
    #     # Get total sample size
    #     total_sample_size = sample_sizes["total"]
        
    #     # Get element cost name and subtitles
    #     element_cost_name = element_data.get("element_cost_name", "")
    #     subtitles = element_data.get("subtitles", [])
        
    #     # Get clt_sample_size_per_day from General Tab
    #     clt_sample_size_per_day = self.general.get("clt_sample_size_per_day", 1)
        
    #     # Check if this is a CLT project
    #     project_type = self.general.get("project_type", "")
    #     if project_type == "CLT" or project_type == "HUT":
    #         # Get total sample size excluding Pilot
    #         total_excluding_pilot = total_sample_size
    #         if "Pilot" in sample_sizes["by_type"]:
    #             total_excluding_pilot -= sample_sizes["by_type"]["Pilot"]
            
    #         # Handle CLT-specific OTHER conditions
    #         if self._contains_term(element_cost_name, ["Tiền vận chuyển"]):
    #             return 2, "Vận chuyển: Qty = 2"

    #         elif self._contains_term(element_cost_name, ["Tiền thuê location", "Tiền thuê tủ lạnh", "Tiền thuê TV", "Tiền thuê partition"]):
    #             coefficient = round(total_excluding_pilot / clt_sample_size_per_day, 1)
    #             formula = f"Tổng sample size (không tính Pilot) / Target ngày: {total_excluding_pilot} / {clt_sample_size_per_day} = {coefficient}"
    #             return coefficient, formula
            
    #         elif self._contains_term(element_cost_name, ["Tiền set-up location"]):
    #             return 2, "Set-up location: Qty = 2"
            
    #         elif self._contains_term(element_cost_name, ["Tiền nước uống, khăn giấy, bánh lạt", "ifield"]):
    #             return total_excluding_pilot, f"Qty = Tổng sample size (không tính Pilot) = {total_excluding_pilot}"
            
    #         elif self._contains_term(
    #             element_cost_name, 
    #             ["Tiền cleaner", 
    #              "Tiền hủy sản phẩm mẫu",
    #              "Tiền giặt khăn trải bàn",
    #              "Tiền mua đá ướp sản phẩm",
    #              "Tiền mua các vật dụng khác"
    #             ]
    #         ):
    #             return 1, "Các chi phí còn lại trong OTHER mặc định là 1"

    #     # Proceed with standard calculation for non-CLT or unmatched CLT items
        
    #     # Check for "cước điện thoại cố định" term
    #     if self._contains_term(element_cost_name, ["cước điện thoại cố định"]):
    #         # Get project type and check if it's CATI
    #         project_type = self.general.get("project_type", "")
            
    #         # Get second subtitle (if available) to determine if it's FW or QC
    #         second_subtitle = subtitles[1] if len(subtitles) > 1 else ""
            
    #         if project_type == "CATI":
    #             # For CATI projects, always use total sample size for both FW and QC
    #             return total_sample_size, f"CATI project type: Tổng sample size = {total_sample_size}"
    #         else:
    #             # For non-CATI projects, check QC methods
    #             if self._contains_term(second_subtitle, ["FW"]):
    #                 # Look for "FW" team with "QC qua điện thoại" method
    #                 for qc_method in self.qc_methods:
    #                     if qc_method["team"] == "FW" and self._contains_term(qc_method["method"], ["QC qua điện thoại"]):
    #                         qc_rate = qc_method["rate"] / 100  # Convert percentage to decimal
    #                         coefficient = total_sample_size * qc_rate
    #                         return coefficient, f"FW with 'QC qua điện thoại': Tổng sample size * QC rate ({total_sample_size} * {qc_rate:.3f} = {coefficient:.2f})"
                    
    #                 # No matching QC method found
    #                 return 0, "No 'QC qua điện thoại' method found for FW team"
                    
    #             elif self._contains_term(second_subtitle, ["QC"]):
    #                 # Look for "QC" team with "QC qua điện thoại" method
    #                 for qc_method in self.qc_methods:
    #                     if qc_method["team"] == "QC" and self._contains_term(qc_method["method"], ["QC qua điện thoại"]):
    #                         qc_rate = qc_method["rate"] / 100  # Convert percentage to decimal
    #                         coefficient = total_sample_size * qc_rate
    #                         return coefficient, f"QC with 'QC qua điện thoại': Tổng sample size * QC rate ({total_sample_size} * {qc_rate:.3f} = {coefficient:.2f})"
                    
    #                 # No matching QC method found
    #                 return 0, "No 'QC qua điện thoại' method found for QC team"
        
    #     # Check for "ifield" term
    #     if self._contains_term(element_cost_name, ["ifield"]):
    #         # Check if platform is iField
    #         if self._contains_term(self.general.get("platform", ""), ["ifield"]):
    #             return total_sample_size, f"Tổng sample size (iField platform): {total_sample_size}"
    #         else:
    #             return 0, "Platform is not iField: Qty = 0"
        
    #     # Default
    #     return 1, "Default OTHER Qty: 1"

    # def _calculate_stationary_coefficient(
    #     self,
    #     element_cost_name,
    #     base_element_cost,
    #     element_data,
    #     sample_sizes,
    #     province=None
    # ):
    #     """
    #     Calculate coefficient for STATIONARY category with province-specific costs.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
    #         element_cost_name (str): Element cost name (subtitle 5)
    #         base_element_cost (float): Base element cost
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation, updated_element_cost)
    #     """
    #     # Use province if provided, otherwise get it from element_data
    #     if province is None and hasattr(element_data, 'get'):
    #         province = element_data.get("province", "Others")
        
    #     # Get province-specific stationary settings
    #     stationary_settings = self.settings.get("stationary", {})
    #     # Use specific province, fallback to "Others" if not found
    #     province_settings = stationary_settings.get(province, stationary_settings.get("Others", {}))

    #     # Default to no cost update
    #     updated_element_cost = base_element_cost
        
    #     # Get CLT-specific values from Genral Tab
    #     clt_provincial_desk_interviewers_count = self.general.get("clt_provincial_desk_interviewers_count", 0)

    #     # Get project_type        
    #     project_type = self.general.get("project_type", "")     
        
    #     # Get sample sizes from General Tab
    #     total_excluding_pilot = sample_sizes["total"] - sample_sizes["by_type"].get("Pilot", 0)

    #     if project_type == "CLT":
    #         # Check for "Photo trắng đen" term
    #         if self._contains_term(element_cost_name, ["Photo trắng đen"]):
    #             # Use the same quantity as Showcard
    #             bw_page_count = self.general.get("bw_page_count", 0)

    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee

    #             if self._contains_term(element_cost_name, ["FW"]):
    #                 # Calculate coefficient: total sample size * 1.3 * showcard count
    #                 coefficient = total_excluding_pilot * 1.3 * bw_page_count

    #                 # Formula explanation
    #                 formula = (
    #                     f"Tổng sample size (không tính pilot) * 130% * số trang photo trắng đen = {total_excluding_pilot} * 130% * {bw_page_count} = {coefficient}\n" +
    #                     f"(Cập nhật giá theo vùng: {bw_photo_fee:,.0f})"
    #                 )
    #             else:
    #                 coefficient = total_excluding_pilot * 3

    #                 # Formula explanation
    #                 formula = (
    #                     f"Tổng sample size (không tính pilot) * 3 = {total_excluding_pilot} * 3 = {coefficient}\n" +
    #                     f"(Cập nhật giá theo vùng: {bw_photo_fee:,.0f})"
    #                 )

    #             return coefficient, formula, updated_element_cost

    #         # Check for "showphoto" term
    #         elif self._contains_term(element_cost_name, ["showphoto"]):
    #             # Get showphoto page count from general tab
    #             showphoto_page_count = self.general.get("showphoto_page_count", 0)

    #             # Calculate coefficient: clt_provincial_desk_interviewers_count * showphoto_page_count
    #             coefficient = clt_provincial_desk_interviewers_count * showphoto_page_count
                
    #             # Update element cost to showphoto fee from settings
    #             showphoto_fee = province_settings.get("showphoto_fee", 250)
    #             updated_element_cost = showphoto_fee

    #             # Formula explanation
    #             formula = (
    #                 f"Số PVV ngồi bàn * Số trang SHOWPHOTO: {clt_provincial_desk_interviewers_count} * {showphoto_page_count} = {coefficient}\n" +
    #                 f"Cập nhật giá theo vùng: {showphoto_fee:,.0f}"
    #             )
                
    #             return coefficient, formula, updated_element_cost

    #         # Check for "Hồ sơ biểu mẫu" term
    #         elif self._contains_term(element_cost_name, ["Hồ sơ biểu mẫu"]):
    #             # Coefficient = total sample size
    #             coefficient = total_excluding_pilot
    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             # Formula explanation
    #             formula = (
    #                 f"Tổng sample size (không tính pilot): {total_excluding_pilot}\n" +
    #                 f"(Cập nhật giá theo vùng: {bw_photo_fee:,.0f})"
    #             )

    #             return coefficient, formula, updated_element_cost

    #         # Check for "Showcard" term
    #         elif self._contains_term(element_cost_name, ["Showcard"]):
    #             # Get showcard page count from general tab
    #             showcard_count = self.general.get("showcard_page_count", 0)
    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             # Formula explanation
    #             formula = (
    #                 f"Số cuốn: {showcard_count}\n" +
    #                 f"Cập nhật giá theo vùng: {bw_photo_fee:,.0f}"
    #             )
                
    #             return showcard_count, formula, updated_element_cost

    #         # Check for "decal" term
    #         elif self._contains_term(element_cost_name, ["decal"]):
    #             # Get decal page count from general tab
    #             decal_count = self.general.get("decal_page_count", 5)

    #             # Calculate coefficient: total_excluding_pilot / decal_count
    #             coefficient = total_excluding_pilot / decal_count if decal_count else 0
                
    #             # Update element cost to decal photo fee from settings
    #             decal_fee = province_settings.get("decal_fee", 250)
    #             updated_element_cost = decal_fee

    #             # Formula explanation
    #             formula = (
    #                 f"Tổng sample / Số decal dán mẫu: {total_excluding_pilot} / {decal_count} = {coefficient}\n" +
    #                 f"Cập nhật giá theo vùng: {decal_fee:,.0f}"
    #             )
                
    #             return coefficient, formula, updated_element_cost

    #         # Check for "In màu" term
    #         elif self._contains_term(element_cost_name, ["In màu"]):
    #             # Get color page count from general tab
    #             color_count = self.general.get("color_page_count", 0)

    #             # Calculate coefficient: clt_provincial_desk_interviewers_count * color count
    #             coefficient = clt_provincial_desk_interviewers_count * color_count

    #             # Update element cost to color photo fee from settings
    #             color_photo_fee = province_settings.get("color_photo_fee", 5000)
    #             updated_element_cost = color_photo_fee

    #             # Formula explanation
    #             formula = (
    #                 f"Số PVV ngồi bàn * Số trang in màu: {clt_provincial_desk_interviewers_count} * {color_count} = {coefficient}\n" +
    #                 f"(Cập nhật giá theo vùng: {color_photo_fee:,.0f})"
    #             )
                
    #             return coefficient, formula, updated_element_cost
            
    #         # Check for "Ép Plastic" term
    #         elif self._contains_term(element_cost_name, ["Ép Plastic"]):
    #             # Get color page count from general tab
    #             color_count = self.general.get("color_page_count", 0)

    #             # Calculate coefficient: clt_provincial_desk_interviewers_count * color count
    #             coefficient = clt_provincial_desk_interviewers_count * color_count

    #             # Update element cost to color photo fee from settings
    #             lamination_fee = province_settings.get("lamination_fee", 5000)
    #             updated_element_cost = lamination_fee

    #             # Formula explanation
    #             formula = (
    #                 f"Số PVV ngồi bàn * Số trang in màu: {clt_provincial_desk_interviewers_count} * {color_count} = {coefficient}\n" +
    #                 f"(Cập nhật giá theo vùng: {lamination_fee:,.0f})"
    #             )

    #             return coefficient, formula, updated_element_cost

    #         # Check for "Dropcard" term
    #         elif self._contains_term(element_cost_name, ["Dropcard"]):
    #             # Get dropcard page count from general tab
    #             dropcard_count = self.general.get("dropcard_page_count", 0)

    #             # Calculate coefficient: clt_provincial_desk_interviewers_count * dropcard count
    #             coefficient = clt_provincial_desk_interviewers_count * dropcard_count

    #             # Update element cost to dropcard fee from settings
    #             dropcard_fee = province_settings.get("dropcard_fee", 1000)
    #             updated_element_cost = dropcard_fee

    #             # Formula explanation
    #             formula = (
    #                  f"Số PVV ngồi bàn * Số trang dropcard: {clt_provincial_desk_interviewers_count} * {dropcard_count} = {coefficient}\n" +
    #                  f"(Cập nhật giá theo vùng: {dropcard_fee:,.0f})"
    #             )
    #             return coefficient, formula, updated_element_cost

    #     elif project_type == "F2F/D2D":
    #         # Check for "Showcard" term
    #         if self._contains_term(element_cost_name, ["Showcard"]):
    #             # Get showcard page count from general tab
    #             showcard_count = self.general.get("showcard_page_count", 0)
    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             return showcard_count, f"Showcard page count: {showcard_count} (Cost updated to {bw_photo_fee:,.0f})", updated_element_cost

    #         # Check for "Dropcard" term
    #         if self._contains_term(element_cost_name, ["Dropcard"]):
    #             # Get dropcard page count from general tab
    #             dropcard_count = self.general.get("dropcard_page_count", 0)
    #             # Calculate coefficient: 2 * dropcard count
    #             coefficient = dropcard_count
    #             # Update element cost to dropcard fee from settings
    #             dropcard_fee = province_settings.get("dropcard_fee", 1000)
    #             updated_element_cost = dropcard_fee
                
    #             return coefficient, f"2 * Dropcard page count: 2 * {dropcard_count} = {coefficient} (Cost updated to {dropcard_fee:,.0f})", updated_element_cost
            
    #         # Check for "In màu" term
    #         if self._contains_term(element_cost_name, ["In màu"]):
    #             # Get color page count from general tab
    #             color_count = self.general.get("color_page_count", 0)
    #             # Calculate coefficient: 2 * color count
    #             coefficient = color_count
    #             # Update element cost to color photo fee from settings
    #             color_photo_fee = province_settings.get("color_photo_fee", 5000)
    #             updated_element_cost = color_photo_fee
                
    #             return coefficient, f"2 * Color page count: 2 * {color_count} = {coefficient} (Cost updated to {color_photo_fee:,.0f})", updated_element_cost
            
    #         # Check for "Ép Plastic" term
    #         if self._contains_term(element_cost_name, ["Ép Plastic"]):
    #             # Get laminated page count from general tab
    #             laminated_count = self.general.get("laminated_page_count", 0)
    #             # Calculate coefficient: 2 * laminated count
    #             coefficient = laminated_count
    #             # Update element cost to lamination fee from settings
    #             lamination_fee = province_settings.get("lamination_fee", 4000)
    #             updated_element_cost = lamination_fee
                
    #             return coefficient, f"2 * Laminated page count: 2 * {laminated_count} = {coefficient} (Cost updated to {lamination_fee:,.0f})", updated_element_cost

    #         # Check for "Hồ sơ biểu mẫu" term
    #         if self._contains_term(element_cost_name, ["Hồ sơ biểu mẫu"]):
    #             # Fixed coefficient of 50
    #             coefficient = 50
    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             return coefficient, f"Fixed Qty: 50 (Cost updated to {bw_photo_fee:,.0f})", updated_element_cost
            
    #         # Check for "Photo trắng đen" term
    #         if self._contains_term(element_cost_name, ["Photo trắng đen"]):
    #             # Use the same quantity as Showcard
    #             showcard_count = self.general.get("showcard_page_count", 0)
    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             return showcard_count, f"Using Showcard page count: {showcard_count} (Cost updated to {bw_photo_fee:,.0f})", updated_element_cost
            
    #         # Check for "Photo Contact Sheet" term
    #         if self._contains_term(element_cost_name, ["Photo Contact Sheet"]):
    #             # Calculate coefficient: (total sample size / 20) * 15
    #             coefficient = (total_excluding_pilot / 20) * 15

    #             # Update element cost to black and white photo fee from settings
    #             bw_photo_fee = province_settings.get("bw_photo_fee", 250)
    #             updated_element_cost = bw_photo_fee
                
    #             formula = f"(Tổng sample size / 20) * 15 = ({total_excluding_pilot} / 20) * 15 = {coefficient:.0f}"
    #             return coefficient, f"{formula} (Cost updated to {bw_photo_fee:,.0f})", updated_element_cost

    #     # Default
    #     return 1, "Default STATIONARY Qty: 1", updated_element_cost

    # def _calculate_travel_coefficient(self, province, element_data, sample_sizes=None):
    #     """
    #     Calculate coefficient for TRAVEL category.
        
    #     Args:
    #         province (str): Province name
    #         element_data (dict): Element data including subtitles list and element_cost_name
    #         sample_sizes (dict): Dictionary containing sample size information
            
    #     Returns:
    #         tuple: (coefficient, formula_explanation, updated_element_cost, element_cost_formula)
    #     """
    #     # Initialize default return values
    #     coefficient = 0
    #     formula = "Default travel coefficient (0.0)"
    #     updated_element_cost = element_data.get("base_element_cost", 0)
    #     element_cost_formula = ""
        
    #     # Early validation checks
    #     if province not in self.travel:
    #         return coefficient, formula, updated_element_cost, element_cost_formula
        
    #     subtitles = element_data.get("subtitles", [])
    #     if len(subtitles) < 2:
    #         return coefficient, formula, updated_element_cost, element_cost_formula
        
    #     # Extract common variables
    #     element_cost_name = subtitles[-1] if subtitles else ""
    #     project_type = self.general.get("project_type", "")
        
    #     # Calculate total sample size excluding pilot
    #     total_excluding_pilot = sample_sizes.get("total", 0) - sample_sizes["by_type"].get("Pilot", 0)

    #     # Get CLT sample size per day
    #     clt_sample_size_per_day = self.general.get("clt_sample_size_per_day", 0.001)
        
    #     # Determine travel type from subtitle
    #     travel_type = subtitles[1] if len(subtitles) > 1 else ""
        
    #     # Handle TRAVEL FULLTIME
    #     if self._contains_term(travel_type, ["TRAVEL FULLTIME"]):
    #         return self._calculate_fulltime_travel(
    #             province, element_cost_name, subtitles, updated_element_cost, element_cost_formula
    #         )
        
    #     # Handle TRAVEL PARTTIME
    #     elif self._contains_term(travel_type, ["TRAVEL PARTTIME"]):
    #         return self._calculate_parttime_travel(
    #             province, subtitles, element_cost_name, project_type,
    #             total_excluding_pilot, clt_sample_size_per_day,
    #             updated_element_cost, element_cost_formula
    #         )
            
    #     return coefficient, formula, updated_element_cost, element_cost_formula

    # def _calculate_fulltime_travel(self, province, element_cost_name, subtitles, updated_element_cost, element_cost_formula):
    #     """Calculate coefficients for fulltime travel."""
    #     # Get fulltime data for this province
    #     fulltime_data = self.travel[province].get("fulltime", {})
        
    #     # Get the assigned people count and travel days
    #     fulltime_quantity = len(fulltime_data.get("assigned_people", []))
    #     fulltime_travel_days = fulltime_data.get("travel_days", 0)

    #     # Get transportation type selection (default to "tàu/xe" if not set)
    #     transportation_type = fulltime_data.get("transportation_type", "tàu/xe")

    #     # Check for "brief" term - always Qty = 1
    #     if self._contains_term(element_cost_name, ["brief"]):
    #         return 1, "Brief cost: Qty = 1 (fixed)", updated_element_cost, element_cost_formula

    #     # Check for "hà nội" term - province-specific logic
    #     if self._contains_term(element_cost_name, ["hà nội"]):
    #         if province == "Hà Nội":
    #             coefficient = fulltime_quantity
    #             formula = f"Hà Nội specific cost: Qty = số người = {fulltime_quantity}"
    #         else:
    #             coefficient = 0
    #             formula = f"Hà Nội specific cost: Province is {province} (not Hà Nội), Qty = 0"
    #         return coefficient, formula, updated_element_cost, element_cost_formula
        
    #     # Check if this is a hotel or food cost for fulltime travel
    #     if self._contains_term(element_cost_name, ["Khách sạn", "ăn uống"]):
    #         # Calculate costs by level and return multiple elements
    #         return self._calculate_travel_cost_by_level(province, element_cost_name, subtitles)
        
    #     # Initialize coefficient and formula
    #     coefficient = 0
    #     formula = ""
        
    #     # Get province-specific transportation costs if available
    #     transportation_settings = self.settings.get("transportation", {})
        
    #     # Check if this is a flight cost
    #     if self._contains_term(element_cost_name, ["máy bay"]):
    #         # Check if user selected "máy bay" transportation
    #         if transportation_type == "máy bay":
    #             # Use province-specific flight cost if available
    #             if province in transportation_settings:
    #                 updated_element_cost = transportation_settings[province].get("flight", 0)
    #                 element_cost_formula = f"Province-specific flight cost for {province}: {updated_element_cost:,.0f} VND"
    #             elif "Others" in transportation_settings:
    #                 updated_element_cost = transportation_settings["Others"].get("flight", 0)
    #                 element_cost_formula = f"Default flight cost (Others): {updated_element_cost:,.0f} VND"
    #         else:
    #             # User selected "tàu/xe", so flight cost should be 0
    #             updated_element_cost = 0
    #             element_cost_formula = f"Flight cost set to 0 because transportation type is '{transportation_type}'"
                
    #     elif self._contains_term(element_cost_name, ["xe", "tàu"]):
    #         # Check if user selected "tàu/xe" transportation
    #         if transportation_type == "tàu/xe":
    #             # Use province-specific train cost if available
    #             if province in transportation_settings:
    #                 updated_element_cost = transportation_settings[province].get("train", 400000)
    #                 element_cost_formula = f"Province-specific train cost for {province}: {updated_element_cost:,.0f} VND"
    #             elif "Others" in transportation_settings:
    #                 updated_element_cost = transportation_settings["Others"].get("train", 400000)
    #                 element_cost_formula = f"Default train cost (Others): {updated_element_cost:,.0f} VND"
    #         else:
    #             # User selected "máy bay", so train/car cost should be 0
    #             updated_element_cost = 0
    #             element_cost_formula = f"Train/car cost set to 0 because transportation type is '{transportation_type}'"
        
    #     # Define rules for different cost types
    #     cost_rules = {
    #         "transportation": {
    #             "terms": ["máy bay", "xe", "tàu"],
    #             "coefficient_calc": lambda qty, days: qty * 2,
    #             "formula_template": "Qty = Số người * 2 lượt = {qty} * 2 = {coef}"
    #         },
    #         "taxi": {
    #             "terms": ["Taxi từ nhà ra sân bay, về nhà"],
    #             "coefficient_calc": lambda qty, days: qty * 4,
    #             "formula_template": "Qty = Số người * 4 lượt = {qty} * 4 = {coef}"
    #         },
    #         "local_transport": {
    #             "terms": ["Chi phí đi lại tại nơi công tác"],
    #             "coefficient_calc": lambda qty, days: qty * days,
    #             "formula_template": "Số người * Số ngày travel = {qty} * {days} = {coef}"
    #         },
    #         "default": {
    #             "terms": [],  # Default case
    #             "coefficient_calc": lambda qty, days: qty,
    #             "formula_template": "Qty = số người = {coef}"
    #         }
    #     }
        
    #     # Find matching rule
    #     rule = None
    #     for rule_key, rule_data in cost_rules.items():
    #         if not rule_data["terms"] or self._contains_term(element_cost_name, rule_data["terms"]):
    #             rule = rule_data
    #             break
        
    #     # Apply the rule
    #     coefficient = rule["coefficient_calc"](fulltime_quantity, fulltime_travel_days)
    #     formula = rule["formula_template"].format(
    #         qty=fulltime_quantity, 
    #         days=fulltime_travel_days, 
    #         coef=coefficient
    #     )
        
    #     return coefficient, formula, updated_element_cost, element_cost_formula

    # def _calculate_parttime_travel(self, province, subtitles, element_cost_name, project_type,
    #                             total_excluding_pilot, clt_sample_size_per_day,
    #                             updated_element_cost, element_cost_formula):
    #     """Calculate coefficients for parttime travel."""
    #     # Get parttime data for this province
    #     parttime_data = self.travel[province].get("parttime", {})
        
    #     # Initialize return values
    #     coefficient = 0
    #     formula = ""
        
    #     # Determine district type (distant or nearby)
    #     district_type = None
    #     if len(subtitles) > 2:
    #         if self._contains_term(subtitles[2], ["HUYỆN XA"]):
    #             district_type = "distant"
    #         elif self._contains_term(subtitles[2], ["HUYỆN GẦN"]):
    #             district_type = "nearby"
        
    #     if not district_type:
    #         return coefficient, formula, updated_element_cost, element_cost_formula
        
    #     # Determine role (supervisor, interviewer, qc)
    #     role = None
    #     if len(subtitles) > 3:
    #         if self._contains_term(subtitles[3], ["SUPERVISOR"]):
    #             role = "supervisor"
    #         elif self._contains_term(subtitles[3], ["INTERVIEWER"]):
    #             role = "interviewer"
    #         elif self._contains_term(subtitles[3], ["QC"]):
    #             role = "qc"
        
    #     if not role:
    #         return coefficient, formula, updated_element_cost, element_cost_formula
            
    #     # Handle CLT projects with RECRUIT/NGOI_BAN distinction for supervisor/interviewer
    #     # and special QC calculation
    #     if project_type == "CLT" and len(subtitles) > 4:
    #         if role in ["supervisor", "interviewer"]:
    #             return self._calculate_clt_parttime_travel(
    #                 parttime_data, role, district_type, subtitles, element_cost_name,
    #                 total_excluding_pilot, clt_sample_size_per_day,
    #                 updated_element_cost, element_cost_formula
    #             )
    #         elif role == "qc":
    #             # Special handling for QC in CLT projects
    #             return self._calculate_clt_qc_parttime_travel(
    #                 parttime_data, district_type, element_cost_name,
    #                 total_excluding_pilot, clt_sample_size_per_day,
    #                 updated_element_cost, element_cost_formula
    #             )
        
    #     # For non-CLT projects or without RECRUIT/NGOI_BAN distinction
    #     quantity = parttime_data.get(role, {}).get(district_type, 0)
    #     coefficient = quantity
    #     formula = f"{district_type.capitalize()} parttime {role} quantity: {quantity}"
        
    #     return coefficient, formula, updated_element_cost, element_cost_formula

    # def _calculate_clt_parttime_travel(self, parttime_data, role, district_type, subtitles, element_cost_name,
    #                                 total_excluding_pilot, clt_sample_size_per_day,
    #                                 updated_element_cost, element_cost_formula):
    #     """Calculate coefficients for CLT parttime travel with RECRUIT/NGOI_BAN distinction."""
    #     # Initialize return values
    #     coefficient = 0
    #     formula = ""
        
    #     # Determine sub-role: RECRUIT or NGOI_BAN
    #     sub_role = None
    #     if self._contains_term(subtitles[4], ["RECRUIT"]):
    #         sub_role = "recruit"
    #     elif self._contains_term(subtitles[4], ["NGỒI BÀN"]):
    #         sub_role = "ngoi_ban"
        
    #     if not sub_role:
    #         # Default for unrecognized sub-roles
    #         quantity = parttime_data.get(role, {}).get(district_type, 0)
    #         coefficient = quantity
    #         formula = f"{district_type.capitalize()} parttime {role} quantity: {quantity}"
    #         return coefficient, formula, updated_element_cost, element_cost_formula
        
    #     # Get the quantity for this role/sub-role combination
    #     quantity_key = f"{sub_role}_{district_type}"
    #     quantity = parttime_data.get(role, {}).get(quantity_key, 0)
        
    #     # Calculate coefficient based on cost type
    #     if self._contains_term(element_cost_name, ["xe", "tàu"]) and district_type == "distant":
    #         coefficient = quantity * 2
    #         formula = f"Số {role.capitalize()} {sub_role.capitalize()} * 2 lượt = {quantity} * 2 = {coefficient}"
        
    #     elif self._contains_term(element_cost_name, ["trợ cấp đi công tác"]):
    #         # Same formula for both distant and nearby districts
    #         days_formula = f"(Tổng sample / Target ngày) + 2 + 1"
    #         days_value = (total_excluding_pilot / clt_sample_size_per_day) + 2 + 1
            
    #         coefficient = days_value * quantity
    #         formula = (
    #             f"[{days_formula}] * Số {role.capitalize()} {sub_role.capitalize()} = "
    #             f"[{total_excluding_pilot} / {clt_sample_size_per_day} + 2 + 1] * {quantity} = {coefficient}"
    #         )
        
    #     else:
    #         # Default case
    #         coefficient = quantity
    #         formula = f"{district_type.capitalize()} parttime {role} {sub_role} quantity: {quantity}"
        
    #     return coefficient, formula, updated_element_cost, element_cost_formula

    # def _calculate_clt_qc_parttime_travel(
    #     self, parttime_data, district_type, element_cost_name,
    #     total_excluding_pilot, clt_sample_size_per_day,
    #     updated_element_cost, element_cost_formula
    # ):
    #     """
    #     Calculate coefficients for CLT QC parttime travel.
        
    #     Args:
    #         parttime_data: Parttime travel data for the province
    #         district_type: "distant" or "nearby"
    #         element_cost_name: Name of the cost element
    #         updated_element_cost: Current element cost
    #         element_cost_formula: Current element cost formula
            
    #     Returns:
    #         tuple: (coefficient, formula, updated_element_cost, element_cost_formula)
    #     """
    #     # Initialize return values
    #     coefficient = 0
    #     formula = ""
        
    #     # Get QC quantity for this district type
    #     quantity = parttime_data.get("qc", {}).get(district_type, 0)
        
    #     # Special calculation for transportation costs in distant districts
    #     if self._contains_term(element_cost_name, ["xe", "tàu"]) and district_type == "distant":
    #         # Get number of desk-based interviewers from general settings
    #         clt_provincial_desk_interviewers_count = self.general.get("clt_provincial_desk_interviewers_count", 0)
            
    #         coefficient = clt_provincial_desk_interviewers_count * 2
    #         formula = f"Số PVV ngồi bàn * 2 lượt = {clt_provincial_desk_interviewers_count} * 2 = {coefficient}"
        
    #     else:
    #         # Default case - use the QC quantity
    #         coefficient = round(
    #             ((total_excluding_pilot / clt_sample_size_per_day) + 1) * quantity, 
    #             2
    #         )
    #         days_formula = f"(Tổng sample / Target ngày) + 1"
    #         formula = (
    #             f"[{days_formula}] * Số QC {district_type.capitalize()} = "
    #             f"[{total_excluding_pilot} / {clt_sample_size_per_day} + 1] * {quantity} = {coefficient}"
    #         )

    #     return coefficient, formula, updated_element_cost, element_cost_formula

    # def _get_audience_growth_rate(self, province, audience):
    #     """
    #     Get the growth rate for a specific target audience in a province.
        
    #     Args:
    #         province (str): Province name
    #         audience (str): Target audience name
            
    #     Returns:
    #         float: Growth rate percentage (0-100)
    #     """
    #     # Default growth rate if not found
    #     default_growth_rate = 100
        
    #     # Look up growth rate in samples data
    #     # if province in self.samples and audience in self.samples[province]:
    #     #     # Use the first sample type's growth rate for simplicity
    #     #     # In a real implementation, we might want a more sophisticated approach
    #     #     sample_types = self.samples[province][audience]
    #     #     if sample_types:
    #     #         first_sample_type = next(iter(sample_types))
    #     #         return sample_types[first_sample_type].get("price_growth", default_growth_rate)
        
    #     return default_growth_rate

    # def _calculate_rollup_costs(self, hierarchy):
    #     """
    #     Calculate rollup costs for each level of the hierarchy.
        
    #     Args:
    #         hierarchy (dict): Hierarchical cost structure
    #     """
    #     for subtitle, data in hierarchy.items():
    #         # Reset cost to include only direct elements
    #         direct_cost = sum(element["total_cost"] for element in data["elements"])
            
    #         # Calculate costs for children recursively
    #         if data["children"]:
    #             self._calculate_rollup_costs(data["children"])
                
    #             # Add children costs to this level
    #             children_cost = sum(child_data["cost"] for child_data in data["children"].values())
    #             data["cost"] = direct_cost + children_cost
    #         else:
    #             data["cost"] = direct_cost

    # def _calculate_hierarchy_total(self, hierarchy):
    #     """
    #     Calculate the total cost for a hierarchy.
        
    #     Args:
    #         hierarchy (dict): Hierarchical cost structure
            
    #     Returns:
    #         float: Total cost for the hierarchy
    #     """
    #     total = 0
    #     for subtitle, data in hierarchy.items():
    #         total += data["cost"]
        
    #     return total

    # def _calculate_travel_cost_by_level(self, province, element_cost_name, subtitles):
    #     """
    #     Calculate travel costs by level for fulltime employees.
    #     Returns a list of elements, one for each level.
        
    #     Args:
    #         province (str): Province name
    #         element_cost_name (str): Element cost name
    #         subtitles (list): Subtitles list
            
    #     Returns:
    #         list: List of elements, each with (coefficient, formula, element_cost, element_cost_formula, level)
    #     """
    #     # Result list for multiple elements
    #     elements = []
        
    #     # Check if province exists in travel data
    #     if province not in self.travel:
    #         return elements
        
    #     # Get assigned people for this province
    #     assigned_people = self.travel[province].get("fulltime", {}).get("assigned_people", [])
        
    #     # If no assigned people, return empty list
    #     if not assigned_people:
    #         return elements
        
    #     # Get the levels for each assigned person
    #     assigned_levels = {}  # Use a dict to store level -> [email1, email2, ...]
    #     for email in assigned_people:
    #         # Find the person in assignments by email
    #         for person in self.assignments:
    #             if person.get("email") == email:
    #                 level = person.get("level")
    #                 if level not in assigned_levels:
    #                     assigned_levels[level] = []
    #                 assigned_levels[level].append(email)
    #                 break
        
    #     # Determine cost type
    #     cost_type = None
    #     if self._contains_term(element_cost_name, ["Khách sạn"]):
    #         cost_type = "hotel"
    #     elif self._contains_term(element_cost_name, ["ăn uống"]):
    #         cost_type = "food"
        
    #     if not cost_type:
    #         return elements
        
    #     # Travel days
    #     travel_days = self.travel[province].get("fulltime", {}).get("travel_days", 0)
    #     travel_nights = self.travel[province].get("fulltime", {}).get("travel_nights", 0)
        
    #     # Create an element for each level
    #     for level, emails in assigned_levels.items():
    #         # Get cost from settings
    #         setting_key = f"travel_{level.lower()}_{cost_type}"
    #         level_cost = self.settings.get(setting_key, DEFAULT_TRAVEL_COSTS.get(level, {}).get(cost_type, 0))
            
    #         # Element specific values
    #         person_count = len(emails)
    #         if cost_type == "hotel":
    #             # Calculate cost for hotel
    #             coefficient = travel_nights * person_count  # Nights * Number of people
                
    #             # Create formula
    #             formula = f"{level} {cost_type}: {travel_nights} nights * {person_count} people = {coefficient}"
    #             cost_formula = f"{level} {cost_type} cost: {level_cost:,.0f}"
    #         elif cost_type == "food":
    #             # Calculate cost for food
    #             coefficient = travel_days * person_count  # Days * Number of people
    #             # Create formula
    #             formula = f"{level} {cost_type}: {travel_days} days * {person_count} people = {coefficient}"
    #             cost_formula = f"{level} {cost_type} cost: {level_cost:,.0f}"
            
    #         # Add to result list with level info
    #         elements.append((coefficient, formula, level_cost, cost_formula, level))
        
    #     return elements

    # def calculate_estimated_costs(self, hierarchy, duration_minutes=10):
    #     def map_duration_to_label(duration_minutes: int) -> str:
    #         for label, (start, end) in DURATION_RANGES.items():
    #             if start <= duration_minutes <= end:
    #                 return label
    #         return None  # Không khớp

    #     def traverse_hierarchy(node, path=None):
    #         path = path or []
    #         if "elements" in node:
    #             for element in node["elements"]:
    #                 yield path, element
    #         if "children" in node:
    #             for key, child in node["children"].items():
    #                 yield from traverse_hierarchy(child, path + [key])

    #     results = []
    #     duration_label = map_duration_to_label(duration_minutes)

    #     for province, audiences in self.samples.items():
    #         for audience_key, audience_data in audiences.items():
    #             sample_size = audience_data.get("sample_size", 0)
    #             price_growth = audience_data.get("price_growth", 100.0)
    #             audience_name = audience_data.get("name", "")
    #             level = audience_data.get("level", "L1")

    #             for category_path, element in traverse_hierarchy(hierarchy['F2F/D2D']):
    #                 cost_dict = element.get("costs", {})
    #                 if level not in cost_dict:
    #                     continue
    #                 try:
    #                     base_cost = float(cost_dict[level].get(duration_label))
    #                 except (TypeError, ValueError):
    #                     continue

    #                 adjusted_cost = round(base_cost * price_growth / 100, 2)
    #                 total_cost = round(adjusted_cost * sample_size, 2)

    #                 results.append({
    #                     "province": province,
    #                     "audience": audience_name,
    #                     "category": " > ".join(category_path),
    #                     "element": element.get("description", ""),
    #                     "code": element.get("code", ""),
    #                     "unit": element.get("unit", ""),
    #                     "level": level,
    #                     "duration": duration_label,
    #                     "base_cost": base_cost,
    #                     "price_growth": price_growth,
    #                     "adjusted_cost": adjusted_cost,
    #                     "sample_size": sample_size,
    #                     "total_cost": total_cost
    #                 })

    #     return results

    # def update_stationary_settings(self, province, field, value):
    #     """
    #     Update a stationary setting for a specific province.
        
    #     Args:
    #         province (str): Province name
    #         field (str): Field name to update
    #         value: New value for the field
    #     """
    #     if "stationary" not in self.settings:
    #         self.settings["stationary"] = {}
            
    #     if province not in self.settings["stationary"]:
    #         self.settings["stationary"][province] = {}
            
    #     self.settings["stationary"][province][field] = value
    #     self.dataChanged.emit()
        
    #     # For backwards compatibility, also update the top-level setting
    #     # if the province is "Others"
    #     if province == "Others":
    #         if field in ["bw_photo_fee", "color_photo_fee", "lamination_fee", 
    #                     "dropcard_fee", "showphoto_fee", "decal_fee"]:
    #             self.settings[field] = value

    # def _get_aggregated_sample_sizes(self, province):
    #     """Get aggregated sample sizes across all target audiences for a province."""
    #     result = {
    #         "by_type": {},
    #         "total": 0,
    #         "daily_sup_targets": {},
    #         "total_daily_sup_target": 0,
    #         "interviewer_target": 2  # Default value, will be updated to average
    #     }
        
    #     # Track interviewer targets for averaging
    #     interviewer_targets = []
        
    #     # Combine sample sizes from all audiences
    #     if province in self.samples:
    #         for sample_entry_key, sample_entry_value in self.samples[province].items():
    #             sample_type = sample_entry_value.get("sample_type", "Unknown")
    #             sample_size = sample_entry_value.get("sample_size", 0)
    #             daily_sup_target = sample_entry_value.get("daily_sup_target", 0)
    #             interviewer_target = sample_entry_value.get("target_for_interviewers", 2)
                
    #             # Add to sample type total
    #             if sample_type not in result["by_type"]:
    #                 result["by_type"][sample_type] = 0
    #             result["by_type"][sample_type] += sample_size
                
    #             # Add to daily SUP target total
    #             if sample_type not in result["daily_sup_targets"]:
    #                 result["daily_sup_targets"][sample_type] = 0
    #             result["daily_sup_targets"][sample_type] += daily_sup_target
                
    #             # Add to overall totals
    #             result["total"] += sample_size
    #             result["total_daily_sup_target"] += daily_sup_target
                
    #             # Collect interviewer targets for averaging
    #             interviewer_targets.append(interviewer_target)
        
    #     # Calculate average interviewer target
    #     if interviewer_targets:
    #         result["interviewer_target"] = sum(interviewer_targets) / len(interviewer_targets)
        
    #     return result

    # def _get_average_growth_rate(self, province, target_audiences):
    #     """
    #     Get the average growth rate across all target audiences for a province.
        
    #     Args:
    #         province (str): Province name
    #         target_audiences (list): List of target audiences
            
    #     Returns:
    #         float: Average growth rate percentage
    #     """
    #     if not target_audiences:
    #         return 0.0
        
    #     total_growth_rate = 0.0
    #     count = 0
        
    #     for audience in target_audiences:
    #         growth_rate = self._get_audience_growth_rate(province, audience)
    #         total_growth_rate += growth_rate
    #         count += 1
        
    #     return total_growth_rate / count if count > 0 else 0.0

    # def _get_updated_base_cost_from_industries(self, base_cost, subtitle_5, audience):
    #     """Update base_cost from industries.json if conditions are met."""
    #     if not audience or not subtitle_5 or not hasattr(self, 'industries_data'):
    #         return base_cost
        
    #     # Parse audience identifier
    #     audience_components = self._parse_audience_identifier(audience)
    #     if not audience_components:
    #         return base_cost
        
    #     target_audience_name = audience_components['name']
        
    #     # Search industries.json for matching target audience
    #     for industry_category, industry_data in self.industries_data.items():
    #         for entry_id, entry_data in industry_data.items():
    #             if entry_data.get('target_audience') == target_audience_name:
    #                 updated_cost = self._map_subtitle_to_price(entry_data, subtitle_5)
    #                 if updated_cost is not None:
    #                     return updated_cost
        
    #     return base_cost

    # def _map_subtitle_to_price(self, target_audience_entry, subtitle_5):
    #     """Map subtitle_5 content to appropriate price key."""
    #     subtitle_5_lower = subtitle_5.lower()
        
    #     if self._contains_term(subtitle_5_lower, ["booster"]):
    #         return target_audience_entry.get("price_booster")
    #     elif self._contains_term(subtitle_5_lower, ["pilot"]):
    #         return target_audience_entry.get("price_pilot")
    #     elif self._contains_term(subtitle_5_lower, ["non"]):
    #         return target_audience_entry.get("price_non")
    #     elif self._contains_term(subtitle_5_lower, ["phiếu"]):
    #         return target_audience_entry.get("price")
        
    #     return None
