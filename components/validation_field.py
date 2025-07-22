import re

class FieldValidator:
    def __init__(self):
        self.rules = {
            "internal_job": [
                {
                    "check": lambda v: bool(v.strip()),
                    "error": "Internal Job is required!"
                },
                {
                    "check": lambda v: re.match(r"^\d{4}-\d{3}$", v),
                    "error": "Internal Job must be in the format YYYY-XXX (e.g., 2023-001)"
                }
            ],
            "symphony": [
                {
                    "check": lambda v: bool(v.strip()),
                    "error": "Symphony is required!"
                },
                {
                    "check": lambda v: re.match(r"^\d{6,8}$", v),
                    "error": "Symphony must be in the format XXXXXXXX (e.g., 12345678)"
                }
            ],
            "project_name" : [
                {
                    "check": lambda v: bool(v.strip()),
                    "error": "Project Name is required!"
                }
            ],
            "project_type" : [
                {
                    "check" : lambda v: not (v == "-- Select --"),
                    "error" : "Please select a project type"
                }
            ],
            "sampling_method" : [
                {
                    "check" : lambda v: not (v == "-- Select --"),
                    "error" : "Please select a Sampling Method"
                }
            ],
            "type_of_quota_control" : [
                {
                    "check" : lambda v: not (v == "-- Select --"),
                    "error" : "Please select a Type of Quota Control."
                }
            ],
            "quota_description" : [
                {
                    "condition" : "Interlocked Quota",
                    "check" : lambda v: bool(len(v) > 0),
                    "error" : "Quota Description is required!"
                }
            ],
            "resp_classification" : [
                {
                    "check" : lambda v: not (v == "-- Select --"),
                    "error" : "Please select a respondent classification"
                }
            ],
            "open_ended_main_count": [
                {
                    "condition" : True,
                    "check" : lambda v: not (v == 0),
                    "error" : "Please enter a value greater than 0."
                }
            ],
            "open_ended_booster_count": [
                {
                    "condition" : True,
                    "check" : lambda v: not (v == 0),
                    "error" : "Please enter a value greater than 0."
                }
            ],
            "clt_concepts_per_respondent": [
                {
                    "condition": True,
                    "check": lambda v: not (v == 0),
                    "error": "Please enter a value greater than 0."
                }
            ]
        }

    def validate(self, field_name, value, condition=None):
        field_rules = self.rules.get(field_name, [])

        if field_name in ["quota_description", "open_ended_main_count", "open_ended_booster_count", "clt_concepts_per_respondent"]:
            for rule in field_rules:
                if condition and rule.get("condition") == condition:
                    if not rule["check"](value):
                        return False, rule["error"]
        else:
            for rule in field_rules:
                if not rule["check"](value):
                    return False, rule["error"]
        
        return True, ""

    def target_audience_validate(self, field_name, value, condition=None):
        rules = {
            "sample_type": [
                {
                    "check": lambda v: not (v == "-- Select --"),
                    "error": "Please select a sample type"
                }
            ],
            "industry_name": [
                {
                    "check": lambda v: not (v == "-- Select --"),
                    "error": "Please enter a industry."
                }
            ],
            "target_audience_name": [
                {
                    "check": lambda v: bool(v.strip()),
                    "error": "Please enter a target audience."
                }
            ]
        }

        field_rules = rules.get(field_name, [])

        for rule in field_rules:
            if not rule["check"](value):
                return False, rule["error"]
        
        return True, ""
