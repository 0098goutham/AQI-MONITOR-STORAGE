import csv
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# MEMBER 3: REAL MANUAL INPUT (Exact PLANET.py experience)
# ═══════════════════════════════════════════════════════════════════════
def classify_air_quality(aqi):
    if 0 <= aqi <= 50:
        return "Good"
    elif 51 <= aqi <= 100:
        return "Moderate"
    else:
        return "Poor"

def member3_real_manual_input():
    """REAL Member 3 experience - MANUAL input like PLANET.py"""
    print("🧑‍💻 MANUAL Air Quality Input Mode (Member 3)")
    print("Type values like: PM2.5 85 AQI 120")
    print("Type 'exit' to stop\n")
    
    records = []
    while True:
        user_input = input("Enter reading: ")
        if user_input.lower() == "exit":
            print("Stopping input.")
            break
            
        try:
            parts = user_input.split()
            location = parts[0]      # "PM2.5"
            pm25_value = float(parts[1])  # 85
            aqi_value = int(parts[3])     # 120
            
            # Basic validation (from PLANET.py)
            if pm25_value < 0 or aqi_value < 0:
                print("REJECTED: Invalid or unreliable reading")
                continue
            
            status = classify_air_quality(aqi_value)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            record = {
                "Timestamp": timestamp,
                "Location": location,    # Member 3's extra field
                "PM2.5": pm25_value,
                "AQI": aqi_value,
                "Status": status
            }
            
            records.append(record)
            print("✅ ACCEPTED:", record)
            
        except:
            print("❌ REJECTED: Invalid or unreliable reading")
    
    return records

# ═══════════════════════════════════════════════════════════════════════
# MEMBER 4: YOUR STORAGE MODULE
# ═══════════════════════════════════════════════════════════════════════
class LocalStorageManager:
    def __init__(self, filename: str = "aqi_readings.csv"):
        self.csv_file = Path(filename)
        self.init_storage()
    
    def init_storage(self):
        try:
            if not self.csv_file.exists():
                with self.csv_file.open(mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])
                print(f"✅ Storage ready: {self.csv_file}")
        except Exception as e:
            print(f"❌ Storage init error: {e}")
    
    def save_reading(self, record: Dict[str, Any]):
        try:
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
            print(f"💾 YOUR STORAGE SAVED: {clean_record}")
            
        except Exception as e:
            print(f"❌ Save error: {e}")
    
    def show_all_data(self):
        try:
            if not self.csv_file.exists():
                print("📁 No data saved yet")
                return
            print("\n📊 YOUR FINAL CSV DATA:")
            print("-" * 40)
            with self.csv_file.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(f"  {row['Timestamp']:10} | {row['PM2.5']:6} | {row['AQI']:4} | {row['Status']}")
        except Exception as e:
            print(f"❌ Read error: {e}")

# ═══════════════════════════════════════════════════════════════════════
# MAIN INTEGRATION
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 COMPLETE AQI SYSTEM: Member 3 → Member 4")
    print("=" * 60)
    
    # YOUR STORAGE
    storage = LocalStorageManager("manual_aqi.csv")
    
    # MEMBER 3 MANUAL INPUT (REAL experience)
    member3_records = member3_real_manual_input()
    
    print(f"\n🔄 Member 3 sent {len(member3_records)} records to YOUR storage...")
    
    # YOUR STORAGE receives each record
    for record in member3_records:
        storage.save_reading(record)
    
    # Show YOUR final result
    storage.show_all_data()
    
    print("\n🎉 SYSTEM COMPLETE!")
