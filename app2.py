from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import base64

app = Flask(__name__)
CORS(app)

labels_dict = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
    'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
    'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
    'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z', 'space': 'space'
}

DATA_DIR = os.path.abspath('./data')


def get_image_base64(char_dir):
    """Get random image as base64 encoded string"""
    try:
        files = [f for f in os.listdir(char_dir)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not files:
            return None

        selected_file = random.choice(files)
        file_path = os.path.join(char_dir, selected_file)

        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        # Determine MIME type
        extension = os.path.splitext(selected_file)[1].lower()
        mime_type = f"image/{extension[1:]}" if extension != '.jpg' else 'image/jpeg'

        return f"data:{mime_type};base64,{encoded_string}"

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None


@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '').strip().upper()
    print(text)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    sign_output = []
    for char in text:
        try:
            if char == " ":
                char_label = "space"
            else:
                char_label = char

            if char_label not in labels_dict:
                sign_output.append(None)
                continue

            folder_name = labels_dict[char_label]
            char_dir = os.path.join(DATA_DIR, folder_name)

            if not os.path.exists(char_dir):
                sign_output.append(None)
                continue

            image_data = get_image_base64(char_dir)
            sign_output.append(image_data)

        except Exception as e:
            print(f"Error processing '{char}': {str(e)}")
            sign_output.append(None)

    return jsonify({"translated_signs": sign_output})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)