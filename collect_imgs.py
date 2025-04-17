import os
import cv2

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 27
dataset_size = 200 # Images to collect per class

cap = cv2.VideoCapture(0)

class_names = ['A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J', 'K', 'L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','space']
# class_names = []

for j in range(number_of_classes):
    class_name = class_names[j] #use indexed values

    class_dir = os.path.join(DATA_DIR, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print('Collecting data for class {}'.format(class_name))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't read frame. Check your camera.")
            exit()

        cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow('Detector', frame)
        if cv2.waitKey(25) == ord('q'):
            break

    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't read frame.")
            break #break inner while loop
        cv2.imshow('Detector', frame)
        cv2.waitKey(25)  # Give time to display and process the frame

        image_path = os.path.join(class_dir, '{}.jpg'.format(counter))
        cv2.imwrite(image_path, frame)

        counter += 1

cap.release()
cv2.destroyAllWindows()
print("Data collection complete.")