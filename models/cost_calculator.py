import json

class CostCalculator:
    def __init__(self, general, samples):
        self.general = general
        self.samples = samples

        self.hierarchy_data = {}

        self.load_cost_hierarchy()
    
    def load_cost_hierarchy(self):
        config_path = ""

        if "CLT" in self.general.get('interview_methods', []):
            config_path = "config/f2f_cost_hierarchy.json"

        with open(config_path, "r", encoding="utf-8") as file:
            self.hierarchy_data = json.load(file)
        