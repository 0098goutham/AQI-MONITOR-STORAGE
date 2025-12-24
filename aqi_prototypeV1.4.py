import pytesseract
from PIL import Image
import os
import re
import csv
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

# =====================================================
# CONFIGURATION
# =====================================================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "input_images")
CSV_FILE = os.path.join(BASE_DIR, "aqi_readings.csv")

PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500),
]

# =====================================================
# OCR + PROCESSING
# =====================================================
def preprocess_image(image_path):
    img = Image.open(image_path).convert("L")
    img = img.point(lambda x: 0 if x < 160 else 255, "1")
    return img

def normalize_text(text):
    text = text.upper().replace("S", "5").replace("O", "0")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(PM|MP)\s*2\s*\.?\s*5", "PM2.5", text)
    return text.strip()

def extract_pm25(text):
    pm_patterns = [
        r"PM2\.5\s*[: ]*\s*([0-9]+(?:\.[0-9]+)?)",
        r"PM25\s*[: ]*\s*([0-9]+(?:\.[0-9]+)?)",
        r"P25[A-Z]*\s*([0-9]+(?:\.[0-9]+)?)",
    ]
    for pat in pm_patterns:
        m = re.search(pat, text)
        if m:
            return float(m.group(1))

    nums = [float(n) for n in re.findall(r"\b[0-9]{1,3}(?:\.[0-9]+)?\b", text)]
    nums = [n for n in nums if 0 <= n <= 500]
    return nums[0] if len(nums) == 1 else None

def compute_aqi_from_pm25(pm25):
    if pm25 is None:
        return None
    for C_low, C_high, I_low, I_high in PM25_BREAKPOINTS:
        if C_low <= pm25 <= C_high:
            aqi = ((I_high - I_low) / (C_high - C_low)) * (pm25 - C_low) + I_low
            return round(aqi)
    return None

def filter_and_validate(raw_text):
    text = normalize_text(raw_text)
    pm25 = extract_pm25(text)
    if pm25 is None or not (0 <= pm25 <= 500):
        return None

    aqi = compute_aqi_from_pm25(pm25)
    if aqi is None or not (0 <= aqi <= 500):
        return None

    return {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "PM2.5": pm25,
        "AQI": aqi,
    }

def classify_air_quality(aqi):
    # Short names as in spec: Good / Moderate / Poor...
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Moderate", "🟡"
    elif aqi <= 150:
        return "Poor", "🟠"
    elif aqi <= 200:
        return "Unhealthy", "🔴"
    elif aqi <= 300:
        return "Very Unhealthy", "🟣"
    return "Hazardous", "⚫"

# =====================================================
# STORAGE
# =====================================================
class LocalStorage:
    def __init__(self, csv_path):
        self.file = Path(csv_path)
        if not self.file.exists():
            with self.file.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])

    def save(self, record):
        status, _ = classify_air_quality(record["AQI"])
        record["Status"] = status
        with self.file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [record["Timestamp"], record["PM2.5"], record["AQI"], status]
            )

    def get_history(self):
        try:
            with self.file.open("r") as f:
                lines = f.readlines()
            return len(lines) - 1 if len(lines) > 1 else 0
        except:
            return 0

