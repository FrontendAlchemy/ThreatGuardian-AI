import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the dataset
data = pd.read_csv('data.csv')

# Ensure that the dataset is loaded correctly
print(data.head())

# Prepare features (X) and labels (y)
X = data['email_text']
y = data['label'].apply(lambda x: 1 if x == 'phishing' else 0)  # 1 for phishing, 0 for legitimate

# Convert email text to TF-IDF features
vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)  # Added stop_words and lowercase
X_tfidf = vectorizer.fit_transform(X)

# Split into training and test data
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Train the model
model = LogisticRegression(max_iter=1000)  # Increase max_iter to ensure convergence
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred))  # Print detailed classification report

# Save the trained model and vectorizer
joblib.dump(model, 'phishing_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')

print("Model and vectorizer saved!")
