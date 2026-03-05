import time

last_garbage_count = 0
 
dashboard_data = {
    "garbage_count": 0,
    "last_sms": "No SMS yet",
    "level": "Clean",
    "timestamp": "No data",
    "location": "Waiting for GPS",
    "history": []
}
def update_dashboard(count, sms_status):
    dashboard_data["garbage_count"] = int(count)
    dashboard_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # ✅ history add (keep last 60 points)
    dashboard_data["history"].append({"t": time.time(), "count": int(count)})
    dashboard_data["history"] = dashboard_data["history"][-60:]
    
    # level logic
    if count == 0:
        dashboard_data["level"] = "Clean"
    elif count < 4:
        dashboard_data["level"] = "Low"
    elif count < 10:
        dashboard_data["level"] = "Medium"
    else:
        dashboard_data["level"] = "HIGH"
    dashboard_data["last_sms"] = sms_status
