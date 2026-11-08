"""AGRI-SENTINEL Flask backend."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, Response, send_from_directory

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IST = timezone(timedelta(hours=5, minutes=30))

sensor_data = {
    "moisture": 0, "motion": 0, "pump": "OFF",
    "animal": "none", "confidence": 0,
    "leaf_status": "Scanning...", "leaf_disease": "",
    "growth_stage": "Monitoring...", "days_to_harvest": 0,
    "timestamp": ""
}
pump_cmd = {"seq": 0, "command": "NONE"}  # what the farmer asked for
latest_frame = None

@app.route('/')
def home():
    return jsonify({"status": "AGRI-SENTINEL backend running!"})

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(sensor_data)

@app.route('/data', methods=['POST'])
def post_data():
    data = request.get_json(silent=True) or {}
    sensor_data.update(data)
    sensor_data["timestamp"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"status": "ok"})

# App -> backend: farmer taps ON / OFF
@app.route('/pump', methods=['POST'])
def set_pump():
    state = str((request.get_json(silent=True) or {}).get("state", "")).upper()
    if state in ("ON", "OFF", "AUTO"):
        pump_cmd["seq"] += 1
        pump_cmd["command"] = state
        return jsonify({"status": "ok", "command": state})
    return jsonify({"status": "bad state"}), 400

# ESP32 polls this. Plain text "seq,COMMAND"
@app.route('/command', methods=['GET'])
def get_command():
    return Response(f"{pump_cmd['seq']},{pump_cmd['command']}", mimetype='text/plain')

# Live preview
@app.route('/frame', methods=['POST'])
def upload_frame():
    global latest_frame
    latest_frame = request.get_data()
    return jsonify({"status": "ok"})

@app.route('/frame', methods=['GET'])
def get_frame():
    if latest_frame is None:
        return jsonify({"error": "no frame yet"}), 404
    return Response(latest_frame, mimetype='image/jpeg',
                    headers={"Cache-Control": "no-store"})

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

        