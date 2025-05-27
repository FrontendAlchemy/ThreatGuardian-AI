import joblib
import os

# Load model once
model_path = "phishing_model.pkl"
vectorizer_path = "vectorizer.pkl"

# Ensure the files exist and load them
if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
else:
    model = None
    vectorizer = None

def detect_phishing(text):
    if not model or not vectorizer:
        return "Error", "Model or vectorizer file not found."
    
    # Handle empty or invalid email content
    if not text or text.strip() == "":
        return "Error", "Email content is empty. Please provide valid input."
    
    X = vectorizer.transform([text])  # Transform the input email text
    prediction = model.predict(X)[0]

    if prediction == 1:
        return "Phishing", "⚠️ This email looks like a phishing attempt."
    else:
        return "Legitimate", "✅ This email appears safe and does not contain phishing patterns."
