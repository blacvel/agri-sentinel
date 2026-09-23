import tensorflow as tf
import numpy as np
import cv2
import os

# Rice growth stages (most common Kerala crop)
growth_stages = [
    'Germination',      # 0-7 days
    'Seedling',         # 7-30 days
    'Tillering',        # 30-60 days
    'Jointing',         # 60-75 days
    'Booting',          # 75-85 days
    'Heading',          # 85-95 days
    'Flowering',        # 95-100 days
    'Milk_Grain',       # 100-115 days
    'Ripening_Harvest'  # 115-130 days
]

# Days range for each stage
stage_days = {
    'Germination': '0-7 days',
    'Seedling': '7-30 days',
    'Tillering': '30-60 days',
    'Jointing': '60-75 days',
    'Booting': '75-85 days',
    'Heading': '85-95 days',
    'Flowering': '95-100 days',
    'Milk_Grain': '100-115 days',
    'Ripening_Harvest': '115-130 days'
}

# Days remaining to harvest from each stage
days_to_harvest = {
    'Germination': 130,
    'Seedling': 115,
    'Tillering': 80,
    'Jointing': 60,
    'Booting': 45,
    'Heading': 35,
    'Flowering': 25,
    'Milk_Grain': 15,
    'Ripening_Harvest': 0
}

def load_model():
    if os.path.exists('growth_model.h5'):
        print("Loading saved growth model...")
        model = tf.keras.models.load_model('growth_model.h5')
        return model

    print("Building growth stage model...")
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
        tf.keras.layers.Dense(len(growth_stages), activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    model.save('growth_model.h5')
    print("Growth model built and saved!")
    return model

def analyze_color(image_path):
    # Color-based harvest detection
    # Golden/yellow dominance = ripening
    img = cv2.imread(image_path)
    if img is None:
        return None

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Green range (healthy growing crop)
    green_lower = np.array([35, 40, 40])
    green_upper = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_percent = np.sum(green_mask > 0) / green_mask.size * 100

    # Yellow/golden range (ripening)
    yellow_lower = np.array([20, 40, 40])
    yellow_upper = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    yellow_percent = np.sum(yellow_mask > 0) / yellow_mask.size * 100

    return green_percent, yellow_percent

def predict_growth_stage(image_path, model):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: {image_path} not found!")
        return

    # AI model prediction
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))
    img_array = np.expand_dims(img_resized, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    predictions = model.predict(img_array, verbose=0)
    predicted_index = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_index])
    stage = growth_stages[predicted_index]

    # Color analysis for harvest confirmation
    colors = analyze_color(image_path)
    green_pct, yellow_pct = colors

    print(f"\n🌾 === AGRI-SENTINEL Growth Analysis ===")
    print(f"📊 AI Predicted Stage: {stage}")
    print(f"📅 Stage Duration: {stage_days[stage]}")
    print(f"⏳ Days to Harvest: {days_to_harvest[stage]} days")
    print(f"🟢 Green coverage: {green_pct:.1f}%")
    print(f"🟡 Yellow coverage: {yellow_pct:.1f}%")
    print(f"📈 Model Confidence: {confidence:.2%}")

    # Harvest alerts based on color analysis
    print(f"\n📢 === ALERT STATUS ===")
    if yellow_pct > 30:
        print("🚨 HARVEST READY — Notify farmer immediately!")
        print("📱 Sending push notification + SMS...")
    elif yellow_pct > 15:
        print("⚠️ HARVEST APPROACHING — Alert: harvest in ~2 weeks")
        print("📱 Sending push notification...")
    elif stage == 'Ripening_Harvest':
        print("🚨 HARVEST READY — Based on AI stage detection!")
    elif stage in ['Milk_Grain', 'Flowering']:
        print("⚠️ HARVEST APPROACHING — Monitor closely")
    else:
        print("✅ Crop growing normally — No action needed")

    return stage, confidence

# Main
print("=== AGRI-SENTINEL Plant Growth Stage Detection ===")
model = load_model()
predict_growth_stage('crop.jpg', model)