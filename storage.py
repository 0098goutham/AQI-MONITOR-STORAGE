import csv
from pathlib import Path
from typing import Dict

class LocalStorageManager:
    def __init__(self, filename: str = "aqi_readings.csv"):
        self.csv_file = Path(filename)
        self.init_storage()
    
    def init_storage(self):
        """Create CSV with headers if it doesn't exist"""
        if not self.csv_file.exists():
            with self.csv_file.open(mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])
    
    def save_reading(self, record: Dict):
        """
        Takes Member 3's output and saves to CSV
        
        Args:
            record: dict with Timestamp, PM2.5, AQI, Status
        """
        with self.csv_file.open(mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record["Timestamp"],
                record["PM2.5"], 
                record["AQI"],
                record["Status"]
            ])
        print(f"✅ Saved: {record['Timestamp']} | PM2.5:{record['PM2.5']} | AQI:{record['AQI']} | {record['Status']}")
    
    def get_latest_reading(self) -> Dict:
        """Get most recent reading for dashboard"""
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

# 🎯 USAGE - How you integrate with Member 3
storage = LocalStorageManager()

# When Member 3 finishes processing, they call:
def from_member3_processing():
    # Example data from Fazila's processing module
    processed_record = {
        "Timestamp": "17:35",
        "PM2.5": 82.5,
        "AQI": 115,
        "Status": "Poor"
    }
    
    # YOU SAVE IT
    storage.save_reading(processed_record)

# For dashboard (Member 5)
latest = storage.get_latest_reading()
print(latest)  # {"Timestamp": "17:35", "PM2.5": 82.5, "AQI": 115, "Status": "Poor"}
