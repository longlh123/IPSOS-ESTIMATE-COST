import re
from formulars.pricing_formulas import (
    calculate_sample_size,
    calculate_total_of_sample_size,
    calculate_total_daily_sup_target
)

MAPPING_STATIONARY = {
    "Photo trắng đen" : "bw_page_count",
    "Showphoto" : "showphoto_page_count",
    "Showcard" : "showcard_page_count",
    "Dropcard" : "dropcard_page_count",
    "In màu \ In concept" : "color_page_count",
    "Decal" : "decal_page_count",
    "Ép Plastic" : "laminated_page_count",
    "Hồ sơ biểu mẫu" : "interview_form_package_count",
    "Chi phí đóng cuốn" : "stimulus_material_production_count"
}

def get_chi_phi_phieu_pv_title(type):
    if type == 'pilot':
        return "Chi phí Phiếu PV - Pilot"
    elif type == 'main':
        return "Chi phí Phiếu PV - Main"
    elif type == 'booster':
        return "Chi phí Phiếu PV - Booster"
    elif type == 'non':
        return "Chi phí Phiếu PV - None"
    elif type == 'recruit':
        return "Chi phí Phiếu PV - Recruit"
    elif type == 'location':
        return "Chi phí Phiếu PV - In Location"
    else:
        return None

def get_default_quanty(project, element, province, title=""):
    quanty = calculate_total_of_sample_size(project.samples[province])

def get_quaphieu_phongvan(project, element, province, title=""):
    description = element.get('description', '')

    audience_data = [
        (key, value)
        for key, value in project.samples[province].items()
        if re.match(pattern=rf"^Q.+PV\s-\s{value.get('sample_type')}$", string=description)
    ]

    quanty = calculate_total_of_sample_size(dict(audience_data))
    return quanty

def get_sample_size_by_sample_type(project, element, province, title=""):
    sample_size = 0
    description = element.get('description', "")

    for target_audience in project.samples[province].values():
        sample_type = target_audience.get('sample_type', "")

        if re.match(pattern=f'Quà Phiếu PV - {sample_type}', string=description):
            sample_size += calculate_sample_size(target_audience.get('sample_size', 0), target_audience.get('extra_rate', 0))

    return sample_size

def get_chiphithue_thietbi(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])

    if "INTERVIEWER" in title:
        return sample_size    

    if "QC" in title:
        clt_sample_size_per_day = project.clt_settings.get("clt_sample_size_per_day", 0)
        quanty = round(sample_size / clt_sample_size_per_day * 2, 2)
        return quanty
    
def get_quanty_parking_fee(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    return sample_size

def get_chiphi_tuyendapvien_idi(project, element, province, title=""):
    sample_recruit_idi = project.clt_settings.get('clt_sample_recruit_idi')
    return sample_recruit_idi

def get_failure_rate(project, element, province, title=""):
    failure_rate = project.clt_settings.get('clt_failure_rate', 0)
    sample_size = calculate_total_of_sample_size(project.samples[province])
    quanty = round(sample_size * failure_rate / 100, 1)
    return round(quanty, 2) 

def get_chiphi_ql_on_field(project, element, province, title=""):
    quanty = 1
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])

    if "SUPERVISOR/ ASSISTANT" in title:
        quanty = 1
    if "QC" in title:
        if project.general.get('project_type') == "CLT":
            quanty = sample_size / 50 + 1
        if project.general.get('project_type') == "F2F/D2D":
            quanty = sample_size / 100
    if "DP" in title:
        open_ended_count = project.general.get('open_ended_main_count', 0) + project.general.get('open_ended_booster_count', 0)

        if sample_size < 100:
            if open_ended_count > 0 and open_ended_count <= 5:
                quanty = 1
            else:
                quanty = 0
        elif sample_size <= 200:
            if open_ended_count > 0 and open_ended_count <= 2:
                quanty = 1
            elif open_ended_count >= 3 and open_ended_count <= 5:
                quanty = sample_size / 100
            else:
                quanty = 0
        else:
            if open_ended_count > 0 and open_ended_count <= 2:
                quanty = sample_size / 200
            elif open_ended_count >= 3 and open_ended_count <= 5:
                quanty = sample_size / 150
            elif open_ended_count >= 6 and open_ended_count <= 8:
                quanty = sample_size / 100
            else:
                quanty = 0

    return quanty
    
