import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

def train_and_evaluate():
    data_path = 'data/Crop_recommendation.csv'
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}")
        return
    
    print("Loading data...")
    df = pd.read_csv(data_path)
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Define models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000, random_state=42),
        'K-Nearest Neighbors': KNeighborsClassifier(),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Support Vector Machine': SVC(probability=True, random_state=42)
    }
    
    results = []
    best_model_name = ""
    best_f1 = 0
    best_pipeline = None
    
    print("\nTraining and evaluating models...\n")
    for name, model in models.items():
        # Create pipeline with scaling
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', model)
        ])
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='accuracy')
        
        # Fit and predict
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        results.append({
            'Model': name,
            'CV Accuracy': cv_scores.mean(),
            'Test Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1 Score': f1
        })
        
        print(f"{name}:")
        print(f"  CV Accuracy: {cv_scores.mean():.4f}")
        print(f"  Test Accuracy: {accuracy:.4f}")
        print(f"  F1 Score: {f1:.4f}\n")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipeline
            
    # Save results to dataframe
    results_df = pd.DataFrame(results)
    os.makedirs('models', exist_ok=True)
    results_df.to_csv('models/model_comparison.csv', index=False)
    
    print(f"Best Model based on F1 Score: {best_model_name}")
    
    # Save best pipeline (includes preprocessor and model)
    model_path = 'models/crop_model.pkl'
    joblib.dump(best_pipeline, model_path)
    print(f"Saved best pipeline to {model_path}")
    
    # Also save the reference ranges (quartiles) for the soil diagnosis module
    print("Calculating dataset reference ranges for soil diagnosis...")
    reference_ranges = {}
    for crop in df['label'].unique():
        crop_data = df[df['label'] == crop]
        reference_ranges[crop] = {
            'N': crop_data['N'].quantile([0.25, 0.75]).to_dict(),
            'P': crop_data['P'].quantile([0.25, 0.75]).to_dict(),
            'K': crop_data['K'].quantile([0.25, 0.75]).to_dict(),
            'ph': crop_data['ph'].quantile([0.25, 0.75]).to_dict()
        }
    joblib.dump(reference_ranges, 'models/soil_reference_ranges.pkl')
    print("Saved soil reference ranges to models/soil_reference_ranges.pkl")

if __name__ == '__main__':
    train_and_evaluate()
