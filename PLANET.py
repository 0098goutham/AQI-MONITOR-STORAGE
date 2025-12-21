from datetime import datetime

def classify_air_quality(aqi):
    if 0 <= aqi <= 50:
        return "Good"
    elif 51 <= aqi <= 100:
        return "Moderate"
    else:
        return "Poor"


print("Manual Air Quality Input Mode")
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

        location = parts[0]          # PM2.5
        pm25_value = float(parts[1]) # PM2.5 value
        aqi_value = int(parts[3])    # AQI value

        # Basic validation
        if pm25_value < 0 or aqi_value < 0:
            raise ValueError

        status = classify_air_quality(aqi_value)
        timestamp = datetime.now().strftime("%H:%M:%S")

        record = {
            "Timestamp": timestamp,
            "Location": location,
            "PM2.5": pm25_value,
            "AQI": aqi_value,
            "Status": status
        }

        records.append(record)
        print("ACCEPTED:", record)

    except:
        print("REJECTED: Invalid or unreliable reading")

print("\nFinal Processed Records:")
for r in records:
    print(r)
