import cv2
import base64
import requests
import numpy as np
from sms_alert import send_alert_sms
import dashboard_data as dd
import time
# Roboflow Model Settings
API_KEY = "2bKZSj1s4HBuaVNNkgL1"
MODEL_ID = "canal-garbage-detection/7"
API_URL = f"https://serverless.roboflow.com/{MODEL_ID}?api_key={API_KEY}&confidence=0.4"


def infer(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    response = requests.post(
    API_URL,
    data=encoded_image,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    timeout=30
    )
    if response.status_code != 200:
      print("Roboflow error:", response.status_code, response.text[:200])
      return {"predictions": []}
    return response.json()


def draw_boxes(frame, predictions):
    for pred in predictions["predictions"]:
        x = int(pred["x"])
        y = int(pred["y"])
        w = int(pred["width"])
        h = int(pred["height"])
        class_name = pred["class"]

        x1 = int(x - w/2)
        y1 = int(y - h/2)
        x2 = int(x + w/2)
        y2 = int(y + h/2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, class_name, (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return frame


def start_webcam(): 
   
    PHONE_IP = "100.120.39.242"   # example: 192.168.137.25
    SHOT_URL = f"http://{PHONE_IP}:8080/shot.jpg"

    print("Starting real-time detection… Press 'q' to exit.")

    last_infer = 0
    cached_preds = {"predictions": []}

    while True:
        try:
           r = requests.get(SHOT_URL, timeout=10)
           img = np.frombuffer(r.content, dtype=np.uint8)
           frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
           if frame is None:
              continue
        except Exception as e:
              print("Camera fetch failed:", e)
              time.sleep(1)
              continue
        
        small = cv2.resize(frame, (320, 320))

        now = time.time()

        if now - last_infer > 1.5:   # run AI every 1 second
          cached_preds = infer(small)
          last_infer = now

          predictions = cached_preds
          count = len(predictions.get("predictions", []))

          # ---- STABLE COUNT (smoothing) ----
        if "count_buffer" not in globals():
          count_buffer = []

          count_buffer.append(count)
          count_buffer = count_buffer[-5:]              # last 5 frames
          stable_count = round(sum(count_buffer)/len(count_buffer))
          count = stable_count

        # Update dashboard with current count
          dd.update_dashboard(count, dd.dashboard_data["last_sms"])

        # SMS logic — only when count increases
        if count > dd.last_garbage_count:
            send_alert_sms(count)
            dd.update_dashboard(count, "SMS Sent")
            dd.last_garbage_count = count

        output = draw_boxes(small, predictions)
        cv2.imshow("Canal Garbage Detection - Real Time", output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_webcam()
