import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# MEMBER 3: DATA PROCESSING MODULE (Fazila's PLANET.py - SIMPLIFIED)
# ═══════════════════════════════════════════════════════════════════════
def classify_air_quality(aqi):
    if 0 <= aqi <= 50:
        return "Good"
    elif 51 <= aqi <= 100:
        return "Moderate"
    else:
        return "Poor"

def simulate_member3_processing():
    """Simulates Member 3's output"""
    print("🔄 MEMBER 3  PROCESSING...")
    # Simulate manual input like in PLANET.py
    test_inputs = [
        ("PM2.5 85 AQI 120"),
        ("PM2.5 45 AQI 65"), 
        ("PM2.5 28 AQI 42")
    ]
    
    records = []
    for user_input in test_inputs:
        parts = user_input.split()
        pm25_value = float(parts[1])
        aqi_value = int(parts[3])
        
        status = classify_air_quality(aqi_value)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        record = {
            "Timestamp": timestamp,
            "Location": "PM2.5",  # ← Member 3's extra field
            "PM2.5": pm25_value,
            "AQI": aqi_value,
            "Status": status
        }
        records.append(record)
        print(f"📤 MEMBER 3 → YOU: {record}")
    
    return records

# ═══════════════════════════════════════════════════════════════════════
# MEMBER 4: YOUR STORAGE MODULE (Goutam)
# ═══════════════════════════════════════════════════════════════════════
class LocalStorageManager:
    def __init__(self, filename: str = "aqi_readings.csv"):
        self.csv_file = Path(filename)
        self.init_storage()
    
    def init_storage(self):
        if not self.csv_file.exists():
            with self.csv_file.open(mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])
    
    def save_reading(self, record: Dict[str, Any]):
        # AUTO-REMOVE Location field
        clean_record = {
            "Timestamp": record.get("Timestamp", ""),
            "PM2.5": record.get("PM2.5", ""),
            "AQI": record.get("AQI", ""),
            "Status": record.get("Status", "")
        }
        
        with self.csv_file.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                clean_record["Timestamp"],
                clean_record["PM2.5"], 
                clean_record["AQI"],
                clean_record["Status"]
            ])
        print(f"✅ YOUR STORAGE SAVED: {clean_record}")
    
    def show_all_data(self):
        if not self.csv_file.exists():
            print("📁 No data yet")
            return
        print("\n📊 YOUR FINAL CSV DATA:")
        print("-" * 40)
        with self.csv_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"  {row['Timestamp']:10} | {row['PM2.5']:6} | {row['AQI']:4} | {row['Status']}")

# ═══════════════════════════════════════════════════════════════════════
# MAIN INTEGRATION (How it works end-to-end)
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 COMPLETE AQI SYSTEM: Member 3 → Member 4")
    print("=" * 60)
    
    # Create YOUR storage
    storage = LocalStorageManager()
    
    # Member 3 processes data
    member3_records = simulate_member3_processing()
    
    # YOUR STORAGE receives each record
    for record in member3_records:
        storage.save_reading(record)
    
    # Show final result
    storage.show_all_data()
