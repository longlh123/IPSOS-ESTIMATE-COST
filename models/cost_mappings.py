def get_cost_tablet_small(project, element):
    device_type = project.general.get('device_type', "").lower()
    tablet_duration = project.general.get('tablet_usage_duration', "<= 15 phút")
    return 5000 if tablet_duration == "<= 15 phút" else 8000

def get_cost_tablet_large(project, element):
    return element.get('costs', {}).get('L1', {}).get('< 30 phút', 0)

def get_cost_laptop(project, element):    
    return element.get('costs', {}).get('L1', {}).get('< 30 phút', 0)

def get_default_cost(project, element):
    return element.get('costs', {}).get('L1', {}).get('< 30 phút', 0)

def get_cost_parking_fee(project, element):
    return project.settings.get('parking_fee', 5000)

COST_MAPPINGS = {
    "default" : get_default_cost,
    "Chi phí thuê tablet < 9 inch" : get_cost_tablet_small,
    "Chi phí thuê tablet >= 9 inch" : get_cost_tablet_large,
    "Chi phí thuê laptop" : get_cost_laptop,
    "Chi phí gửi xe" : get_cost_parking_fee

}

def map_cost_for_element(project, element):
    description = element.get('description', "")

    for key, func in COST_MAPPINGS.items():
        if key == description:
            return func(project, element)
    return COST_MAPPINGS["default"](project, element)