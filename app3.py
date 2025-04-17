from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import base64
import speech_recognition as sr

app = Flask(__name__)
CORS(app)

labels_dict = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
    'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
    'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
    'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z', 'space': 'space'
}

DATA_DIR = os.path.abspath('./data')
recognizer = sr.Recognizer()
print(recognizer)

def get_image_base64(char_dir):
    try:
        files = [f for f in os.listdir(char_dir)
               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not files:
            return None
        selected_file = random.choice(files)
        with open(os.path.join(char_dir, selected_file), "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        extension = os.path.splitext(selected_file)[1].lower()
        mime_type = f"image/{extension[1:]}" if extension != '.jpg' else 'image/jpeg'
        return f"data:{mime_type};base64,{encoded_string}"
    except:
        return None

@app.route('/process-speeech', methods=['POST'])
def process_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip().upper()
        print(f"Received text: {text}")  # Log the received text

        if not text:
            return jsonify({"error": "No text provided"}), 400

        sign_output = []
        for char in text:
            if char == " ":
                char_label = "space"
            else:
                char_label = char

            if char_label in labels_dict:
                folder_name = labels_dict[char_label]
                char_dir = os.path.join(DATA_DIR, folder_name)
                image_data = get_image_base64(char_dir) if os.path.exists(char_dir) else None
                sign_output.append(image_data)
            else:
                sign_output.append(None)

        return jsonify({
            "transcribed_text": text,
            "translated_signs": sign_output
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)