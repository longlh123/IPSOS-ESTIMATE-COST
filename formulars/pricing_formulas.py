def calculate_sample_size(sample_size, extra_rate):
    """
    Tính sample_size + extra
    """
    sample_size_extra = round(sample_size * extra_rate / 100) 
    return sample_size + sample_size_extra

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

def has_custom_daily_sup_target(daily_sup_target, sample_size, target_for_interviewer, interviewers_per_supervisor):
    """Check if the daily supervisor target has been customized."""
    calculated_daily_sup_target = calculate_daily_sup_target(sample_size, target_for_interviewer, interviewers_per_supervisor)

    if abs(daily_sup_target - calculated_daily_sup_target) > 0.001:
        return True
    return False