def get_chiphi_ql_recruit_on_field(project, element, province, title=""):
    """
    Chi phi quan ly - on field = 2 + daily_sup_target 
    """
    if "SUPERVISOR/ ASSISTANT" in title:
        daily_sup_target = calculate_total_daily_sup_target(project.samples.get(province, {}))
        quanty = round(daily_sup_target, 2) + 2
        return quanty
    if "QC" in title:
        sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
        quanty = round((sample_size / 50)) + 1
        return quanty

def get_chiphi_ql_ngoiban_on_field(project, element, province, title=""):
    """
    Chi phi quan ly ngoi ban - on field = 2 + (sample_size / sample_size_target_per_day)
    """
    quanty = 0.0

    for key, target_audience in project.samples[province].items():
        if target_audience.get('sample_type') not in ["Pilot", "Non"]:
            sample_size = calculate_sample_size(target_audience.get('sample_size', 0), target_audience.get('extra_rate', 0))
            daily_interview_target = target_audience['target']['daily_interview_target']

            quanty = round(sample_size / daily_interview_target, 2)
    
    return 2 + quanty

def get_chiphi_ql_idi(project, element, province, title=""):
    sample_recruit_idi = project.clt_settings.get('clt_sample_recruit_idi')
    return round(sample_recruit_idi / 15, 2)

def get_chiphi_qc_in_home(project, element, province, title=""):
    """
    Formular: Sample * 20%
    """
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    quanty = round(sample_size * 20 / 100, 2)
    return quanty

def get_chiphi_qc_in_location(project, element, province, title=""):
    """
    Formular: Sample / Daily Interview Target 
    """

    return 1

def get_chiphi_coding(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    number_of_openendeds = project.general.get('open_ended_main_count', 0) + project.general.get('open_ended_booster_count', 0)
    quanty = 0

    if sample_size < 100:
        if 1 <= number_of_openendeds <= 5:
            quanty = 1
        else:
            quanty = round(sample_size / 100, 0)
    elif 101 <= number_of_openendeds <= 200:
        if 1 <= number_of_openendeds <= 2:
            quanty = 1
        elif 3 <= number_of_openendeds <= 8:
            quanty = round(sample_size / 100, 0)
        else:
            quanty = round(sample_size / 100, 0)
    else:
        if 1 <= number_of_openendeds <= 2:
            quanty = round(sample_size / 200, 0)
        elif 3 <= number_of_openendeds <= 5:
            quanty = round(sample_size / 150, 0)
        elif 6 <= number_of_openendeds <= 8:
            quanty = round(sample_size / 100, 0)
        else:
            quanty = round(sample_size / 100, 0)

    return quanty

def get_chiphi_input(project, element, province, title=""):
    quanty = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot"])
    return quanty

def get_chiphi_hotrocleandata(project, element, province, title=""):
    quanty = 1
    return quanty

def get_chiphi_cuocdienthoaicodinh(project, element, province, title=""):
    project_type = project.general.get("project_type")
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])

    if project_type == "CATI":
        return sample_size
    else:
        return round(sample_size * 0.75, 2)

def get_chiphi_carddienthoai(project, element, province, title=""):
    project_type = project.general.get("project_type")
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    quanty = 0

    if project_type == "CLT":
        titles = title.split(' / ')

        if titles[len(titles) - 1] == "FW":
            quanty = round(sample_size / 75, 2)
        if titles[len(titles) - 1] == "QC":
            quanty = round(sample_size / 150, 2)

    return quanty

def get_photo_trangden(project, element, province, title=""):
    """
    Formular = sample_size * 130% * Số trang photo trắng đen
    """
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    bw_page_count = project.general.get('bw_page_count', 0)
    quanty = sample_size * 1.3 * bw_page_count
    return quanty

def get_show_photo(project, element, province, title=""):
    showphoto_page_count = project.general.get("showphoto_page_count", 0)
    clt_provincial_desk_interviewers_count = project.general.get("clt_provincial_desk_interviewers_count", 0)
    quanty = clt_provincial_desk_interviewers_count * showphoto_page_count
    return quanty

