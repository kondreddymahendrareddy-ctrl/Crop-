# Intelligent Crop Recommendation, Soil Diagnosis and Fertilizer Guidance System

**Smart Soil Analysis • Crop Prediction • Fertilizer Guidance**

This project is a comprehensive B.Tech Data Science and Visualization application built using Machine Learning and Streamlit. It intelligently recommends crops based on soil metrics and real-time weather data, diagnoses soil health against dataset-derived standards, and provides fertilizer guidance.

## Features

1. **Top 3 Crop Recommendation**: ML-powered predictions with confidence scores.
2. **Real-time Weather Integration**: Fetches environmental data dynamically using Open-Meteo.
3. **Soil Diagnostic Engine**: Compares your soil to dataset interquartile references.
4. **Data Visualization**: Interactive NPK comparison charts using Plotly.
5. **Warning System & Improvement Advice**: Actionable feedback based on soil deficits or excesses.
6. **Fertilizer Guidance**: Heuristic recommendations to fix soil imbalances.
7. **User Authentication & History**: Secure login (bcrypt) and past analysis tracking.
8. **PDF Reports**: Downloadable professional analysis reports.
9. **Admin Dashboard**: System-wide analytics and model metrics.

## Architecture

- **Frontend**: Streamlit (Python)
- **Backend**: Python (Pandas, Scikit-learn, SQLite)
- **Machine Learning**: Random Forest Classifier (Trained on Kaggle Crop Dataset)
- **APIs**: Open-Meteo Geocoding and Weather Forecast
- **Database**: SQLite3
- **PDF Generation**: FPDF2

## Dataset Information

- **Crop Recommendation Dataset**: Sourced from Kaggle (`Crop_recommendation.csv`). Contains 2200 records, 22 crop classes, with NPK, temperature, humidity, pH, and rainfall features.
- **Fertilizer Recommendation Dataset**: *Note: This dataset was missing during initialization, so a heuristic fallback engine is used for Fertilizer Guidance instead of a dedicated ML model.*

## Folder Structure

```
intelligent_crop_system/
├── app.py                     # Main Streamlit application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── assets/                    # Static assets like Custom CSS
├── data/                      # Raw Kaggle datasets
├── database/                  # SQLite database (crop_system.db)
├── models/                    # Saved ML models and reference ranges (.pkl)
├── ml/                        # ML training and EDA scripts
│   ├── data_analysis.py
│   ├── inspect_data.py
│   └── train_crop_model.py
├── modules/                   # UI and Logic modules for Streamlit
│   ├── authentication.py
│   ├── dashboard.py
│   ├── crop_recommendation.py
│   ├── weather_service.py
│   ├── soil_diagnosis.py
│   ├── fertilizer_guidance.py
│   ├── history.py
│   ├── reports.py
│   ├── profile.py
│   └── admin.py
├── tests/                     # Test scripts (e.g., geolocator, weather API)
└── utils/                     # Helper utilities
    └── database.py
```

## Installation & Setup

1. **Clone/Download the repository**
2. **Set up Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Database Initialization**:
   The application initializes the SQLite database automatically. You can also run:
   ```bash
   python utils/database.py
   ```
5. **Train the Machine Learning Model**:
   This processes the dataset, trains the Random Forest model, and calculates soil reference ranges.
   ```bash
   python ml/train_crop_model.py
   ```
6. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## ML Algorithms Evaluated

The system evaluated the following algorithms for Crop Recommendation:
- Logistic Regression
- K-Nearest Neighbors
- Decision Tree
- Random Forest
- Support Vector Machine

**Random Forest** achieved the highest F1 Score (~99.5%) and was saved to the `models/` folder.

## Limitations

- The Weather API provides *daily* precipitation, whereas the dataset relies on *seasonal/annual* rainfall averages. A fallback manual input is provided in the UI for realistic predictions.
- Fertilizer guidance uses a rule-based heuristic approach due to the absence of the corresponding ML dataset.
- Dataset-derived soil reference ranges (interquartile ranges) are used for diagnosis, which may not completely substitute official localized agronomic standards.

## Future Enhancements
- Integrate a robust ML model for Fertilizer Recommendation when data is available.
- Connect to local IoT soil sensors for live NPK+pH data feeding.
- Add multi-language support for rural accessibility.
