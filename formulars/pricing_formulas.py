def calculate_sample_size(sample_size, extra_rate):
    sample_size = sample_size + round(sample_size * extra_rate / 100, 0)
    return sample_size

def calculate_total_of_sample_size(target_audience_data, excluding_items=list()):
    total = 0

    for key, target_audience in target_audience_data.items():
        if target_audience.get('sample_type') not in excluding_items:
            total += calculate_sample_size(target_audience.get('sample_size', 0), target_audience.get('extra_rate', 0))
    
    return total

def calculate_device_rental_costs(device_type, tablet_duration, base_element_cost):
    if device_type == "Tablet < 9 inch":
        cost = 5000 if tablet_duration == "<= 15 phút" else 8000
    else:
        cost = base_element_cost
    return cost

def calculate_daily_sup_target(sample_size, target_for_interviewer, interviewers_per_supervisor):
    """
    Calculate the daily supervisor target based on sample size, target for interviewers, and interviewers per supervisor.
    
    :param sample_size: Total number of interviews to be conducted
    :param target_for_interviewers: Target number of interviews per interviewer
    :param interviewers_per_supervisor: Number of interviewers supervised by one supervisor
    :return: Daily supervisor target
    """
    if target_for_interviewer > 0 and interviewers_per_supervisor > 0:
        return round(sample_size / target_for_interviewer / interviewers_per_supervisor, 2)
    return 0.0

def calculate_total_daily_sup_target(target_audience_data):
    total = 0.0

    for key, target_audience in target_audience_data.items():
        if target_audience.get('sample_type', '') in ["Main", "Booster"]:
            total += target_audience['target']['daily_sup_target']

    return round(total, 2)