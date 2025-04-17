from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import pickle
import mediapipe as mp
from gtts import gTTS
import tempfile
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Load the gesture recognition model
try:
    with open('model.p', 'rb') as f:
        model_data = pickle.load(f)
    model = model_data['model']
    label_to_index = model_data['label_to_index']
    index_to_label = {v: k for k, v in label_to_index.items()}
except Exception as e:
    print(f"Error loading model: {str(e)}")
    exit()

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


def process_image(image):
    """Process image and extract hand landmarks"""
    try:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        if not results.multi_hand_landmarks:
            return None

        x_coords = []
        y_coords = []
        data_aux = []

        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                x_coords.append(landmark.x)
                y_coords.append(landmark.y)

            for landmark in hand_landmarks.landmark:
                data_aux.append(landmark.x - min(x_coords))
                data_aux.append(landmark.y - min(y_coords))

        return np.array(data_aux)
    except Exception as e:
        print(f"Image processing error: {str(e)}")
        return None


@app.route('/process-gesture', methods=['POST'])
def handle_gesture():
    """Endpoint for processing gesture images"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    try:
        file = request.files['image']
        img_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400

        processed_data = process_image(img)
        if processed_data is None:
            return jsonify({'prediction': None})

        prediction = model.predict([processed_data])[0]
        gesture = index_to_label.get(prediction, 'Unknown')

        print(f"{datetime.now()} - Predicted gesture: {gesture}")
        return jsonify({'prediction': gesture})

    except Exception as e:
        print(f"Gesture processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/text-to-speech', methods=['POST'])
def handle_text_to_speech():
    """Endpoint for converting text to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400

        tts = gTTS(text=text, lang='en')
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        tts.save(filepath)

        return send_file(
            filepath,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='sign_language_speech.mp3'
        )

    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)