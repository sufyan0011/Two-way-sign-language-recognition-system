from flask import Flask, request, jsonify
import pickle
import cv2
import mediapipe as mp
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the frontend

# Load the trained model and label mappings
try:
    with open('model.p', 'rb') as f:
        model_dict = pickle.load(f)
    model = model_dict['model']
    label_to_index = model_dict['label_to_index']  # e.g. {'A': 0, 'B': 1, ..., 'SPACE': 26}
    index_to_label = {index: label for label, index in label_to_index.items()}
except Exception as e:
    print("Error loading model:", e)
    exit()

# Set up MediaPipe Hands for static image processing
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True,
                       max_num_hands=1,
                       min_detection_confidence=0.9,
                       min_tracking_confidence=0.7)

# ... [unchanged imports and setup above]

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    file_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({'error': 'Invalid image data'}), 400

    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        x_coords, y_coords = [], []
        data_aux = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                x_coords.append(lm.x)
                y_coords.append(lm.y)
            for lm in hand_landmarks.landmark:
                data_aux.append(lm.x - min(x_coords))
                data_aux.append(lm.y - min(y_coords))
        if data_aux:
            data_aux = np.array(data_aux)
            prediction = model.predict([data_aux])
            predicted_character = index_to_label.get(prediction[0], "Unknown")

            print(f"Predicted: {predicted_character}")  # Logging

            return jsonify({'prediction': predicted_character})

    return jsonify({'prediction': None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)