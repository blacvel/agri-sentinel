import tensorflow as tf
import numpy as np
import cv2
import urllib.request
import os

# Disease class names from PlantVillage dataset
class_names = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
    'Apple___healthy', 'Blueberry___healthy', 'Cherry___Powdery_mildew',
    'Cherry___healthy', 'Corn___Cercospora_leaf_spot',
    'Corn___Common_rust', 'Corn___Northern_Leaf_Blight', 'Corn___healthy',
    'Grape___Black_rot', 'Grape___Esca', 'Grape___Leaf_blight',
    'Grape___healthy', 'Orange___Haunglongbing',
    'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper___Bacterial_spot', 'Pepper___healthy',
    'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
    'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch',
    'Strawberry___healthy', 'Tomato___Bacterial_spot',
    'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

def load_model():
    # Check if model already exists
    if os.path.exists('leaf_model.h5'):
        print("Loading saved model...")
        model = tf.keras.models.load_model('leaf_model.h5')
        return model

    print("Building MobileNetV2 model...")
    # Use MobileNetV2 as base
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(len(class_names), activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.save('leaf_model.h5')
    print("Model built and saved!")
    return model

def predict_leaf(image_path, model):
    # Load and preprocess image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: {image_path} not found!")
        return

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    # Predict
    predictions = model.predict(img_array, verbose=0)
    predicted_index = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_index])
    predicted_class = class_names[predicted_index]

    # Parse result
    parts = predicted_class.split('___')
    plant = parts[0]
    condition = parts[1] if len(parts) > 1 else "Unknown"

    print(f"\n🌿 Plant: {plant}")
    print(f"📋 Condition: {condition}")
    print(f"📊 Confidence: {confidence:.2%}")

    if 'healthy' in condition.lower():
        print("✅ Leaf is HEALTHY")
    else:
        print("⚠️ DISEASE DETECTED — Alert farmer!")

    return predicted_class, confidence

# Main
print("=== AGRI-SENTINEL Leaf Disease Detection ===")
model = load_model()

# Test with leaf image
predict_leaf('leaf.jpg', model)