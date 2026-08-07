import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os

def train_fertilizer_model():
    print("Loading Fertilizer dataset...")
    df = pd.read_csv('data/Fertilizer_Recommendation.csv')
    
    # Identify categorical columns
    categorical_cols = ['Soil Type', 'Crop Type']
    
    # Encode categorical columns
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le
        
    X = df.drop('Fertilizer Name', axis=1)
    y = df['Fertilizer Name']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    
    # Save the model and encoders
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/fertilizer_model.pkl')
    joblib.dump(encoders, 'models/fertilizer_encoders.pkl')
    print("Model and encoders saved to models/")

if __name__ == "__main__":
    train_fertilizer_model()
