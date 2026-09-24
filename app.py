from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
CORS(app)

FCM_SERVER_KEY = "your-firebase-server-key-here"

def send_push_notification(title, body, token):
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Store latest sensor data
sensor_data = {
    "moisture": 0,
    "motion": 0,
    "pump": "OFF",
    "timestamp": ""
}

# ESP32 sends sensor data here
@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data
    data = request.get_json()
    sensor_data.update(data)
    sensor_data["timestamp"] = str(datetime.datetime.now())
    print(f"Received: {data}")
    return jsonify({"status": "ok"})

# App reads sensor data from here
@app.route('/data', methods=['GET'])
def send_data():
    return jsonify(sensor_data)

# App controls pump from here
@app.route('/pump', methods=['POST'])
def control_pump():
    global sensor_data
    command = request.get_json()
    sensor_data["pump"] = command.get("state", "OFF")
    print(f"Pump command: {sensor_data['pump']}")
    return jsonify({"status": "ok", "pump": sensor_data["pump"]})

# Alert endpoint for push notifications
@app.route('/alert', methods=['POST'])
def send_alert():
    data = request.get_json()
    title = data.get('title', 'AGRI-SENTINEL Alert')
    body = data.get('body', 'Alert from your farm')
    token = data.get('token', '')
    result = send_push_notification(title, body, token)
    return jsonify(result)

# Check if Flask is running
@app.route('/')
def home():
    return jsonify({"status": "AGRI-SENTINEL backend running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)