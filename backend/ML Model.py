import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
df = pd.read_csv("dataset.csv")  # Assuming your file is an Excel file

# Preprocess the data
df = df.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)
df.fillna("Unknown", inplace=True)

# Split the data into symptoms and disease
X = df.iloc[:, 1:]  # Symptoms (all columns except the first)
y = df.iloc[:, 0]  # Disease (first column)

# Get all unique symptom names and map each symptom to a unique number
unique_symptoms = set(X.values.flatten()) - {"Unknown"}
symptom_dict = {symptom: i+1 for i, symptom in enumerate(unique_symptoms)}
symptom_dict["Unknown"] = 0
X = X.applymap(lambda symptom: symptom_dict.get(symptom, 0))

# Encode the disease labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Save the label encoder and symptom dictionary
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(symptom_dict, "symptom_dict.pkl")

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "diagnostic_model.pkl")

# Evaluate the model
y_pred = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("✅ Model training complete. Files saved: diagnostic_model.pkl, label_encoder.pkl, symptom_dict.pkl")
