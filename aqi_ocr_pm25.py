import pytesseract
from PIL import Image
import os
import re
import csv
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

# 1. Adjust this path to your actual Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "input_images")
CSV_FILE = os.path.join(BASE_DIR, "aqi_readings.csv")

# If needed, explicitly tell Tesseract where tessdata lives (parent of tessdata)
# import os as _os
# _os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR"

# PM2.5 breakpoints (µg/m³) and AQI ranges – from AQI spec / article [page:0][web:40]
PM25_BREAKPOINTS = [
    # (C_low, C_high, I_low, I_high)
    (0.0,   12.0,    0,   50),   # Good
    (12.1,  35.4,   51,  100),   # Moderate
    (35.5,  55.4,  101,  150),   # Unhealthy for Sensitive Groups
    (55.5, 150.4,  151,  200),   # Unhealthy
    (150.5, 250.4, 201,  300),   # Very Unhealthy
    (250.5, 500.4, 301,  500),   # Hazardous
]

# =====================================================
# OCR PREPROCESSING
# =====================================================

def preprocess_image(image_path):
    """
    Open image, convert to grayscale and apply simple thresholding
    to improve OCR on digital displays.
    """
    img = Image.open(image_path).convert("L")
    img = img.point(lambda x: 0 if x < 160 else 255, "1")
    return img

# =====================================================
# TEXT NORMALIZATION
# =====================================================

def normalize_text(text):
    """
    Normalize OCR text:
    - Uppercase
    - Fix common OCR confusions (S->5, O->0)
    - Collapse whitespace
    - Normalize 'PM2.5' variants
    """
    text = text.upper()
    text = text.replace("S", "5").replace("O", "0")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(PM|MP)\s*2\s*\.?\s*5", "PM2.5", text)
    text = text.strip()
    return text

# =====================================================
# PM2.5 EXTRACTION (NO DIRECT AQI)
# =====================================================

def extract_pm25(text):
    """
    Extract PM2.5 numeric value from normalized text.
    Tries labeled patterns first, then a safe fallback.
    """
    pm_patterns = [
        r"PM2\.5\s*[: ]*\s*([0-9]+(?:\.[0-9]+)?)",
        r"PM25\s*[: ]*\s*([0-9]+(?:\.[0-9]+)?)",
        r"P25[A-Z]*\s*([0-9]+(?:\.[0-9]+)?)"
    ]

    for pat in pm_patterns:
        m = re.search(pat, text)
        if m:
            return float(m.group(1))

    # Fallback: single standalone number in reasonable range
    nums = [float(n) for n in re.findall(r"\b[0-9]{1,3}(?:\.[0-9]+)?\b", text)]
    nums = [n for n in nums if 0 <= n <= 500]
    if len(nums) == 1:
        return nums[0]

    return None

# =====================================================
# AQI COMPUTATION FROM PM2.5
# =====================================================

def compute_aqi_from_pm25(pm25):
    """
    Convert PM2.5 concentration (µg/m³) to AQI using
    the standard linear interpolation formula and PM2.5 breakpoints. [page:0][web:40]
    """
    if pm25 is None:
        return None

    for C_low, C_high, I_low, I_high in PM25_BREAKPOINTS:
        if C_low <= pm25 <= C_high:
            aqi = ((I_high - I_low) / (C_high - C_low)) * (pm25 - C_low) + I_low
            return round(aqi)

    return None

# =====================================================
# FILTER + VALIDATE FULL READING
# =====================================================

def filter_and_validate(raw_text):
    text = normalize_text(raw_text)
    pm25 = extract_pm25(text)

    if pm25 is None:
        return None

    if not (0 <= pm25 <= 500):
        return None

    aqi = compute_aqi_from_pm25(pm25)
    if aqi is None or not (0 <= aqi <= 500):
        return None

    return {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "PM2.5": pm25,
        "AQI": aqi
    }

# =====================================================
# AQI CATEGORY
# =====================================================

def classify_air_quality(aqi):
    """
    Map AQI numeric value to category text,
    matching the standard 6-level AQI scale. [page:0]
    """
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

# =====================================================
# LOCAL CSV STORAGE
# =====================================================

class LocalStorage:
    def __init__(self, csv_path):
        self.file = Path(csv_path)
        if not self.file.exists():
            with self.file.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "PM2.5", "AQI", "Status"])

    def save(self, record):
        with self.file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                record["Timestamp"],
                record["PM2.5"],
                record["AQI"],
                record["Status"]
            ])
        print("✅ STORED:", record)

# =====================================================
# MANUAL OCR FLOW
# =====================================================

def run_manual_ocr():
    storage = LocalStorage(CSV_FILE)

    while True:
        if not os.path.isdir(IMAGE_FOLDER):
            print(f"❌ Image folder not found: {IMAGE_FOLDER}")
            break

        images = [
            img for img in os.listdir(IMAGE_FOLDER)
            if img.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not images:
            print("❌ No images found in input_images folder.")
            break

        print("\nAvailable Images:")
        for i, img in enumerate(images, start=1):
            print(f"{i}. {img}")
        print("0. Exit")

        try:
            choice = int(input("\nSelect image number: "))

            if choice == 0:
                print("Exiting.")
                break

            if choice < 1 or choice > len(images):
                print("Invalid selection.")
                continue

            image_path = os.path.join(IMAGE_FOLDER, images[choice - 1])

            img = preprocess_image(image_path)

            # Whitelist digits, dot, and letters needed for "PM" etc. [web:60][web:49]
            ocr_config = "--psm 11 -c tessedit_char_whitelist=0123456789.PM"

            raw_text = pytesseract.image_to_string(img, config=ocr_config)

            print("\n--- RAW OCR OUTPUT ---")
            print(raw_text)

            result = filter_and_validate(raw_text)

            print("--------------------------------")

            if result:
                result["Status"] = classify_air_quality(result["AQI"])
                storage.save(result)
            else:
                print("❌ REJECTED: No reliable numeric data")

            print("--------------------------------")
            input("Press ENTER to continue...")

        except ValueError:
            print("Please enter a valid number.")

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    print("\n📷 MANUAL AIR QUALITY OCR SYSTEM (PM2.5 → AQI)\n")
    run_manual_ocr()
