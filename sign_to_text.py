import pickle
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

# Load the trained model and label mapping
try:
    model_dict = pickle.load(open('./model.p', 'rb'))
    model = model_dict['model']
    label_to_index = model_dict['label_to_index']  # This now includes a "SPACE" label
    index_to_label = {index: label for label, index in label_to_index.items()}  # reverse mapping
except FileNotFoundError:
    print("Error: model.p not found. Run train_classifier.py first.")
    exit()

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Set up the hand detection in video mode.
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.9,
    min_tracking_confidence=0.7
)

recognized_sentence = ""
gesture_cooldown = 2  # seconds between accepted predictions
time_last_prediction = time.time()

# Prediction buffer to store a number of recent predictions
prediction_buffer = deque(maxlen=7)  # adjust buffer length as needed

while True:
    data_aux = []
    x_coords = []
    y_coords = []

    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read frame.")
        break

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on the frame.
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            # Collect coordinates for each landmark.
            for lm in hand_landmarks.landmark:
                x_coords.append(lm.x)
                y_coords.append(lm.y)

            # Build the feature vector normalized relative to the hand region.
            for lm in hand_landmarks.landmark:
                data_aux.append(lm.x - min(x_coords))
                data_aux.append(lm.y - min(y_coords))

        # Calculate bounding box around the hand.
        x1 = max(int(min(x_coords) * W) - 10, 0)
        y1 = max(int(min(y_coords) * H) - 10, 0)
        x2 = min(int(max(x_coords) * W) + 10, W)
        y2 = min(int(max(y_coords) * H) + 10, H)

        if data_aux:
            data_aux = np.asarray(data_aux)
            prediction = model.predict([data_aux])
            predicted_character_index = prediction[0]
            predicted_character = index_to_label[predicted_character_index]

            # Append the current prediction into our buffer.
            prediction_buffer.append(predicted_character)

            # If the last several predictions are identical, consider it a stable prediction.
            if len(set(prediction_buffer)) == 1:
                time_since_prediction = time.time() - time_last_prediction
                if time_since_prediction > gesture_cooldown:
                    if predicted_character == "SPACE":
                        # Insert a space when the space gesture is detected.
                        recognized_sentence += " "
                    else:
                        recognized_sentence += predicted_character
                    time_last_prediction = time.time()
                    prediction_buffer.clear()  # Reset the buffer after accepting the prediction

            # Draw bounding box and display predicted character.
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)
    else:
        # Clear the prediction buffer if no hand is detected.
        prediction_buffer.clear()

    # Display the accumulated sentence on the frame.
    cv2.putText(frame, recognized_sentence, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow('Detector', frame)
    key = cv2.waitKey(2)

    # If backspace is pressed (key value 8), delete the last character.
    if key == 8:
        recognized_sentence = recognized_sentence[:-1]

    if key == ord('c'):  # Clear the sentence
        recognized_sentence = ""
        prediction_buffer.clear()

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Final Recognized Sentence:", recognized_sentence)

