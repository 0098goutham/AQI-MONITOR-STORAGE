import csv
from pathlib import Path
from typing import Dict
from datetime import datetime
import time

class LocalStorageManager:
    def __init__(self, filename: str = "aqi_readings.csv"):
        self.csv_file = Path(filename)
        self.init_storage()
    
    def init_storage(self):
        if not self.csv_file.exists():
            with self.csv_file.open(mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])
    
    def save_reading(self, record: Dict):
        with self.csv_file.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record["Timestamp"],
                record["PM2.5"], 
                record["AQI"],
                record["Status"]
            ])
        print(f"✅ SAVED: {record['Timestamp']} | PM2.5:{record['PM2.5']} | AQI:{record['AQI']} | {record['Status']}")
    
    def get_latest_reading(self) -> Dict:
        if not self.csv_file.exists():
            return None
        with self.csv_file.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            readings = list(reader)
            if readings:
                latest = readings[-1].copy()
                latest["PM2.5"] = float(latest["PM2.5"])
                latest["AQI"] = int(latest["AQI"])
                return latest
        return None
    
    def show_all_data(self):
        """Show complete CSV content"""
        if not self.csv_file.exists():
            print("📁 No data yet")
            return
        print("\n📊 ALL SAVED DATA:")
        print("-" * 50)
        with self.csv_file.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"  {row['Timestamp']:10} | {row['PM2.5']:6} | {row['AQI']:4} | {row['Status']}")

# 🔥 SIMULATE MEMBER 3 OUTPUT (FAZILA'S PROCESSING)
def simulate_member3_output(storage):
    """Generate fake data like Member 3 would"""
    statuses = ["Good", "Moderate", "Poor", "Poor", "Moderate"]
    
    for i in range(5):
        # Simulate real AQI values
        pm25 = 25 + i * 12.5  # 25, 37.5, 50, 62.5, 75
        aqi = 40 + i * 20     # 40, 60, 80, 100, 120
        status = statuses[i]
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        record = {
            "Timestamp": timestamp,
            "PM2.5": round(pm25, 1),
            "AQI": aqi,
            "Status": status
        }
        
        # "Member 3" sends data to YOU
        print(f"\n📥 MEMBER 3 SENDING: {record}")
        storage.save_reading(record)
        
        # Simulate time between readings
        time.sleep(1)
    
    print("\n🎉 TEST COMPLETE! Check your CSV file.")

# 🚀 RUN THE TEST
if __name__ == "__main__":
    storage = LocalStorageManager()
    
    print("🧪 TESTING LOCAL STORAGE MODULE")
    print("=" * 50)
    
    # Show initial state
    storage.show_all_data()
    
    # Simulate 5 readings from Member 3
    simulate_member3_output(storage)
    
    # Final state
    print("\n📁 FINAL CSV CONTENT:")
    storage.show_all_data()
    
    # Show latest for dashboard
    latest = storage.get_latest_reading()
    print(f"\n🎯 LATEST FOR DASHBOARD: {latest}")
