from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

sensor_data = {
    "moisture": 0,
    "motion": 0,
    "pump": "OFF",
    "animal": "none",
    "confidence": 0,
    "leaf_status": "Scanning...",
    "leaf_disease": "Unknown",
    "growth_stage": "Monitoring...",
    "days_to_harvest": 0,
    "timestamp": ""
}

@app.route('/')
def home():
    return jsonify({"status": "AGRI-SENTINEL backend running!"})

@app.route('/data', methods=['GET'])
def send_data():
    return jsonify(sensor_data)

@app.route('/data', methods=['POST'])
def receive_data():
    global sensor_data
    data = request.get_json()
    sensor_data.update(data)
    sensor_data["timestamp"] = str(datetime.datetime.now())
    print(f"Received: {data}")
    return jsonify({"status": "ok"})

@app.route('/pump', methods=['POST'])
def control_pump():
    global sensor_data
    command = request.get_json()
    sensor_data["pump"] = command.get("state", "OFF")
    print(f"Pump: {sensor_data['pump']}")
    return jsonify({"status": "ok", "pump": sensor_data["pump"]})

@app.route('/pump', methods=['GET'])
def get_pump():
    return jsonify({"pump": sensor_data["pump"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)