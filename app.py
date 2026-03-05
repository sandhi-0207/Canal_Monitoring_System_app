from flask import Flask, render_template, jsonify, request
import dashboard_data as dd   # shared data coming from realtime.py
import time
from realtime import start_webcam
import threading 
from flask import Response
import cv2
import requests
import numpy as np
app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    return jsonify(dd.dashboard_data)   # return real updated data

# --------- Live graph history ----------

@app.route("/history")
def history():
    return jsonify(dd.dashboard_data["history"])   # last 60 points


PHONE_IP = "100.120.39.242:8080"     # example: 192.168.1.10:8080
SHOT_URL = f"http://{PHONE_IP}/shot.jpg"

def gen_frames():
    while True:
        try:
            r = requests.get(SHOT_URL, timeout=3)
            img = np.frombuffer(r.content, dtype=np.uint8)
            frame = cv2.imdecode(img, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        except:
            continue

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/update_location", methods=["POST"])
def update_location():
    data = request.json
    dd.dashboard_data["location"] = f"{data['lat']}, {data['lon']}"
    return "OK", 200

def start_bg_detection():
    realtime.start_webcam()   # your existing function

if __name__ == "__main__":
    t = threading.Thread(target=start_webcam, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

