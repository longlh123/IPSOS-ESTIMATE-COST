import pandas as pd
import json
import numpy as np

def build_cost_hierarchy_from_csv(csv_path):
    df = pd.read_csv(
        csv_path,
        header=[0],
        index_col=[0, 1, 2, 3, 4, 5, 6, 7, 8],
        encoding="utf-8"
    )
    df.fillna("", inplace=True)

    hierarchy = {}

    for idx, row in df.iterrows():
        project_type, s1, s2, s3, s4, s5, s6, code, unit = idx
        base_cost = row.get(("Base Cost", ""), 0)

        keys = [project_type, s1, s2, s3, s4, s5]
        current_level = hierarchy
        
        for key in keys:
            if pd.isnull(key) or not key or pd.isna(key):
                break
            if key not in current_level:
                current_level[key] = {
                    "children": {},
                    "elements": []
                }
            node = current_level[key]        # giữ lại node đầy đủ
            current_level = node["children"] # đi xuống children

        # Add element at the last level (not using s5 as key)
        element = {
            "code": code,
            "unit": "" if pd.isnull(unit) else unit,
            "description": s6,
            "cost": 0
        }
        
        # Add base cost to the element
        for col in df.columns:
            element["cost"] = row[col]
        
        node["elements"].append(element)

    return hierarchy


if __name__ == "__main__":
    csv_file = "CLT.csv"  # Đường dẫn đến file CSV
    hierarchy = build_cost_hierarchy_from_csv(csv_file)

    # Ghi kết quả ra file JSON
    with open("clt_cost_hierarchy.json", "w", encoding="utf-8") as f:
        json.dump(hierarchy, f, ensure_ascii=False, indent=2)

    print("✅ Hierarchy JSON has been saved to 'clt_cost_hierarchy.json'")