def get_show_card(project, element, province, title=""):
    showcard_page_count = project.general.get("showcard_page_count", 0)
    quanty = showcard_page_count
    return quanty

def get_drop_card(project, element, province, title=""):
    dropcard_page_count = project.general.get("dropcard_page_count", 0)
    clt_provincial_desk_interviewers_count = project.general.get("clt_provincial_desk_interviewers_count", 0)
    quanty = clt_provincial_desk_interviewers_count * dropcard_page_count
    return quanty

def get_inmau_inconcept(project, element, province, title=""):
    color_page_count = project.general.get("color_page_count", 0)
    clt_provincial_desk_interviewers_count = project.general.get("clt_provincial_desk_interviewers_count", 0)
    quanty = clt_provincial_desk_interviewers_count * color_page_count
    return quanty

def get_decal(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    decal_page_count = project.general.get("decal_page_count", 0)
    quanty = (sample_size / decal_page_count) if decal_page_count > 0 else 0
    return quanty

def get_ep_flastic(project, element, province, title=""):
    laminated_page_count = project.general.get('laminated_page_count', 0)
    clt_provincial_desk_interviewers_count = project.general.get("clt_provincial_desk_interviewers_count", 0)
    quanty = clt_provincial_desk_interviewers_count * laminated_page_count
    return quanty

def get_hosobieumau(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    quanty = sample_size
    return quanty

def get_chiphidongcuon(project, element, province, title=""):
    stimulus_material_production_count = project.general.get('stimulus_material_production_count', 0)
    quanty = stimulus_material_production_count
    return quanty

def get_sample_recruit_idi(project, element, province, title=""):
    return project.clt_settings.get('clt_sample_recruit_idi', 0)

def get_chiphi_assistant_set_up(project, element, province, title=""):
    return project.clt_settings.get('clt_assistant_setup_days', 1)

def get_chiphi_assistant_on_field(project, element, province, title=""):
    """
    Chi phí Assistant - On-field = round(sample_size / daily_interview_target, 2)
    """
    quanty = 0.0

    for key, target_audience in project.samples[province].items():
        if target_audience.get('sample_type') not in ["Pilot", "Non"]:
            sample_size = calculate_sample_size(target_audience.get('sample_size', 0), target_audience.get('extra_rate', 0))
            daily_interview_target = target_audience['target']['daily_interview_target']

            quanty = round(sample_size / daily_interview_target, 2)
    
    return quanty

def get_other_default(project, element, province, title=""):
    return 1

def get_tienvanchuyen(project, element, province, title=""):
    return 2

def get_tienthue_location(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    clt_sample_size_per_day = project.clt_settings.get('clt_sample_size_per_day', 0)
    quanty = round(sample_size / clt_sample_size_per_day, 2)
    return quanty

def get_tienthue_tulanh(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    clt_sample_size_per_day = project.clt_settings.get('clt_sample_size_per_day', 0)
    quanty = round(sample_size / clt_sample_size_per_day, 2)
    return quanty

def get_tienthue_tivi(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    clt_sample_size_per_day = project.clt_settings.get('clt_sample_size_per_day', 0)
    quanty = round(sample_size / clt_sample_size_per_day, 2)
    return quanty

def get_tienthue_partition(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    clt_sample_size_per_day = project.clt_settings.get('clt_sample_size_per_day', 0)
    quanty = round(sample_size / clt_sample_size_per_day, 2)
    return quanty

def get_tien_setup_location(project, element, province, title=""):
    return 2

def get_tien_nuocuong_khangiay_banhlat(project, element, province, title=""):
    sample_size = calculate_total_of_sample_size(project.samples[province], excluding_items=["Pilot", "Non"])
    return sample_size

QUANTY_MAPPINGS = {
    "default" : get_default_quanty,
    "Chi phí thuê tablet < 9 inch" : get_chiphithue_thietbi,
    "Chi phí thuê tablet >= 9 inch" : get_chiphithue_thietbi,
    "Chi phí thuê laptop" : get_chiphithue_thietbi,

    "Chi phí gửi xe" : get_quanty_parking_fee,
    "Chi phí Phiếu PV - Bài rớt giữa chừng" : get_failure_rate,
    "Chi phí Tuyển đáp viên IDI" : get_chiphi_tuyendapvien_idi,
    #--SUPERVISOR / ASSISTANT
    "Chi phí Quản lý - On-field" : get_chiphi_ql_on_field,
    "Chi phí Quản lý recruit - On-field" : get_chiphi_ql_recruit_on_field,
    "Chi phí Quản lý ngồi bàn - On-field" : get_chiphi_ql_ngoiban_on_field,
    "Chi phí Quản lý IDI" : get_chiphi_ql_idi,

    "Chi phí Assistant - Set up" : get_chiphi_assistant_set_up,
    "Chi phí Assistant - On-field" : get_chiphi_assistant_on_field,

    #--QC
    "Chi phí QC - In home" : get_chiphi_qc_in_home,
    "Chi phí QC - In Location" : get_chiphi_qc_in_location,
    "Chi phí QC - IDI" : get_sample_recruit_idi,

    #--DP
    "Chi phí Coding" : get_chiphi_coding,
    "Chi phí Input" : get_chiphi_input,
    "Chi phí Quản lý - Hỗ trợ clean data" : get_chiphi_hotrocleandata,

    #--INCENTIVE
    "Quà Phiếu PV - Pilot": get_quaphieu_phongvan,
    "Quà Phiếu PV - Main": get_quaphieu_phongvan,
    "Quà Phiếu PV - Booster": get_quaphieu_phongvan,
    "Quà Phiếu PV - Non": get_quaphieu_phongvan,
    "Quà Phiếu PV - IDI" : get_sample_recruit_idi,
    
    #--COMMUNICATION
    "Chi phí Cước điện thoại cố định" : get_chiphi_cuocdienthoaicodinh,
    "Chi phí Card điện thoại" : get_chiphi_carddienthoai,

    #--STATIONARY
    "Photo trắng đen" : get_photo_trangden,
    "Showphoto" : get_show_photo,
    "Showcard" : get_show_card,
    "Dropcard" : get_drop_card,
    "In màu \ In concept" : get_inmau_inconcept,
    "Decal" : get_decal,
    "Ép Plastic" : get_ep_flastic,
    "Hồ sơ biểu mẫu" : get_hosobieumau,
    "Chi phí đóng cuốn" : get_chiphidongcuon,

    #--OTHER
    "other_default" : get_other_default,
    "Tiền vận chuyển" : get_tienvanchuyen,
    "Tiền thuê location" : get_tienthue_location, 
    "Tiền thuê tủ lạnh, …" : get_tienthue_tulanh,
    "Tiền thuê TV" : get_tienthue_tivi, 
    "Tiền thuê partition" : get_tienthue_partition,
    "Tiền set-up location" : get_tien_setup_location,
    "Tiền nước uống, khăn giấy, bánh lạt,…" : get_tien_nuocuong_khangiay_banhlat
}

def map_quanty_for_element(project, element, province, title=""):
    description = element.get('description', "")

    for key, func in QUANTY_MAPPINGS.items():
        if key == description:
            return func(project, element, province, title=title)
    
    if title == "OTHER":
        return QUANTY_MAPPINGS["other_default"](project, element, province)
    else:
        return QUANTY_MAPPINGS["default"](project, element, province)

###-------- QUANTY BY PRICING ---------------

def get_sample_size_by_province(project, price, province, target_audience):
    return calculate_sample_size(target_audience.get('sample_size', 0), target_audience.get('extra_rate', 0))

QUANTY_BY_PRICING_MAPPINGS = {
    "default" : get_sample_size_by_province, 
    "Chi phí Phiếu PV - Recruit" : get_sample_size_by_province,
    "Chi phí Phiếu PV - In Location" : get_sample_size_by_province
}
         
def map_quanty_for_price(project, price, province, target_audience):
    description = get_chi_phi_phieu_pv_title(price.get('type', "").lower())

    for key, func in QUANTY_BY_PRICING_MAPPINGS.items():
        if key == description:
            return func(project, price, province, target_audience)
    return QUANTY_BY_PRICING_MAPPINGS["default"](project, price, province, target_audience)
