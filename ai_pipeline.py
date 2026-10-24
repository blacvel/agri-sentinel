import cv2
import requests
import time
import numpy as np
import tensorflow as tf
from ultralytics import YOLO

RENDER_URL = "https://agri-sentinel-47x8.onrender.com"
WEBCAM_INDEX = 0

print("Loading AI models...")
yolo_model = YOLO('yolov8n.pt')
leaf_model = tf.keras.models.load_model('leaf_model.h5')
growth_model = tf.keras.models.load_model('growth_model.h5')
print("All models loaded!")

growth_stages = [
    'Germination', 'Seedling', 'Tillering', 'Jointing',
    'Booting', 'Heading', 'Flowering', 'Milk_Grain', 'Ripening_Harvest'
]
days_to_harvest = {
    'Germination': 130, 'Seedling': 115, 'Tillering': 80,
    'Jointing': 60, 'Booting': 45, 'Heading': 35,
    'Flowering': 25, 'Milk_Grain': 15, 'Ripening_Harvest': 0
}

def send_to_backend(data):
    try:
        requests.post(f"{RENDER_URL}/data", json=data, timeout=5)
    except:
        print("Backend unreachable — retrying next cycle")

def detect_animal(frame):
    results = yolo_model(frame)
    animals = ['bird','cat','dog','horse','cow','elephant','bear','zebra','giraffe']
    for result in results:
        for box in result.boxes:
            name = yolo_model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            if name in animals and conf > 0.5:
                return name, conf
    return None, 0

def analyze_leaf(frame):
    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    pred = leaf_model.predict(img, verbose=0)
    idx = np.argmax(pred[0])
    conf = float(pred[0][idx])
    diseases = ['Apple___Apple_scab','Apple___healthy','Tomato___Early_blight',
                'Tomato___Late_blight','Tomato___healthy','Potato___Early_blight',
                'Potato___healthy','Corn___Common_rust','Corn___healthy']
    disease = diseases[idx] if idx < len(diseases) else 'Unknown'
    healthy = 'healthy' in disease.lower()
    return disease, conf, healthy

def analyze_growth(frame):
    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    pred = growth_model.predict(img, verbose=0)
    idx = np.argmax(pred[0])
    stage = growth_stages[idx]
    days = days_to_harvest.get(stage, 0)
    return stage, days

def main():
    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print("Cannot open webcam!")
        return

    print(f"AGRI-SENTINEL AI Pipeline running...")
    print(f"Backend: {RENDER_URL}")
    print("Press Q to quit")

    last_leaf_scan = 0
    last_growth_scan = 0
    LEAF_INTERVAL = 7200
    GROWTH_INTERVAL = 86400

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        animal, conf = detect_animal(frame)
        if animal:
            print(f"ANIMAL DETECTED: {animal} ({conf:.0%})")
            send_to_backend({"motion": 1, "animal": animal, "confidence": round(conf, 2)})
        else:
            send_to_backend({"motion": 0, "animal": "none"})

        now = time.time()
        if now - last_leaf_scan > LEAF_INTERVAL:
            disease, conf, healthy = analyze_leaf(frame)
            status = "Healthy" if healthy else "Disease Detected"
            print(f"Leaf scan: {disease} ({conf:.0%})")
            send_to_backend({
                "leaf_status": status,
                "leaf_disease": disease,
                "leaf_confidence": round(conf, 2)
            })
            last_leaf_scan = now

        if now - last_growth_scan > GROWTH_INTERVAL:
            stage, days = analyze_growth(frame)
            print(f"Growth stage: {stage}, Days to harvest: {days}")
            send_to_backend({"growth_stage": stage, "days_to_harvest": days})
            last_growth_scan = now

        cv2.imshow('AGRI-SENTINEL', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()