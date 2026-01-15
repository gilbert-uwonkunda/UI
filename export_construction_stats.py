# export_construction_stats.py
# Run this script to update construction_stats.json with latest data from geodatabase
# Schedule with Windows Task Scheduler for automatic updates

import arcpy
import json
from datetime import datetime
from collections import defaultdict

# Configuration
FC_PATH = r"E:\Projects\SecondaryCities\Publish.gdb\National_Construction_Master_2025"
OUTPUT_PATH = OUTPUT_PATH = r"E:\Projects\UNDP\UNDP\Home Page\construction_stats.json"  # Your GitHub repo folder

# Official Rwanda zoning colors
ZONING_COLORS = {
    "W5": "#c6e0b4", "W4": "#c6e0b4", "W3": "#c6e0b4", "W2": "#c6e0b4",
    "U": "#7f5f3f", "T": "#b2b2b2", "T1": "#b2b2b2",
    "R4": "#ff5a25", "R3": "#ff7f00", "R2": "#ffbb36",
    "R1B": "#ffebb0", "R1A": "#ffec18", "R1": "#ffff7f",
    "PF5": "#003fff", "PF4": "#003fff", "PF3": "#003fff", "PF2": "#003fff", "PF1": "#003fff",
    "PA": "#00ffff",
    "P3C": "#0d4925", "P3B": "#0d4925", "P2": "#007f3f", "P1": "#7dff00",
    "I3": "#9452a5", "I2": "#9c7abc", "I1": "#c27ac0",
    "C3": "#960202", "C1": "#cc3366",
    "A1": "#6e8131", "A2": "#6e8131",
    "ET": "#888888"
}

def export_stats():
    print(f"Reading data from: {FC_PATH}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize stats structure
    stats = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "national": {
            "total": 0,
            "legal": 0,
            "illegal": 0,
            "existing": 0,
            "demolished": 0,
            "compliance": 0
        },
        "provinces": {},
        "districts": [],
        "zoning": []
    }
    
    # Temporary storage for aggregation
    province_data = defaultdict(lambda: {"total": 0, "legal": 0, "illegal": 0})
    district_data = defaultdict(lambda: {"province": "", "district": "", "total": 0, "legal": 0, "illegal": 0})
    zone_illegal = defaultdict(int)
    
    # Read all records
    fields = ["province", "district", "legal_t", "zone_code"]
    record_count = 0
    
    with arcpy.da.SearchCursor(FC_PATH, fields) as cursor:
        for row in cursor:
            prov = row[0] if row[0] else "Unknown"
            dist = row[1] if row[1] else "Unknown"
            legal = row[2] if row[2] else "Unknown"
            zone = row[3] if row[3] else "Unknown"
            
            record_count += 1
            
            # National totals
            stats["national"]["total"] += 1
            if legal == "Legal":
                stats["national"]["legal"] += 1
            elif legal == "Illegal":
                stats["national"]["illegal"] += 1
            elif legal == "Existing":
                stats["national"]["existing"] += 1
            elif legal == "Demolished":
                stats["national"]["demolished"] += 1
            
            # Province aggregation
            province_data[prov]["total"] += 1
            if legal == "Legal":
                province_data[prov]["legal"] += 1
            elif legal == "Illegal":
                province_data[prov]["illegal"] += 1
            
            # District aggregation
            key = f"{prov}|{dist}"
            district_data[key]["province"] = prov
            district_data[key]["district"] = dist
            district_data[key]["total"] += 1
            if legal == "Legal":
                district_data[key]["legal"] += 1
            elif legal == "Illegal":
                district_data[key]["illegal"] += 1
            
            # Zoning (illegal only)
            if legal == "Illegal" and zone and zone != "Unknown":
                zone_illegal[zone] += 1
    
    print(f"Processed {record_count:,} records")
    
    # Calculate national compliance
    verified = stats["national"]["legal"] + stats["national"]["illegal"]
    if verified > 0:
        stats["national"]["compliance"] = round((stats["national"]["legal"] / verified) * 100, 1)
    
    # Process province data with compliance
    for prov, data in province_data.items():
        verified = data["legal"] + data["illegal"]
        compliance = round((data["legal"] / verified) * 100, 1) if verified > 0 else 0
        stats["provinces"][prov] = {
            "total": data["total"],
            "legal": data["legal"],
            "illegal": data["illegal"],
            "compliance": compliance
        }
    
    # Process district data with compliance, sorted by illegal count
    districts_list = []
    for key, data in district_data.items():
        verified = data["legal"] + data["illegal"]
        compliance = round((data["legal"] / verified) * 100, 1) if verified > 0 else 0
        districts_list.append({
            "province": data["province"],
            "district": data["district"],
            "total": data["total"],
            "legal": data["legal"],
            "illegal": data["illegal"],
            "compliance": compliance
        })
    
    # Sort by illegal count (descending)
    stats["districts"] = sorted(districts_list, key=lambda x: -x["illegal"])
    
    # Process zoning data (top 12)
    sorted_zones = sorted(zone_illegal.items(), key=lambda x: -x[1])[:12]
    stats["zoning"] = [
        {
            "code": code,
            "illegal": count,
            "color": ZONING_COLORS.get(code, "#666666")
        }
        for code, count in sorted_zones
    ]
    
    # Write JSON
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*50}")
    print(f"EXPORT COMPLETE")
    print(f"{'='*50}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Total buildings: {stats['national']['total']:,}")
    print(f"Legal: {stats['national']['legal']:,}")
    print(f"Illegal: {stats['national']['illegal']:,}")
    print(f"Compliance: {stats['national']['compliance']}%")
    print(f"Provinces: {len(stats['provinces'])}")
    print(f"Districts: {len(stats['districts'])}")
    print(f"Zoning categories: {len(stats['zoning'])}")
    print(f"{'='*50}")
    
    return stats

if __name__ == "__main__":
    export_stats()