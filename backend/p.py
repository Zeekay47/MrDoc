import  joblib
symptom_dict = joblib.load("symptom_dict.pkl")
print("Dictionary samples:")
for k, v in list(symptom_dict.items())[:30]:
    print(f"{k.ljust(20)} → {v}")