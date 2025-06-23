# config/predefined_values.py
# -*- coding: utf-8 -*-
"""
Predefined values for the Project Cost Calculator application.
All dropdown lists and fixed options are defined here for easy maintenance.
"""
# Complexity
COMPLEXITY = [
    "Basic",
    "Standard",
    "Complex"
]

DATA_PROCESSING_METHOD = [
    "TOPLINE",
    "SPSS",
    "VISUAL SHELF",
    "BVC SPSS",
    "IBN SPSS"
]

# Project types
PROJECT_TYPES = [
"F2F/D2D",
"HUT",
"CLT",
"CATI"
]

SAMPLE_TYPES = [
    "Pilot",
    "Main",
    "Boosters",
    "Non"
]

# Sampling methods
SAMPLING_METHODS = [
"Random sampling",
"Purposive sampling",
"Intercept",
"Other"
]

# Type Of Quota Control
TYPE_OF_QUOTA_CONTROLS = [
    "No Quota",
    "Parallel Flexible Quota",
    "Parallel Fixed Quota",
    "Interlocked Quota"
]

QUOTA_DESCRIPTION = [
    "City",
    "Gender",
    "Age group",
    "Class",
    "LSM",
    "BUMO"
]

# Interview methods
INTERVIEW_METHODS = [
    "CAPI",
    "CATI",
    "ONLINE",
    "MS",
    "OTHER"
]

# Recruit Method
RECRUIT_METHOD = [
    "Client List",
    "FW free find/ FW connection"
]

# Service lines
SERVICE_LINES = [
    "BHT",
    "CEX",
    "HEC",
    "INNO",
    "IUU",
    "MSU",
    "S3"
]

CLIENTS = [
    "PEPSI",
    "TÂN HIỆP PHÁT"
]

# Industries by service line (dependency relationship)
INDUSTRIES_BY_SERVICE_LINE = [
    "Alcohol drinks", "Automotive", "Baby Diaper", "Banking", "Beauty", "Beer", "Beverage (Energy drink)", "Beverage (LRB)", "BFSI", "Biscuit", "Cider", "Cigarette", "Cigarettes / Tobacco", "CMB", "CMB & drinking yogurt", "Confectionery", "Confectionery (Bánh kẹo)", "Deodorant", "diary based milk", "Dishwashing", "Doctor - Normal disease", "Doctor - Rare disease", "Drinking yogurt", "Ecommerce", "Electrical", "Energy drink", "Fabric Softener", "Facial Cleanser", "Femcare", "Floor Cleaner", "Food", "Fresh Milk", "HCPs - Board of Management", "Healthcare", "Home applicance", "Ice-cream", "Infant Milk", "Insurance", "Liquid Detergent", "Liquid milk", "Milk", "Milk & dairy products", "Others", "Paint/ Chemical", "Patient - Rx Medicine", "Patient - Supplements & OTC Medicine", "Personal care", "Pharmacist", "Probiotic drinks", "Probiotics drinking yogurt", "Purified Water", "RTD Tea", "RTDT", "Seasoning (nước tương, nước mắm,…)", "Shampoo & Conditioner", "Shower Gel", "Snack", "Soya Milk", "Spoon Yogurt", "Stationary and School Supply", "Sterilized drinking yogurt", "Tabacco", "Tobacco", "Toothpaste", "Total FMCG", "yogurt"
]

# Vietnam provinces
VIETNAM_PROVINCES = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
    "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
    "Bình Thuận", "Cà Mau", "Cao Bằng", "Đà Nẵng",
    "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp",
    "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh",
    "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên",
    "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng",
    "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An",
    "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình",
    "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng",
    "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa",
    "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long",
    "Vĩnh Phúc", "Yên Bái", "Hồ Chí Minh", "Cần Thơ", "N/A"
]

# Common target audiences (examples, can be expanded)
TARGET_AUDIENCES = [
    "Bác sĩ chuyên khoa",
    "Bác sĩ đa khoa",
    "Chủ/ quản lý cửa hàng",
    "Dược sĩ nhà thuốc chuỗi",
    "Dược sĩ nhà thuốc lẻ",
    "HSSV, NVVP, Công nhân, Nội trợ",
    "N/A",
    "Nhân viên công ty bảo hiểm thuộc công ty KH",
    "Nhân viên y tế cấp quản lý"
]

# Default Target for Interviewers by target audience
TARGET_AUDIENCE_INTERVIEWER_TARGETS = {
    "Bác sĩ chuyên khoa": 2,
    "Bác sĩ đa khoa": 2,
    "Chủ/ quản lý cửa hàng": 2,
    "Dược sĩ nhà thuốc chuỗi": 2,
    "Dược sĩ nhà thuốc lẻ": 2,
    "HSSV, NVVP, Công nhân, Nội trợ": 2,
    "N/A": 2,
    "Nhân viên công ty bảo hiểm thuộc công ty KH": 2,
    "Nhân viên y tế cấp quản lý": 2
}

# QC Teams
QC_TEAMS = [
    "FW", "QC", "DP"
]

# QC Methods
QC_METHODS = [
    "QC tại nhà",
"QC qua điện thoại",
"QC qua điện thoại kiểm tra sự tồn tại",
"QC qua điện thoại (khoán nguyên dự án)",
"QC nghe file ghi âm",
"QC DP",
"QC phiếu Non",
"QC tại CLT",
"QC Coding",
]

# Level definitions for assigned people
ASSIGNED_PEOPLE_LEVELS = ["Junior", "Senior", "Manager", "Director"]

# Default travel costs per level
DEFAULT_TRAVEL_COSTS = {
    "Junior": {
        "hotel": 500000,  # Chi phí Khách sạn
        "food": 500000,   # Chi phí ăn uống
    },
    "Senior": {
        "hotel": 1000000,
        "food": 800000,
    },
    "Manager": {
        "hotel": 2000000,
        "food": 1000000,
    },
    "Director": {
        "hotel": 3000000,
        "food": 1200000,
    }
}

DURATION_RANGES = {
    "< 15 phút": (0, 14),
    "15-30 phút": (15, 30),
    "30-45 phút": (31, 45),
    "45-60 phút": (46, 60)
}

SUBCONTRACTORS = {
    "External Subcontract",
    "Ipsos Global Subcontract"
}

COST_TYPES = {
    "Coding", "Consulting", "Data Processing (modelling)", "Reporting", "Fieldwork Online", "Fieldwork Offline", "Scripting link", "Transcription", "Translation"
}

CURRENCIES = {
    "VND", "USD", "EUR", "GBP", "JPY", "CNY"
}