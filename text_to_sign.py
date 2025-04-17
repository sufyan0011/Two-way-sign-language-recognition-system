import os
import cv2
import random
import speech_recognition as sr  # For speech-to-text

# Define the labels dictionary (mapping characters to themselves)
labels_dict = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
    'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
    'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
    'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z', 'SPACE': 'SPACE'
}

DATA_DIR = './data'  # Your data directory


def convert_text_to_sign(text, data_dir, labels_dict):
    """
    Converts text input into a sequence of sign language representations.

    Args:
        text (str): The text to convert.
        data_dir (str): Path to the directory containing the sign images.
        labels_dict (dict): Dictionary mapping characters to folder names.

    Returns:
        list: A list of image paths corresponding to the sign language translation
              of the input text.
    """
    sign_representations = []
    for char in text.upper():
        if char == " ":
            char_label = "SPACE"
        else:
            char_label = char

        # Check if the character has a corresponding folder
        if char_label in labels_dict:
            char_dir = os.path.join(data_dir, labels_dict[char_label])

            if os.path.exists(char_dir) and os.path.isdir(char_dir):
                image_files = [f for f in os.listdir(char_dir) if f.endswith('.jpg') or f.endswith('.png')]
                if image_files:
                    image_path = os.path.join(char_dir, random.choice(image_files))  # Get a random image
                    sign_representations.append(image_path)
                else:
                    print(f"⚠ Warning: No images found for sign '{char_label}' in '{char_dir}'.")
                    sign_representations.append(None)
            else:
                print(f"⚠ Warning: No directory found for character '{char_label}'.")
                sign_representations.append(None)
        else:
            print(f"⚠ Warning: No mapping found for character '{char}'.")
            sign_representations.append(None)

    return sign_representations


if __name__ == '__main__':
    # Choose input method
    input_method = input("Enter 'text' for text input or 'voice' for voice input: ").lower()

    if input_method == 'text':
        text_input = input("Enter a sentence: ")
    elif input_method == 'voice':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Say something!")
            audio = r.listen(source)

        try:
            text_input = r.recognize_google(audio)
            print("✅ You said: " + text_input)
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            text_input = ""
        except sr.RequestError as e:
            print(f"❌ Could not request results from Google Speech Recognition service; {e}")
            text_input = ""
    else:
        print("⚠ Invalid input method. Using text input.")
        text_input = input("Enter a sentence: ")

    sign_output = convert_text_to_sign(text_input, DATA_DIR, labels_dict)

    if sign_output:
        for image_path in sign_output:
            if image_path:
                img = cv2.imread(image_path)
                if img is not None:
                    cv2.imshow("Sign", img)
                    cv2.waitKey(1000)  # Display image for 1 second
                    cv2.destroyAllWindows()
                else:
                    print(f"❌ ERROR: Could not read image from file {image_path}")

            else:
                print("⚠ No image to display for this character.")

    else:
        print(f"⚠ No sign language representation available for '{text_input}'.")

    cv2.destroyAllWindows()  # Always clean up OpenCV windows