# =====================================================
# GUI DASHBOARD
# =====================================================
class AQIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OFFLINE AIR QUALITY MONITOR")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a1a")

        self.storage = LocalStorage(CSV_FILE)

        self.setup_ui()
        os.makedirs(IMAGE_FOLDER, exist_ok=True)

    def setup_ui(self):
        # MAIN TITLE
        title = tk.Label(
            self.root,
            text="AIR QUALITY MONITOR",
            font=("Arial", 24, "bold"),
            fg="#00ff88",
            bg="#1a1a1a",
        )
        title.pack(pady=5)

        # SMALL SUBTITLE
        subtitle = tk.Label(
            self.root,
            text="PM2.5 → AQI → Status", # (for one fixed location)
            font=("Arial", 11),
            fg="#cccccc",
            bg="#1a1a1a",
        )
        subtitle.pack(pady=(0, 10))

        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # LEFT: current reading
        left_frame = tk.Frame(main_frame, bg="#1a1a1a")
        left_frame.pack(side="left", fill="both", expand=True)

        # HEADING ABOVE BIG NUMBER
        tk.Label(
            left_frame,
            text="AQI VALUE (Air Quality Index)",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#1a1a1a",
        ).pack(pady=(0, 5))

        self.aqi_label = tk.Label(
            left_frame,
            text="--",
            font=("Arial", 72, "bold"),
            fg="#00ff88",
            bg="#2d2d2d",
            width=8,
            height=2,
        )
        self.aqi_label.pack(pady=10)

        # HEADING + STATUS NAME
        tk.Label(
            left_frame,
            text="AQI CATEGORY",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#1a1a1a",
        ).pack(pady=(10, 0))

        self.status_label = tk.Label(
            left_frame,
            text="No Data",
            font=("Arial", 22, "bold"),
            fg="#ffcc00",
            bg="#1a1a1a",
        )
        self.status_label.pack(pady=5)

        # HEADING + PM2.5
        tk.Label(
            left_frame,
            text="PM2.5 CONCENTRATION (µg/m³)",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#1a1a1a",
        ).pack(pady=(10, 0))

        self.pm_label = tk.Label(
            left_frame,
            text="-- µg/m³",
            font=("Arial", 16),
            fg="#cccccc",
            bg="#1a1a1a",
        )
        self.pm_label.pack()

        self.time_label = tk.Label(
            left_frame,
            text="Last updated: --",
            font=("Arial", 12),
            fg="#888888",
            bg="#1a1a1a",
        )
        self.time_label.pack(pady=(5, 0))

        # RIGHT: controls + history + status log
        right_frame = tk.Frame(main_frame, bg="#1a1a1a", width=250)
        right_frame.pack(side="right", fill="y")
        right_frame.pack_propagate(False)

        tk.Label(
            right_frame,
            text="CONTROLS",
            font=("Arial", 16, "bold"),
            fg="#00ff88",
            bg="#1a1a1a",
        ).pack(pady=10)

        tk.Button(
            right_frame,
            text="Process Image",
            font=("Arial", 14),
            bg="#00ff88",
            fg="black",
            command=self.process_image,
            relief="flat",
            padx=20,
            pady=10,
        ).pack(pady=10, fill="x")

        tk.Label(
            right_frame,
            text="HISTORY",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#1a1a1a",
        ).pack(pady=(30, 10))

        self.history_label = tk.Label(
            right_frame,
            text="0 readings",
            font=("Arial", 16, "bold"),
            fg="#cccccc",
            bg="#1a1a1a",
        )
        self.history_label.pack()

        tk.Label(
            right_frame,
            text="STATUS LOG",
            font=("Arial", 12, "bold"),
            fg="#888888",
            bg="#1a1a1a",
        ).pack(pady=(20, 5))

        self.status_text = tk.Text(
            right_frame,
            height=6,
            width=28,
            bg="#2d2d2d",
            fg="#cccccc",
            font=("Consolas", 10),
        )
        self.status_text.pack(pady=5, fill="x")

    def log_status(self, message):
        self.status_text.insert(
            tk.END, f"{datetime.now().strftime('%H:%M:%S')}: {message}\n"
        )
        self.status_text.see(tk.END)

    def update_dashboard(self, record):
        status, emoji = classify_air_quality(record["AQI"])

        # Number = AQI value
        self.aqi_label.config(text=str(record["AQI"]), fg="#00ff88")

        # Category name
        status_text = f"{emoji}  {status}"
        self.status_label.config(text=status_text, fg="#ffcc00")

        # PM2.5
        self.pm_label.config(text=f"{record['PM2.5']:.1f} µg/m³", fg="#00ff88")

        # Time label with explanation
        self.time_label.config(
            text=f"Last updated: {record['Timestamp']}", fg="#cccccc"
        )

        self.history_label.config(text=f"{self.storage.get_history()} readings")
        self.log_status(f"NEW: AQI {record['AQI']} - {status}")

    def process_image_thread(self, image_path):
        try:
            self.log_status(f"Processing: {os.path.basename(image_path)}")
            img = preprocess_image(image_path)
            raw_text = pytesseract.image_to_string(
                img, config="--psm 11 -c tessedit_char_whitelist=0123456789.PM25"
            )
            self.log_status(f"OCR: {repr(raw_text.strip())}")

            result = filter_and_validate(raw_text)
            if result:
                self.storage.save(result)
                self.root.after(0, lambda: self.update_dashboard(result))
            else:
                self.root.after(
                    0, lambda: self.log_status("REJECTED: No valid PM2.5 data")
                )
        except Exception as e:
            self.root.after(0, lambda: self.log_status(f"Error: {str(e)}"))

    def process_image(self):
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
        filename = filedialog.askopenfilename(
            initialdir=IMAGE_FOLDER,
            title="Select AQI Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")],
        )
        if filename:
            threading.Thread(
                target=self.process_image_thread, args=(filename,), daemon=True
            ).start()

    def on_closing(self):
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AQIApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
