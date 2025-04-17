import os
import pickle
import mediapipe as mp
import cv2
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

data = []
labels = []

class_names = ['A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J', 'K', 'L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','space']

for dir_ in class_names: #iterate over the list instead of file
    for img_path in os.listdir(os.path.join(DATA_DIR, dir_)):
        data_aux = []
        x_ = []
        y_ = []

        img = cv2.imread(os.path.join(DATA_DIR, dir_, img_path))
        if img is None:
            print(f"Warning: Could not read image {img_path} in directory {dir_}")
            continue # skip image if can't read

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))
            data.append(data_aux)
            labels.append(dir_)  # Use directory name as label

print("Dataset creation complete.")
print("Number of samples:", len(data))

#Ensure all have the same number of features!
feature_length = len(data[0]) if data else 0 # assumes the first sample has all the features

cleaned_data = []
cleaned_labels = []

for i in range(len(data)):
    if len(data[i]) == feature_length:
      cleaned_data.append(data[i])
      cleaned_labels.append(labels[i])
    else:
        print(f"Inconsistent feature length found for {labels[i]} at position {i}")

data = cleaned_data
labels = cleaned_labels

f = open('data.pickle', 'wb')
pickle.dump({'data': data, 'labels': labels}, f)
f.close()

print("Cleaned dataset saved to data.pickle")