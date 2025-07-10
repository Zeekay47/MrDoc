from models import Rule, Condition
from models import Symptom

def map_duration(duration_text):
    duration_mapping = {
        "Short": 1,
        "Medium": 2,
        "Long": 3
    }
    return duration_mapping.get(duration_text)

def map_severity(severity_text):
    severity_mapping = {
        "Mild": 1,
        "Moderate": 2,
        "Severe": 3
    }
    return severity_mapping.get(severity_text)



import numpy as np
import joblib
from models import Symptom  # Assuming you have this import


def evaluate_symptoms(symptom_ids):
    # 1. Load artifacts
    model = joblib.load("diagnostic_model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    symptom_dict = joblib.load("symptom_dict.pkl")

    # 2. Get symptom names from database and normalize
    db_symptoms = Symptom.query.filter(Symptom.id.in_(symptom_ids)).all()
    present_symptoms = [s.name.strip().lower().replace(' ', '_') for s in db_symptoms]

    # 3. Create vector using the EXACT encoding from training
    symptom_vector = np.zeros(len(symptom_dict))
    j=0
    for symptom_name in present_symptoms:
        if symptom_name in symptom_dict:
            code = symptom_dict[symptom_name]
            symptom_vector[j] = code  # Codes start at 1
        j=j+1

    # 4. Select first 17 features to match training data structure
    symptom_vector = symptom_vector[:17]

    # 5. Debug output
    print("\n=== DEBUG ===")
    print(f"Input Symptom IDs: {symptom_ids}")
    print(f"DB Symptoms: {[s.name for s in db_symptoms]}")
    print(f"Normalized Names: {present_symptoms}")
    print(f"Mapped Codes: {[symptom_dict.get(s) for s in present_symptoms]}")
    print(f"Final Vector (first 17): {symptom_vector}")
    print(f"Vector Sum: {sum(symptom_vector)}")

    # 6. Predict
    if sum(symptom_vector) > 0:
        prediction = model.predict([symptom_vector])
        return label_encoder.inverse_transform(prediction).tolist()
    return ["No matching symptoms found"]

