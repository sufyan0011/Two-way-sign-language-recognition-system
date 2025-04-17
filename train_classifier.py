import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Loading data...")
try:
    data_dict = pickle.load(open('./data.pickle', 'rb'))
    data = data_dict['data']
    labels = data_dict['labels']
except FileNotFoundError:
    print("Error: data.pickle not found.  Run create_dataset.py first.")
    exit()

if not data:
    print("Error: No data loaded.  Check data.pickle content.")
    exit()

# Convert labels to numerical values based on class names
class_names = ['A', 'B', 'C', 'D', 'E', 'F','G', 'H', 'I', 'J', 'K', 'L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','space']

label_to_index = {label: index for index, label in enumerate(class_names)}
numerical_labels = [label_to_index[label] for label in labels]  # Convert labels to numerical values

data = np.asarray(data)
numerical_labels = np.asarray(numerical_labels) #use labels from here
print("Data shape:", data.shape)
print("Labels shape:", numerical_labels.shape)

# Split data
x_train, x_test, y_train, y_test = train_test_split(data, numerical_labels, test_size=0.2, shuffle=True, stratify=numerical_labels)

# Train the model
print("Training model...")
model = RandomForestClassifier()
model.fit(x_train, y_train)

# EvaluateA
y_predict = model.predict(x_test)
score = accuracy_score(y_test, y_predict)
print('Accuracy: {}%'.format(score * 100))

# Save the model
print("Saving model...")
f = open('model.p', 'wb')
pickle.dump({'model': model, 'label_to_index': label_to_index}, f)  # Include label mapping
f.close()

print("Model training complete and saved to model.p")