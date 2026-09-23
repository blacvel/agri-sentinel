from ultralytics import YOLO
import cv2

model = YOLO('yolov8n.pt')

img = cv2.imread('test.jpg')

if img is None:
    print("Error: test.jpg not found!")
    print("Please save an animal image as test.jpg in this folder")
else:
    print("Running animal detection...")
    results = model(img)

    detected = False
    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            print(f"Detected: {class_name} | Confidence: {confidence:.2f}")
            detected = True

    if not detected:
        print("Nothing detected in image")

    results[0].save(filename='detection_result.jpg')
    print("Result saved as detection_result.jpg")
