from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

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

# Check if Flask is running
@app.route('/')
def home():
    return jsonify({"status": "AGRI-SENTINEL backend running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)