from twilio.rest import Client
from dashboard_data import dashboard_data
import time

# ---------------------------------------
# 🔹 Twilio Credentials
# ---------------------------------------
ACCOUNT_SID = "ACe6exxxxxxxxxxxxx322118"
AUTH_TOKEN = "73eaxxxxxxxxx95cf1e98a810c0c35"
TWILIO_NUMBER = "+15077xxxx"
TARGET_NUMBER = "+91843xxxxx"

# ---------------------------------------
# 🔹 Alert System Variables
# ---------------------------------------
last_garbage_count = 0
last_reset_time = time.time()

THRESHOLD_INCREASE = 4
RESET_INTERVAL = 24 * 60 * 60

# ---------------------------------------
# 🔹 Location
# ---------------------------------------
CANAL_LOCATION = "Anna Nagar Canal, Chennai"

# ---------------------------------------
# 🔹 Send SMS Function
# ---------------------------------------
def send_alert_sms(current_count):
    global last_garbage_count, last_reset_time

    now = time.time()

    # Reset alert system every 24 hours
    if now - last_reset_time > RESET_INTERVAL:
        last_garbage_count = 0
        last_reset_time = now
        print("🔄 Daily alert reset completed.")

    # Check threshold increase
    if current_count - last_garbage_count >= THRESHOLD_INCREASE:
        location_live = dashboard_data.get("location", "")
        maps_link = f"https://maps.google.com/?q={location_live}" if location_live else CANAL_LOCATION
        message_text = (
         f"⚠️ CanalGuard AI Alert!\n"
         f"🗑️ Garbage Count: {current_count}\n"
         f"📍 Location:\n{maps_link}\n"
         f"🚨 Immediate cleaning required!"
)
           
        

        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            sms = client.messages.create(
                body=message_text,
                from_=TWILIO_NUMBER,
                to=TARGET_NUMBER
            )
            print("📩 SMS Sent:", sms.sid)

            last_garbage_count = current_count

        except Exception as e:
            print("❌ SMS sending failed:", e)
            return False

    else:
        print(f"ℹ️ No alert — increase too small (Need +{THRESHOLD_INCREASE}).")
        return False 
